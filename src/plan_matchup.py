"""Generate supported, provisional count-state plans for Misiorowski versus Rays."""
import json
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import pandas as pd

from download_statcast import ROOT, MLB, request, atomic_json, now
from matchup_model import (RUN, MIZ, LABELS, MEASURE, load_matchup, with_priors, predict)
from sequence import states_for, solve, continuation

DATE = pd.Timestamp('2026-10-23')
NAMES = {'FF': 'four-seam fastball', 'FC': 'cutter', 'CU': 'curveball', 'SL': 'slider'}


def main():
    data = pd.read_pickle(ROOT / 'data/processed/matchup/model_frame.pkl')
    manifest = json.loads((RUN / 'manifest.json').read_text())
    metrics = json.loads((RUN / 'metrics.json').read_text())
    if hashlib.sha256((ROOT / 'data/processed/matchup/model_frame.pkl').read_bytes()).hexdigest() != metrics['processed_frame_sha256']:
        raise ValueError('Prepared matchup frame changed after the forecast fit')
    if data.game_date.max() > pd.Timestamp(manifest['as_of']):
        raise ValueError('Future observations in forecast history')
    bundle = joblib.load(RUN / 'forecast.joblib')
    schedule = request(f'{MLB}/schedule', {'sportId': 1, 'teamId': 158,
        'date': '2026-10-23', 'hydrate': 'probablePitcher,team'}).json()
    atomic_json(ROOT / 'data/processed/matchup/schedule.json', schedule)
    games = [g for day in schedule['dates'] for g in day['games'] if g['gamePk'] == 849805]
    game = games[0]
    if game['teams']['home'].get('probablePitcher', {}).get('id') != int(MIZ):
        raise ValueError('Miz is not the listed Game 1 starter; refresh the matchup')
    lineup_source = f'{MLB}/game/{game["gamePk"]}/boxscore'
    box = request(lineup_source).json()
    confirmed = box.get('teams', {}).get('away', {}).get('battingOrder', [])
    recent = json.loads((ROOT / 'data/processed/matchup/rays_last_boxscore.json').read_text())
    last_team = next(t for t in recent['teams'].values() if t['team']['id'] == 139)
    order = confirmed if len(confirmed) == 9 else last_team['battingOrder']
    status = 'posted Game 1 batting order' if len(confirmed) == 9 else 'provisional: latest completed-game order, not confirmed Game 1 lineup'
    players = sorted(manifest['batters'], key=lambda p: order.index(p['id']) if p['id'] in order else 99)
    miz = data[data.pitcher.eq(MIZ) & data.game_date.ge('2026-01-01')].copy()
    recent_dates = sorted(miz.game_date.unique())[-4:]
    latest = miz[miz.game_date.isin(recent_dates)]
    configurations, query_rows = [], []
    for player in players:
        side = 'L' if player['bat_side'] in ('L', 'S') else 'R'
        counts = miz[miz.stand.eq(side)].groupby('pitch_type').size()
        recent_counts = latest.groupby('pitch_type').size()
        actions = [a for a, n in counts.items() if n >= 50 and recent_counts.get(a, 0) >= 5]
        if not actions:
            raise ValueError(f'No supported repertoire for {side}')
        counts_by_state = miz[miz.stand.eq(side)].groupby(['balls', 'strikes', 'pitch_type']).size()
        allowed = {}
        for b in range(4):
            for s in range(3):
                available = [a for a in actions if counts_by_state.get((b, s, a), 0) >= 5]
                allowed[(b, s)] = available or [max(actions, key=lambda a: counts_by_state.get((b, s, a), 0))]
        states = states_for(actions)
        configurations.append((player, side, actions, states, allowed, counts_by_state))
        for state in states:
            for action in actions:
                row = dict(pitcher=MIZ, batter=str(player['id']), pitch_type=action, p_throws='R',
                    stand=side, balls=state[0], strikes=state[1], previous_pitch_type=state[2],
                    previous_result=state[3], game_date=DATE, outcome=None, woba_value=np.nan)
                row.update({name: np.nan for name in MEASURE})
                query_rows.append(row)
    queries = pd.DataFrame(query_rows)
    enriched = with_priors(pd.concat([data, queries], ignore_index=True)).iloc[len(data):].reset_index(drop=True)
    probabilities = predict(bundle, enriched)
    pd.concat([enriched[bundle['features']], pd.DataFrame(probabilities, columns=['p_' + x for x in LABELS])], axis=1).to_csv(RUN / 'forecast_contexts.csv', index=False)
    rewards = {'out': 0.0}
    for name in ['single', 'extra_base', 'home_run', 'hbp']:
        rewards[name] = float(data.loc[data.outcome.eq(name), 'woba_value'].mean())
    rewards['walk'] = float(data.loc[data.events.eq('walk'), 'woba_value'].mean())
    if any(not np.isfinite(x) for x in rewards.values()):
        raise ValueError('Missing terminal outcome weights')
    pointer, cards, policy_rows = 0, [], []
    for player, side, actions, states, allowed, support in configurations:
        tables = {}
        for state in states:
            for action in actions:
                tables[(state, action)] = dict(zip(LABELS, map(float, probabilities[pointer])))
                pointer += 1
        policy, action_values = solve(states, actions, tables, rewards, allowed=allowed)
        root = (0, 0, 'START', 'START')
        opener = policy[root]
        after_strike = continuation(root, opener, 'strike')
        after_whiff = continuation(root, opener, 'whiff')
        after_ball = continuation(root, opener, 'ball')
        second = policy[after_strike]
        putaway_state = continuation(after_strike, second, 'strike')
        rankings = sorted(action_values[root], key=action_values[root].get)
        gap = action_values[root][rankings[1]] - action_values[root][rankings[0]] if len(rankings) > 1 else None
        card = {**player, 'stand_vs_miz': side, 'latest_lineup_position': order.index(player['id']) + 1 if player['id'] in order else None,
            'opener': opener, 'if_called_strike': policy[after_strike], 'if_whiff': policy[after_whiff],
            'if_ball': policy[after_ball], 'at_0_2_after_two_strikes': policy[putaway_state],
            'strike_branch_sequence': [opener, second, policy[putaway_state]],
            'root_alternative': rankings[1] if len(rankings) > 1 else None,
            'root_model_value_gap': gap, 'close_alternative_heuristic': gap is not None and gap < .015,
            'root_action_values': action_values[root], 'root_outcome_probabilities': tables[(root, opener)],
            'allowed_repertoire': actions}
        sample = data[data.batter.eq(str(player['id'])) & data.p_throws.eq('R')]
        card['batter_support_by_pitch'] = {a: int(sample.pitch_type.eq(a).sum()) for a in actions}
        cards.append(card)
        for state in states:
            for action, value in action_values[state].items():
                count_n = int(support.get((state[0], state[1], action), 0))
                policy_rows.append({'batter': player['id'], 'batter_name': player['name'], 'stand': side,
                    'balls': state[0], 'strikes': state[1], 'previous_pitch': state[2], 'previous_result': state[3],
                    'candidate_pitch': action, 'selected_pitch': policy[state], 'approximate_terminal_woba_plus_cost': value,
                    'miz_count_pitch_support': count_n, 'batter_pitch_vs_rhp_support': int(sample.pitch_type.eq(action).sum()),
                    **{'p_' + k: v for k, v in tables[(state, action)].items()}})
    pd.DataFrame(policy_rows).to_csv(RUN / 'count_policies.csv', index=False)
    physical = miz.groupby(['game_type', 'pitch_type'])[MEASURE].mean()
    physical.to_csv(RUN / 'miz_regular_vs_postseason_shape.csv')
    start = datetime.fromisoformat(game['gameDate'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/Chicago'))
    report = {'generated_at_utc': now(), 'game_pk': game['gamePk'], 'game_time_central': start.isoformat(),
        'venue': game['venue']['name'], 'as_of': manifest['as_of'], 'lineup_status': status,
        'lineup_source': lineup_source, 'scorer': bundle['scorer'], 'rewards': rewards,
        'pitch_cost': .0001, 'support_rule': '50 season pitches per handedness, 5 uses in last four outings, 5 pitches in count when available',
        'state_model': 'count plus previous pitch and result; terminal approximate wOBA, not game run expectancy',
        'card_scope': 'first-look neutral PA; update from the actual count and preceding outcome',
        'policy_validity': 'model-implied associations; optimality under these assumptions does not establish a causal game strategy',
        'cards': cards, 'evaluation': metrics}
    atomic_json(RUN / 'game_plan.json', report)
    overall = metrics['test']['overall']
    improvement = 100 * (overall['context_log_loss'] - overall['xgboost_log_loss']) / overall['context_log_loss']
    lines = ['# Miz vs. Rays — provisional Game 1 pitch plan', '',
        f"**{start.strftime('%A, %B %d, %Y at %I:%M %p')} Central, {game['venue']['name']}.**", '',
        f"Lineup status: {status}. The first nine rows use the latest completed Rays game's order, unless Game 1's order has been posted. Bench options follow. This is not an announced Game 1 batting order.", '',
        'The table is a count-dependent model scenario, not a fixed script. Start with the opener; choose the next pitch from the observed ball/strike result. The 0–2 column follows two strikes on the displayed strike branch. A foul with two strikes keeps the count and triggers a new decision from the updated previous-pitch state.', '',
        '| Batter | Side vs. Miz | Open 0–0 | If called strike, 0–1 | If ball, 1–0 | After two strikes, 0–2 | Opening alternative |',
        '|---|---|---|---|---|---|---|']
    for c in cards:
        label = c['name'] + (' (bench option)' if c['latest_lineup_position'] is None else '')
        lines.append(f"| {label} | {c['stand_vs_miz']} | {c['opener']} | {c['if_called_strike']} | {c['if_ball']} | {c['at_0_2_after_two_strikes']} | {c['root_alternative'] or '—'} |")
    lines += ['', '**Pitch key:** FF = four-seam fastball; FC = cutter; CU = curveball; SL = slider.', '',
        '## How much to trust this', '',
        f"The expanded dataset has {metrics['data']['unique_usable_rows']:,} unique usable pitches from 2025–26. All 30 player-season downloads reconcile with MLB physical pitch counts. Two rounds compared profile/context features with added prior-pitch sequence features, across two chronological development folds. The sequence gain was small; most improvement is not evidence of a special learned pitch order.", '',
        f"On the new postseason test, XGBoost transition log loss improved {improvement:.2f}% over the contextual baseline ({overall['xgboost_log_loss']:.5f} vs. {overall['context_log_loss']:.5f}); {overall['rows']:,} pitches in {overall['games']} games. Miz's own test is only 182 pitches in two games. Aggregate postseason results were publicly known before evaluation. The forecast model was then refit on all pregame observations; it has no independent new test.", '',
        'The planner minimizes approximate terminal wOBA plus a declared 0.0001 pitch-usage cost, with correct count changes and two-strike foul loops. It does not maximize whiffs alone. A walk, HBP, or damaging contact carries a terminal cost. These are weighted PA outcomes, not actual predicted runs or an expected score.', '',
        'Actions require at least 50 season pitches by Miz against the relevant side and at least five uses in his last four outings. Count-level options generally need five observations. Individual batter/pitch samples are reported in game_plan.json and count_policies.csv. Same-day and future measurements do not enter the history features.', '',
        'Observed pitch choice and execution are confounded. This model does not know intended location, catcher calls, hitter adaptation, or how Miz feels during warmups. It cannot establish that these branches outperform his actual strategy. Tiny model gaps are not meaningful proof of a preferred pitch. Use the alternative column to preserve options rather than repeating a deterministic script.', '',
        '## Files and updates', '',
        '- game_plan.json: all 14 batter cards, support, weights, alternatives, and probabilities.',
        '- count_policies.csv: every supported count/previous-pitch branch.',
        '- miz_regular_vs_postseason_shape.csv: observed velocity, spin, movement, and extension by pitch.',
        '- selection.json and metrics.json: development rounds and locked postseason evaluation.',
        '- forecast_contexts.csv and forecast.joblib: scored scenarios and saved forecast model.', '',
        f"Official game/lineup feed: [{lineup_source}]({lineup_source}). Roster and schedule snapshots are stored under data/processed/matchup/. Data cutoff is October 20; refresh availability and the batting order before game time."]
    (ROOT / 'MIZ_RAYS_GAME_PLAN.md').write_text('\n'.join(lines) + '\n')
    atomic_json(ROOT / 'data/processed/matchup/latest_plan.json', {'run': str(RUN), 'game_pk': game['gamePk']})
    print(json.dumps({'lineup_status': status, 'scorer': bundle['scorer'], 'batter_cards': len(cards),
        'report': str(ROOT / 'MIZ_RAYS_GAME_PLAN.md')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
