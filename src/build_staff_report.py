"""Build a staff explorer that loads one compressed pitcher dataset at a time."""
import gzip
import json
import shutil

import pandas as pd

from download_statcast import ROOT, atomic_json
from matchup_model import LABELS
from staff_matchup import RUN, NAMES, P, HISTORY


def encode_records(frame,batters,pitches,results,history):
    rows=[]
    for r in frame.itertuples():
        prefix=[batters[str(r.batter)],r.balls,r.strikes,r.outs,r.base_mask]
        if history:
            prefix += [pitches[r.previous_pitch],results[r.previous_result]]
        row=prefix+[pitches[r.candidate_pitch],round(r.expected_batting_run_delta,8),round(r.erpa_runs_per_pitch,8),int(r.pitcher_count_pitch_support)]
        if history:row.append(int(r.pitcher_history_support))
        row += [round(r.sparse_mapping_probability,5)]
        row += [round(getattr(r,'p_'+label),7) for label in LABELS]
        row.append(int(r.support_fallback))
        rows.append(row)
    return rows


def main():
    manifest=json.loads((RUN/'forecast_manifest.json').read_text());metrics=json.loads((RUN/'metrics.json').read_text())
    data_dir=RUN/'data';data_dir.mkdir(exist_ok=True)
    batters={str(p['id']):i for i,p in enumerate(manifest['batters'])}
    pitch_list=['START']+sorted({a for p in manifest['pitchers'] for a in p['repertoire']})
    pitch_index={a:i for i,a in enumerate(pitch_list)};result_list=['START','ball','strike','whiff','foul'];result_index={a:i for i,a in enumerate(result_list)}
    weights=pd.read_csv(RUN/'run_value_weights.csv')
    weight_table={ '|'.join(map(str,key)):g.set_index('outcome').reindex(LABELS).expected_batting_run_delta.tolist()
        for key,g in weights.groupby(['balls','strikes','outs','base_mask'])}
    meta={**manifest,'pitch_names':NAMES,'pitches':pitch_list,'results':result_list,'outcomes':LABELS,'weights':weight_table,'metrics':metrics}
    reports=['# Brewers pitchers vs Rays: individual matchup sheets','',
        f"{len(manifest['pitchers'])} pitchers, {len(manifest['batters'])} hitters, {manifest['count_situations']:,} count/base/out situations and {manifest['candidate_comparisons']:,} supported exact-history candidate comparisons.",'',
        'Open http://localhost:8765/explorer.html for ranked pitches at every count, runner/out state and reachable previous history. Read [the ERPA guide](ERPA_GUIDE.md) for the full definition and calculation.','',
        f"Source cutoff: **{manifest['as_of']}**. Forecast context date: {manifest['forecast_date']}. Active-roster membership is not a guarantee of final game eligibility, health or availability. The source schedule lists Game 1 on October 23; no last-game result or confirmed batting order is assumed.",'',
        'These tables use **bases empty, no outs**. Openers and two-strike choices average this pitcher’s observed reachable histories; the called-strike and ball branches condition on the recommended opener and that actual result. They are next-pitch rankings, not a fixed script or a proven optimal sequence. ERPA is runs per 100 equivalent decisions above **this pitcher’s own supported usual mix**; it is not comparable across pitchers as an ability rating. A `*` means only one supported pitch and therefore ERPA zero.','',
        f"Shared model: {metrics['selected']['name']}; mean regular-season development log loss {metrics['selected']['mean_log_loss']:.5f}. October has already been inspected and is used only for retrospective diagnostics. No new independent action-policy validation is claimed.",'']
    for person in manifest['pitchers']:
        out=RUN/'pitchers'/str(person['id'])
        average=pd.read_csv(out/'count_candidates.csv.gz',dtype={'batter':str,'pitcher':str})
        history=pd.read_csv(out/'history_candidates.csv.gz',dtype={'batter':str,'pitcher':str})
        history['candidate_count']=history.groupby(HISTORY).candidate_pitch.transform('size')
        payload=dict(marginal=encode_records(average,batters,pitch_index,result_index,False),
                     history=encode_records(history,batters,pitch_index,result_index,True))
        raw=json.dumps(payload,separators=(',',':'),allow_nan=False).encode()
        (data_dir/f"{person['id']}.json").write_bytes(raw)
        (data_dir/f"{person['id']}.json.gz").write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
        a=average[average.outs.eq(0)&average.base_mask.eq(0)&average['rank'].eq(1)].set_index(['batter','balls','strikes'])
        h=history[history.outs.eq(0)&history.base_mask.eq(0)&history['rank'].eq(1)].set_index(['batter','balls','strikes','previous_pitch','previous_result'])
        lines=[f"## {person['name']} ({person['throws']}HP)",'',
            f"Supported arsenal across batting sides: {', '.join(NAMES.get(p,p) for p in person['repertoire'])}. Source-season pitches: {person['season_pitches']:,}. Last recorded appearance: {person['last_appearance']}; latest four outings: {person['recent_pitches']} pitches. These records do not establish game availability.",'',
            '| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |',
            '|---|---|---|---|---|---|---|']
        for batter in manifest['batters']:
            bid=str(batter['id']);first=a.loc[(bid,0,0)];opener=first.candidate_pitch
            strike=h.loc[(bid,0,1,opener,'strike')];ball=h.loc[(bid,1,0,opener,'ball')]
            def formatted(row):
                star='*' if int(row.get('candidate_count',2))==1 else ''
                return f"{row.candidate_pitch}{star} ({row.erpa_runs_per_100:+.2f})"
            side=('L' if person['throws']=='R' else 'R') if batter['bat_side']=='S' else batter['bat_side']
            lines.append(f"| {batter['name']} | {side} | {formatted(first)} | {formatted(strike)} | {formatted(ball)} | {formatted(a.loc[(bid,0,2)])} | {formatted(a.loc[(bid,3,2)])} |")
        lines+=['',f"[Count summaries](pitchers/{person['id']}/count_summary.csv) · [Ranked count candidates](pitchers/{person['id']}/count_candidates.csv.gz) · [Exact-history candidate comparisons](pitchers/{person['id']}/history_candidates.csv.gz)",'']
        reports+=lines
        local='\n'.join(lines).replace(f"pitchers/{person['id']}/",'')
        (out/'PLAN.md').write_text(local+'\n')
        print(f"Built {person['name']}: {len(raw):,} bytes, compressed {(data_dir/f'{person['id']}.json.gz').stat().st_size:,}",flush=True)
    report='\n'.join(reports)
    (RUN/'STAFF_RAYS_GAME_PLAN.md').write_text(report+'\n')
    (ROOT/'STAFF_RAYS_GAME_PLAN.md').write_text(report.replace('](pitchers/',']('+str(RUN.relative_to(ROOT))+'/pitchers/')+'\n')
    shutil.copyfile(ROOT/'ERPA_GUIDE.md',RUN/'ERPA_GUIDE.md')
    html=(ROOT/'src/staff_explorer.html').read_text()
    encoded=json.dumps(meta,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    (RUN/'explorer.html').write_text(html.replace('META_JSON',encoded))
    shutil.copyfile(ROOT/'src/staff_explorer.js',RUN/'app.js')
    atomic_json(RUN/'ui_manifest.json',dict(pitchers=len(manifest['pitchers']),batters=len(manifest['batters']),
        transport='Per-pitcher gzip JSON loaded on selection; plain JSON fallback; HTTP required',
        count_situations=manifest['count_situations'],candidate_comparisons=manifest['candidate_comparisons']))
    print('Built staff explorer:',RUN/'explorer.html',flush=True)


if __name__=='__main__':main()
