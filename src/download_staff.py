"""Acquire audited histories for the active Brewers staff and active Rays hitters.

This version reuses the immutable October 20 matchup snapshot for unchanged
players. New pitcher histories use the same acquisition and reconciliation rules.
Roster/schedule snapshots are read-only MLB feeds, not assumed game availability.
"""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from download_statcast import ROOT, MLB, atomic_json, now, request
from download_matchup import AS_OF, fetch, reconcile

OUT=ROOT/'data/processed/staff_rays'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # Keep the first roster/schedule snapshots for reproducible reruns. Use a new
    # versioned source directory when intentionally refreshing a later matchup.
    snapshots={'brewers_roster':(f'{MLB}/teams/158/roster',{'rosterType':'active','hydrate':'person'}),
        'rays_roster':(f'{MLB}/teams/139/roster',{'rosterType':'active','hydrate':'person'}),
        'schedule':(f'{MLB}/schedule',{'sportId':1,'teamId':158,'startDate':'2026-10-01','endDate':'2026-11-07','hydrate':'probablePitcher'})}
    for name,(url,params) in snapshots.items():
        if not (OUT/f'{name}.json').exists():
            atomic_json(OUT/f'{name}.json',request(url,params).json())
    original=json.loads((ROOT/'data/processed/matchup/manifest.json').read_text())
    if original['status']!='complete' or original['as_of']!=AS_OF:
        raise ValueError('Original matchup snapshot is not complete at this cutoff')
    old={(p['role'],p['id'],p['season']):p for p in original['players']}
    brewers=json.loads((OUT/'brewers_roster.json').read_text())
    rays=json.loads((OUT/'rays_roster.json').read_text())
    pitchers=[dict(id=r['person']['id'],name=r['person']['fullName'],
        throws=r['person']['pitchHand']['code']) for r in brewers['roster'] if r['position']['abbreviation']=='P']
    batters=[dict(id=r['person']['id'],name=r['person']['fullName'],
        bat_side=r['person']['batSide']['code']) for r in rays['roster'] if r['position']['abbreviation']!='P']
    manifest=dict(as_of=AS_OF,status='in_progress',fetched_at_utc=now(),pitchers=pitchers,batters=batters,players=[],
        source_snapshots={name:dict(file=str((OUT/f'{name}.json').relative_to(ROOT)),
            sha256=hashlib.sha256((OUT/f'{name}.json').read_bytes()).hexdigest()) for name in snapshots},
        roster_note='Active roster snapshot, not a guarantee of World Series eligibility, health, rest or game availability',
        roster_sources=['https://statsapi.mlb.com/api/v1/teams/158/roster?rosterType=active&hydrate=person',
                        'https://statsapi.mlb.com/api/v1/teams/139/roster?rosterType=active&hydrate=person'])
    tasks=[(role,person,season) for role,people in [('pitcher',pitchers),('batter',batters)] for person in people for season in (2025,2026)]
    def acquire(task):
        role,person,season=task; key=(role,person['id'],season)
        if key in old:
            saved=old[key].copy(); path=ROOT/saved['file']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=saved['sha256']:
                raise ValueError('Existing audited source changed')
            saved['reused_audit']=True
            return saved
        rows,path=fetch(role,person['id'],season)
        audit=reconcile(role,person['id'],season,rows)
        return dict(role=role,id=person['id'],name=person['name'],season=season,
            file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rows=len(rows),audit=audit)
    atomic_json(OUT/'manifest.json',manifest)
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(acquire,t) for t in tasks]
        for future in as_completed(futures):
            p=future.result(); manifest['players'].append(p)
            atomic_json(OUT/'manifest.json',manifest)
            print(f"{p['name']} {p['season']} {p['role']}: {p['rows']} rows; differences={len(p['audit']['differences'])}, extra={len(p['audit']['unexpected_games'])}",flush=True)
    manifest['players'].sort(key=lambda p:(p['role'],p['id'],p['season']))
    manifest['status']='complete' if all(not p['audit']['differences'] and not p['audit']['unexpected_games'] for p in manifest['players']) else 'incomplete'
    atomic_json(OUT/'manifest.json',manifest)
    if manifest['status']!='complete':raise ValueError('Resolve staff coverage differences before training')
    print(f"Complete: {len(pitchers)} pitchers, {len(batters)} hitters, {len(manifest['players'])} player seasons",flush=True)


if __name__=='__main__':main()
