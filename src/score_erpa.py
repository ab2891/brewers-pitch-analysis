"""Score all counts, base/out states, and reachable histories in run units."""
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

from download_statcast import ROOT, atomic_json, now
from matchup_model import RUN, LABELS, MIZ
from run_value import (COUNTS, fit_run_weights, run_values, relative_value,
                       reachable_states, base_label)

RUN = Path(os.environ.get('MATCHUP_RUN', RUN)).resolve()
OUT = RUN / 'run_values'
STATE = ['batter', 'balls', 'strikes', 'previous_pitch', 'previous_result']
P = ['p_' + label for label in LABELS]


def history_weights(frame, candidates):
    miz = frame[frame.pitcher.eq(MIZ) & frame.game_date.ge('2026-01-01')]
    n = miz.groupby(['stand', 'balls', 'strikes', 'previous_pitch_type', 'previous_result']).size()
    weights = {}
    for _, group in candidates.groupby(['batter', 'balls', 'strikes']):
        contexts = group[STATE + ['stand']].drop_duplicates()
        values = []
        for row in contexts.itertuples():
            key = (row.stand, row.balls, row.strikes, row.previous_pitch, row.previous_result)
            values.append(float(n.get(key, 0)))
        if sum(values) == 0:
            values = [1.] * len(contexts)
        total = sum(values)
        for row, value in zip(contexts.itertuples(), values):
            weights[(row.batter, row.balls, row.strikes, row.previous_pitch, row.previous_result)] = value / total
    return weights


def candidate_mix(group):
    # Counts already come from 2026 Miz pitches against this handedness/count.
    values = group.miz_count_pitch_support.to_numpy(dtype=float)
    if values.sum() == 0:
        values = np.ones(len(group))
    return values / values.sum()


