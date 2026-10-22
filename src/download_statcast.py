"""Download regular-season Statcast with checkpoints and MLB reconciliation."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import time
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
TEAM_ID, KYLE_HARRISON_ID = 158, 690986
MLB = 'https://statsapi.mlb.com/api/v1'
KEY = ('game_pk', 'at_bat_number', 'pitch_number')
AUTOMATIC = {'automatic_ball', 'automatic_strike'}
REQUIRED = set(KEY) | {'pitcher', 'game_date', 'game_type', 'pitch_type', 'description', 'delta_run_exp'}

def now():
    return datetime.now(timezone.utc).isoformat()

def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)

def request(url, params=None):
    for attempt in range(4):
        try:
            response = requests.get(url, params=params, timeout=(15, 120))
            response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)

def date_chunks(start, end, chunk_days):
    if chunk_days < 1 or start > end:
        raise ValueError('Invalid dates or chunk size')
    while start <= end:
        last = min(start + timedelta(days=chunk_days - 1), end)
        yield start, last
        start = last + timedelta(days=1)

def validate_rows(rows, pitcher, start, end):
    seen = {}
    for row in rows:
        if REQUIRED - set(row) or None in row or any(v is None for v in row.values()):
            raise ValueError('Malformed Statcast row')
        if row['pitcher'] != str(pitcher):
            raise ValueError('Savant ignored the pitcher filter')
        if row['game_type'] != 'R':
            raise ValueError('Non-regular-season row')
        if not start.isoformat() <= row['game_date'][:10] <= end.isoformat():
            raise ValueError('Out-of-range Savant date')
        key = tuple(row[k] for k in KEY)
        if any(not x for x in key):
            raise ValueError('Missing pitch key')
        if key in seen and row != seen[key]:
            raise ValueError('Conflicting duplicate pitch records')
        seen[key] = row
    return list(seen.values())

def fetch_window(pitcher, start, end, cache):
    params = {'all': 'true', 'type': 'details', 'player_type': 'pitcher',
        'pitchers_lookup[]': pitcher, 'game_date_gt': start.isoformat(),
        'game_date_lt': end.isoformat(), 'hfGT': 'R|'}
    path = cache / f'{pitcher}_{start}_{end}.json'
    if path.exists():
        saved = json.loads(path.read_text())
        digest = hashlib.sha256(json.dumps(saved['rows'], sort_keys=True).encode()).hexdigest()
        if saved['params'] != params or digest != saved['sha256']:
            raise ValueError(f'Invalid checkpoint: {path}')
        return validate_rows(saved['rows'], pitcher, start, end)
    response = request('https://baseballsavant.mlb.com/statcast_search/csv', params)
    reader = csv.DictReader(io.StringIO(response.content.decode('utf-8-sig')))
    if not reader.fieldnames or REQUIRED - set(reader.fieldnames):
        raise ValueError('Savant did not return a valid pitch CSV; not an empty success')
    rows = list(reader)
    if len(rows) >= 25000:
        if start == end:
            raise ValueError('Single-day response at truncation limit')
        middle = start + (end - start) // 2
        return fetch_window(pitcher, start, middle, cache) + fetch_window(pitcher, middle + timedelta(days=1), end, cache)
    rows = validate_rows(rows, pitcher, start, end)
    atomic_json(path, {'params': params, 'fetched_at_utc': now(), 'rows': rows,
        'sha256': hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()})
    return rows

def write_csv(path, rows):
    columns = list(dict.fromkeys(k for row in rows for k in row)) or sorted(REQUIRED)
    temp = path.with_suffix('.csv.tmp')
    with temp.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)

def get_roster(season, output):
    saved = output / f'pitcher_roster_{season}.csv'
    if saved.exists():
        with saved.open(encoding='utf-8-sig', newline='') as handle:
            roster = {int(r['player_id']): r for r in csv.DictReader(handle)}
    else:
        roster = {}
    response = request(f'{MLB}/stats', {'stats': 'season', 'group': 'pitching',
        'season': season, 'teamId': TEAM_ID, 'playerPool': 'ALL', 'limit': 1000})
    blocks = response.json().get('stats', [])
    if not blocks or any(len(b.get('splits', [])) < b.get('totalSplits', 0) for b in blocks):
        raise ValueError('Missing or truncated team participant list')
    participants = set()
    for block in blocks:
        for split in block.get('splits', []):
            person = split['player']
            participants.add(int(person['id']))
            roster[int(person['id'])] = {'player_id': person['id'], 'player_name': person['fullName'],
                'position': 'Pitching appearance', 'status': 'Verified season participant',
                'team_id': TEAM_ID, 'season': season}
    roster.setdefault(KYLE_HARRISON_ID, {'player_id': KYLE_HARRISON_ID, 'player_name': 'Kyle Harrison',
        'position': 'P', 'status': 'Comparison pitcher', 'team_id': '', 'season': season})
    return list(roster.values()), participants, response.url

def appearances(pitcher, season, start, end):
    response = request(f'{MLB}/people/{pitcher}/stats', {'stats': 'gameLog', 'group': 'pitching',
        'season': season, 'gameType': 'R'})
    blocks = response.json().get('stats', [])
    if not blocks:
        raise ValueError(f'No pitching-log response for {pitcher}')
    logs = [s for b in blocks for s in b.get('splits', [])
        if start.isoformat() <= s['date'] <= end.isoformat() and s.get('sport', {}).get('id') == 1]
    return logs, response.url

def reconcile(rows, logs):
    expected = {str(s['game']['gamePk']): s for s in logs}
    all_counts = Counter(r['game_pk'] for r in rows)
    physical = Counter(r['game_pk'] for r in rows if r['description'] not in AUTOMATIC)
    return {'expected_games': len(expected), 'saved_games': len(all_counts),
        'missing_games': sorted(set(expected) - set(all_counts)),
        'unexpected_games': sorted(set(all_counts) - set(expected)),
        'pitch_count_differences': [{'game_pk': k, 'date': s['date'], 'saved_rows': physical[k],
            'mlb_pitches': s['stat']['numberOfPitches']} for k, s in expected.items()
            if physical[k] != s['stat']['numberOfPitches']],
        'automatic_event_rows': sum(r['description'] in AUTOMATIC for r in rows),
        'physical_pitch_rows': sum(physical.values()),
        'mlb_pitch_total': sum(s['stat']['numberOfPitches'] for s in logs)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--season', type=int, default=date.today().year)
    parser.add_argument('--start', type=date.fromisoformat)
    parser.add_argument('--end', type=date.fromisoformat, default=date.today() - timedelta(days=1))
    parser.add_argument('--chunk-days', type=int, default=62)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/raw')
    args = parser.parse_args()
    start = args.start or date(args.season, 3, 1)
    if start > args.end or start.year != args.season or args.end.year != args.season or args.chunk_days < 1:
        parser.error('Use valid dates within --season and a positive chunk size')
    args.output.mkdir(parents=True, exist_ok=True)
    roster, participants, roster_source = get_roster(args.season, args.output)
    audit_path = ROOT / 'data/processed' / f'completeness_audit_{args.season}.json'
    metadata_path = args.output / f'download_metadata_{args.season}.json'
    requested = {'season': args.season, 'start': start.isoformat(), 'end': args.end.isoformat(),
        'team_id': TEAM_ID, 'game_type': 'R', 'comparison_pitcher_id': KYLE_HARRISON_ID}
    audit = {'requested': requested, 'audited_at_utc': now(), 'status': 'in_progress',
        'team_participant_source': roster_source, 'team_season_participant_ids': sorted(participants),
        'pitch_count_convention': 'Physical pitch rows excluding automatic_ball and automatic_strike', 'pitchers': []}
    atomic_json(audit_path, audit)
    atomic_json(metadata_path, {**requested, 'status': 'in_progress', 'started_at_utc': now()})
    write_csv(args.output / f'pitcher_roster_{args.season}.csv', roster)
    team_games, team_keys = set(), set()
    team_physical, expected_team_physical, team_automatic = 0, 0, 0
    for player in roster:
        pitcher = int(player['player_id'])
        print(f"Downloading {player['player_name']} ({pitcher})", flush=True)
        rows = []
        for begin, end in date_chunks(start, args.end, args.chunk_days):
            rows.extend(fetch_window(pitcher, begin, end, args.output / '.downloads'))
        rows = validate_rows(rows, pitcher, start, args.end)
        logs, source = appearances(pitcher, args.season, start, args.end)
        check = reconcile(rows, logs)
        for difference in check['pitch_count_differences']:
            game = difference['game_pk']
            day = date.fromisoformat(difference['date'])
            replacement = [r for r in fetch_window(pitcher, day, day, args.output / '.downloads') if r['game_pk'] == game]
            if replacement:
                rows = [r for r in rows if r['game_pk'] != game] + replacement
        check = reconcile(rows, logs)
        expected_team_physical += sum(s['stat']['numberOfPitches'] for s in logs if s['team']['id'] == TEAM_ID)
        for row in rows:
            pitching_team = row['home_team'] if row['inning_topbot'] == 'Top' else row['away_team']
            if pitching_team == 'MIL':
                key = tuple(row[k] for k in KEY)
                if key in team_keys:
                    raise ValueError('Duplicate team pitch key across pitcher files')
                team_keys.add(key)
                team_games.add(row['game_pk'])
                team_physical += row['description'] not in AUTOMATIC
                team_automatic += row['description'] in AUTOMATIC
        for row in rows:
            row.update(study_pitcher_id=str(pitcher), study_pitcher_name=player['player_name'],
                study_group='brewers' if pitcher in participants else 'comparison',
                study_comparison='kyle_harrison' if pitcher == KYLE_HARRISON_ID else '')
        rows.sort(key=lambda r: (r['game_date'], int(r['game_pk']), int(r['at_bat_number']), int(r['pitch_number'])))
        path = args.output / f'pitcher_{pitcher}_{args.season}.csv'
        write_csv(path, rows)
        audit['pitchers'].append({'player_id': str(pitcher), 'name': player['player_name'],
            'file_exists': True, 'rows': len(rows), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'game_types': dict(Counter(r['game_type'] for r in rows)),
            'first': min((r['game_date'] for r in rows), default=None),
            'last': max((r['game_date'] for r in rows), default=None),
            'regular_season_reconciliation': {**check, 'source_url': source},
            'milwaukee_games': sum(s['team']['id'] == TEAM_ID for s in logs)})
        atomic_json(audit_path, audit)
        print(f"  saved {len(rows)} rows; missing {len(check['missing_games'])}; discrepancies {len(check['pitch_count_differences'])}", flush=True)
    missing = sum(len(r['regular_season_reconciliation']['missing_games']) for r in audit['pitchers'])
    differences = sum(len(r['regular_season_reconciliation']['pitch_count_differences']) for r in audit['pitchers'])
    unexpected = sum(len(r['regular_season_reconciliation']['unexpected_games']) for r in audit['pitchers'])
    schedule = request(f'{MLB}/schedule', {'sportId': 1, 'teamId': TEAM_ID,
        'startDate': start.isoformat(), 'endDate': args.end.isoformat(), 'gameType': 'R'})
    expected_games = {str(g['gamePk']) for day in schedule.json().get('dates', [])
        for g in day['games'] if g['status']['abstractGameState'] == 'Final'}
    audit['team_schedule_reconciliation'] = {'source_url': schedule.url,
        'expected_games': len(expected_games), 'saved_games': len(team_games),
        'missing_games': sorted(expected_games - team_games), 'unexpected_games': sorted(team_games - expected_games),
        'physical_pitch_rows': team_physical, 'expected_physical_pitches': expected_team_physical,
        'automatic_event_rows': team_automatic}
    audit['summary'] = {'files': len(roster), 'rows': sum(r['rows'] for r in audit['pitchers']),
        'missing_pitcher_games': missing, 'pitch_count_discrepancies': differences,
        'unexpected_pitcher_games': unexpected, 'milwaukee_appearances': sum(r['milwaukee_games'] for r in audit['pitchers']),
        'team_participants': len(participants)}
    schedule_clean = team_games == expected_games and team_physical == expected_team_physical
    audit['status'] = 'complete' if missing == differences == unexpected == 0 and schedule_clean else 'incomplete'
    audit['audited_at_utc'] = now()
    atomic_json(audit_path, audit)
    atomic_json(metadata_path, {**requested, 'status': audit['status'], 'completed_at_utc': now(), 'audit': str(audit_path)})
    print(json.dumps(audit['summary'], indent=2), flush=True)
    if audit['status'] != 'complete':
        raise SystemExit('Coverage incomplete; see audit discrepancies')

if __name__ == '__main__':
    main()
