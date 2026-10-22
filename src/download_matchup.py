"""Acquire opponent batter and pitcher histories without changing the team dataset."""
import csv
import hashlib
import io
import json
from collections import Counter
from datetime import date
from pathlib import Path

from download_statcast import ROOT, MLB, AUTOMATIC, KEY, atomic_json, now, request

OUT = ROOT / 'data/processed/matchup'
RAW = ROOT / 'data/raw/matchup'
TYPES = {'R', 'F', 'D', 'L', 'W'}
AS_OF = '2026-10-20'
MIZ = 694819


def fetch(role, person, season):
    start, end = f'{season}-03-01', f'{season}-10-20'
    params = {'all': 'true', 'type': 'details', 'player_type': role,
        ('pitchers_lookup[]' if role == 'pitcher' else 'batters_lookup[]'): person,
        'game_date_gt': start, 'game_date_lt': end, 'hfGT': 'R|F|D|L|W|'}
    path = RAW / f'{role}_{person}_{season}.json'
    if path.exists():
        d = json.loads(path.read_text())
        digest = hashlib.sha256(json.dumps(d['rows'], sort_keys=True).encode()).hexdigest()
        if d['params'] != params or d['sha256'] != digest:
            raise ValueError(f'Invalid matchup checkpoint {path}')
        rows = d['rows']
    else:
        response = request('https://baseballsavant.mlb.com/statcast_search/csv', params)
        reader = csv.DictReader(io.StringIO(response.content.decode('utf-8-sig')))
        required = set(KEY) | {'pitcher', 'batter', 'description', 'pitch_type', 'woba_value'}
        if not reader.fieldnames or required - set(reader.fieldnames):
            raise ValueError('Invalid matchup CSV schema')
        rows = list(reader)
        if len(rows) >= 25000:
            raise ValueError('Matchup query reached truncation limit')
        for r in rows:
            if None in r or any(v is None for v in r.values()):
                raise ValueError('Malformed matchup row')
            if r[role] != str(person) or not start <= r['game_date'][:10] <= end or r['game_type'] not in TYPES:
                raise ValueError('Ignored matchup identity/date/game-type filter')
            if any(not r[k] for k in KEY):
                raise ValueError('Missing matchup pitch key')
        atomic_json(path, {'params': params, 'source_url': response.url, 'fetched_at_utc': now(),
            'rows': rows, 'sha256': hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()})
    return rows, path


def reconcile(role, person, season, rows):
    expected, sources = {}, []
    for game_type in sorted(TYPES):
        response = request(f'{MLB}/people/{person}/stats', {'stats': 'gameLog',
            'group': 'pitching' if role == 'pitcher' else 'hitting', 'season': season, 'gameType': game_type})
        body = response.json()
        if 'stats' not in body:
            raise ValueError('Invalid appearance-log response')
        sources.append(response.url)
        for block in body['stats']:
            for s in block.get('splits', []):
                if f'{season}-03-01' <= s['date'] <= f'{season}-10-20' and s.get('sport', {}).get('id') == 1:
                    expected[str(s['game']['gamePk'])] = s['stat']['numberOfPitches']
    physical = Counter(r['game_pk'] for r in rows if r['description'] not in AUTOMATIC)
    differences = [{'game_pk': k, 'csv_pitches': physical[k], 'mlb_pitches': n}
                   for k, n in expected.items() if physical[k] != n]
    extra = sorted(set(physical) - set(expected))
    return {'expected_games_with_pitches': sum(n > 0 for n in expected.values()),
        'saved_games_with_pitches': len(physical), 'physical_pitches': sum(physical.values()),
        'expected_physical_pitches': sum(expected.values()), 'differences': differences,
        'unexpected_games': extra, 'sources': sources}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    roster_response = request(f'{MLB}/teams/139/roster', {'rosterType': 'active', 'hydrate': 'person'})
    roster = roster_response.json()
    atomic_json(OUT / 'rays_roster.json', roster)
    batters = [r for r in roster['roster'] if r['position']['abbreviation'] != 'P']
    manifest = {'as_of': AS_OF, 'status': 'in_progress', 'roster_source': roster_response.url,
        'fetched_at_utc': now(), 'players': [], 'batters': [{'id': r['person']['id'],
            'name': r['person']['fullName'], 'bat_side': r['person']['batSide']['code']} for r in batters]}
    atomic_json(OUT / 'manifest.json', manifest)
    people = [('pitcher', MIZ, 'Jacob Misiorowski')] + [('batter', r['person']['id'], r['person']['fullName']) for r in batters]
    for role, person, name in people:
        for season in (2025, 2026):
            print(f'{name} {role} {season}', flush=True)
            rows, path = fetch(role, person, season)
            audit = reconcile(role, person, season, rows)
            manifest['players'].append({'role': role, 'id': person, 'name': name, 'season': season,
                'file': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'rows': len(rows), 'audit': audit})
            atomic_json(OUT / 'manifest.json', manifest)
            print(f"  rows {len(rows)}; count differences {len(audit['differences'])}; unexpected {len(audit['unexpected_games'])}", flush=True)
    manifest['status'] = 'complete' if all(not p['audit']['differences'] and not p['audit']['unexpected_games'] for p in manifest['players']) else 'incomplete'
    atomic_json(OUT / 'manifest.json', manifest)
    print('Matchup acquisition:', manifest['status'], flush=True)
    if manifest['status'] != 'complete':
        raise SystemExit('Resolve matchup coverage discrepancies before fitting')


if __name__ == '__main__':
    main()