def diagnostic(data):
    """Known holdout reused for a diagnostic, never new validation or tuning."""
    predictions = pd.read_csv(RUN / 'postseason_predictions.csv', dtype={'game_pk': str, 'pitcher': str, 'batter': str})
    source = data[data.game_date.ge('2026-10-01')].copy()
    from run_value import add_base_outs
    source = add_base_outs(source)
    mapping = fit_run_weights(data[data.game_date.lt('2026-10-01')])
    values = mapping.pivot(index=['balls','strikes','outs','base_mask'], columns='outcome', values='expected_batting_run_delta').reindex(columns=LABELS)
    expected = values.reindex(pd.MultiIndex.from_frame(source[['balls','strikes','outs','base_mask']])).to_numpy()
    if not np.array_equal(predictions.game_pk.astype(str).to_numpy(), source.game_pk.astype(str).to_numpy()):
        raise ValueError('Diagnostic predictions do not align with saved source rows')
    projected = run_values(predictions[P].to_numpy(), expected)
    y = pd.to_numeric(source.delta_run_exp, errors='coerce').to_numpy()
    finite = np.isfinite(y)
    mean = pd.to_numeric(data.loc[data.game_date.lt('2026-10-01'), 'delta_run_exp'], errors='coerce').mean()
    return {'status': 'diagnostic on previously scored test; not a new independent test',
        'rows': int(finite.sum()), 'projected_run_value_rmse': float(np.sqrt(mean_squared_error(y[finite], projected[finite]))),
        'training_mean_rmse': float(np.sqrt(mean_squared_error(y[finite], np.full(finite.sum(), mean))))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frame_path = RUN / 'model_frame.pkl'
    if not frame_path.exists():
        frame_path = ROOT / 'data/processed/matchup/model_frame.pkl'
    data = pd.read_pickle(frame_path)
    report = json.loads((RUN / 'metrics.json').read_text())
    digest = hashlib.sha256(frame_path.read_bytes()).hexdigest()
    if digest != report['processed_frame_sha256']:
        raise ValueError('Forecast source changed')
    policies = pd.read_csv(RUN / 'count_policies.csv', dtype={'batter': str})
    usable = []
    for _, group in policies.groupby('batter', sort=False):
        reachable = reachable_states(group)
        mask = [tuple(x) in reachable for x in group[['balls','strikes','previous_pitch','previous_result']].itertuples(index=False, name=None)]
        usable.append(group.loc[mask].copy())
    candidates = pd.concat(usable, ignore_index=True)
    weights = fit_run_weights(data)
    weights.to_csv(OUT / 'run_value_weights.csv', index=False)
    weight_table = weights.pivot(index=['balls','strikes','outs','base_mask'], columns='outcome', values='expected_batting_run_delta').reindex(columns=LABELS)
    support_table = weights.pivot(index=['balls','strikes','outs','base_mask'], columns='outcome', values='full_cell_n').reindex(columns=LABELS)
    conditional = {'outs', 'base_mask'}.issubset(candidates.columns)
    # History frequencies are a fixed reference; do not count the 24 replicated forecasts as observations.
    history_mix = history_weights(data, candidates.drop_duplicates(STATE + ['candidate_pitch']))
    miz_history_n = data[data.pitcher.eq(MIZ) & data.game_date.ge('2026-01-01')].groupby(
        ['stand','balls','strikes','previous_pitch_type','previous_result']).size()
    counts_summary, averaged_candidates, history_candidates, history_summary = [], [], [], []
    grouping = ['batter','balls','strikes'] + (['outs','base_mask'] if conditional else [])
    for identity_key, group in candidates.groupby(grouping, sort=False):
        person, b, s = identity_key[:3]
        group = group.copy()
        group['history_weight'] = [history_mix[tuple(x)] for x in group[STATE].itertuples(index=False, name=None)]
        # Each state's candidate set is identical at a fixed handedness/count.
        marginal = group.groupby('candidate_pitch', sort=False)[P].apply(lambda x: (x.to_numpy() * group.loc[x.index, 'history_weight'].to_numpy()[:,None]).sum(axis=0))
        actions = marginal.index.tolist()
        probability = np.stack(marginal.to_list())
        supports = group.groupby('candidate_pitch', sort=False).miz_count_pitch_support.first().reindex(actions)
        mix = supports.to_numpy(dtype=float); mix = mix / mix.sum() if mix.sum() else np.ones(len(actions))/len(actions)
        for outs in ([identity_key[3]] if conditional else range(3)):
            for bases in ([identity_key[4]] if conditional else range(8)):
                rv_weights = weight_table.loc[(b,s,outs,bases)].to_numpy(dtype=float)
                cell_n = support_table.loc[(b,s,outs,bases)].to_numpy(dtype=float)
                erv = run_values(probability, rv_weights)
                reference, erpa = relative_value(erv, mix)
                ranking = np.argsort(erv, kind='stable')
                best, second = int(ranking[0]), int(ranking[1]) if len(ranking)>1 else None
                identity = dict(batter=person, batter_name=group.batter_name.iloc[0], stand=group.stand.iloc[0],
                    balls=int(b), strikes=int(s), outs=outs, base_mask=bases, bases=base_label(bases))
                baseline_p = mix @ probability
                for i, action in enumerate(actions):
                    sparse = float(probability[i] @ (cell_n < 20))
                    averaged_candidates.append({**identity, 'candidate_pitch': action, 'expected_batting_run_delta': erv[i],
                        'expected_pitching_run_value': -erv[i], 'usual_mix_batting_run_delta': reference,
                        'erpa_runs_per_pitch': erpa[i], 'erpa_runs_per_100': 100*erpa[i],
                        'regret_vs_best_runs': erv[i]-erv[best], 'miz_count_pitch_support': int(supports.iloc[i]),
                        'reference_mix_weight': mix[i], 'sparse_mapping_probability': sparse,
                        **dict(zip(P, map(float, probability[i]))),
                        **{'erpa_from_'+label: float((baseline_p[j]-probability[i,j])*rv_weights[j]) for j,label in enumerate(LABELS)}})
                counts_summary.append({**identity, 'best_pitch': actions[best],
                    'runner_up': actions[second] if second is not None else None,
                    'best_expected_batting_run_delta': erv[best], 'usual_mix_batting_run_delta': reference,
                    'best_erpa_runs_per_pitch': erpa[best], 'best_erpa_runs_per_100':100*erpa[best],
                    'advantage_vs_runner_up_runs': erv[second]-erv[best] if second is not None else None,
                    'candidate_count': len(actions), 'sparse_mapping_probability': float(probability[best] @ (cell_n<20)),
                    'history_mode': 'average over reachable prior histories using Miz count/hand frequencies'})
                for history, subgroup in group.groupby(['previous_pitch','previous_result'], sort=False):
                    sub_p = subgroup[P].to_numpy(dtype=float)
                    sub_erv = run_values(sub_p, rv_weights)
                    sub_ref, sub_erpa = relative_value(sub_erv, candidate_mix(subgroup))
                    order = np.argsort(sub_erv, kind='stable'); first=int(order[0]); next_i=int(order[1]) if len(order)>1 else None
                    history_n = int(miz_history_n.get((identity['stand'],b,s,history[0],history[1]),0))
                    h_identity={**identity, 'previous_pitch':history[0], 'previous_result':history[1],
                        'miz_history_support':history_n}
                    history_summary.append({**h_identity, 'best_pitch':subgroup.candidate_pitch.iloc[first],
                        'runner_up':subgroup.candidate_pitch.iloc[next_i] if next_i is not None else None,
                        'best_expected_batting_run_delta':sub_erv[first], 'usual_mix_batting_run_delta':sub_ref,
                        'best_erpa_runs_per_pitch':sub_erpa[first], 'best_erpa_runs_per_100':100*sub_erpa[first],
                        'advantage_vs_runner_up_runs':sub_erv[next_i]-sub_erv[first] if next_i is not None else None,
                        'candidate_count':len(subgroup), 'sparse_mapping_probability':float(sub_p[first] @ (cell_n<20))})
                    for i,row in enumerate(subgroup.itertuples()):
                        history_candidates.append({**h_identity, 'candidate_pitch':row.candidate_pitch,
                            'expected_batting_run_delta':sub_erv[i], 'expected_pitching_run_value':-sub_erv[i],
                            'usual_mix_batting_run_delta':sub_ref, 'erpa_runs_per_pitch':sub_erpa[i],
                            'erpa_runs_per_100':100*sub_erpa[i], 'regret_vs_best_runs':sub_erv[i]-sub_erv[first],
                            'miz_count_pitch_support':int(row.miz_count_pitch_support),
                            **dict(zip(P, map(float, sub_p[i])))})
        if not conditional or tuple(identity_key[3:]) == (2, 7):
            print(f'{person} {b}-{s}: scored all 24 base/out states', flush=True)
    summary=pd.DataFrame(counts_summary); average=pd.DataFrame(averaged_candidates)
    details=pd.DataFrame(history_candidates); detail_summary=pd.DataFrame(history_summary)
    identity_columns=['batter','balls','strikes','outs','base_mask']
    for table, group_columns in [(average,identity_columns),(details,identity_columns+['previous_pitch','previous_result'])]:
        table['rank']=table.groupby(group_columns).expected_batting_run_delta.rank(method='first').astype(int)
        table.sort_values(group_columns+['rank'],inplace=True)
    summary.to_csv(OUT/'count_summary.csv',index=False)
    average.to_csv(OUT/'count_candidates.csv.gz',index=False,compression='gzip')
    details.to_csv(OUT/'history_candidates.csv.gz',index=False,compression='gzip')
    detail_summary.to_csv(OUT/'history_summary.csv.gz',index=False,compression='gzip')
    if len(summary)!=14*12*24 or not np.isfinite(average.expected_batting_run_delta).all():
        raise ValueError('Incomplete situation coverage')
    diagnostic_result=diagnostic(data)
    result={'generated_at_utc':now(),'score':'ERPA: Expected Runs Prevented Above supported usual mix (project definition)',
        'formula':'ERPA(s,a) = sum_k mix(k|hand,count)*ERV(s,k) - ERV(s,a)',
        'erv_formula':'ERV(s,a) = sum_outcome P(outcome|batter,count,outs,runners,prior pitch,candidate)*E[delta_run_exp|count,outs,bases,outcome]' if conditional else 'Original model: probabilities omit runners/outs',
        'units':'runs per next pitch; 100x is runs per 100 equivalent pitches',
        'reference':'2026 Miz pitch frequencies by handedness/count, restricted and normalized to supported candidate set; same mix for each prior history',
        'counts':len(COUNTS),'base_out_states':24,'batters':14,'count_situations':len(summary),
        'history_situations':len(detail_summary),'history_candidate_comparisons':len(details),
        'run_weight_rows':len(weights),'smoothing_pseudocount':20,'diagnostic':diagnostic_result,
        'probabilities_condition_on_base_outs':conditional,
        'model_note':'Runners and outs are pre-pitch probability inputs and run-impact inputs.' if conditional else 'Frozen transition probabilities do not condition on bases/outs; only run-impact weights change with base/out state.',
        'scope':'Immediate next-pitch value with historical RE continuation; all legal previous histories over the eligible repertoire, including rare past choices. Next actions remain support-pruned.',
        'limits':'Outcome-associated observational estimates; sparse cells pooled; model probability error and action selection confounding remain. Not proven causal runs saved.',
        'source_frame_sha256':digest}
    atomic_json(OUT/'metrics.json',result)
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    main()
