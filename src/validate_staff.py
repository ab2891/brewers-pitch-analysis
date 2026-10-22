"""Check generated staff coverage, legal histories, values and separate baselines."""
import json
import numpy as np
import pandas as pd

from download_statcast import atomic_json, now
from staff_matchup import RUN, STATE, HISTORY, P, batter_side


def main():
    manifest=json.loads((RUN/'forecast_manifest.json').read_text())
    values=pd.read_csv(RUN/'run_value_weights.csv').pivot(index=['balls','strikes','outs','base_mask'],columns='outcome',values='expected_batting_run_delta').reindex(columns=[p[2:] for p in P])
    checked=[]
    for person in manifest['pitchers']:
        out=RUN/'pitchers'/str(person['id'])
        summary=pd.read_csv(out/'count_summary.csv',dtype={'batter':str,'pitcher':str})
        average=pd.read_csv(out/'count_candidates.csv.gz',dtype={'batter':str,'pitcher':str})
        history=pd.read_csv(out/'history_candidates.csv.gz',dtype={'batter':str,'pitcher':str})
        assert len(summary)==len(manifest['batters'])*12*24
        assert not summary.duplicated(STATE).any()
        for frame,keys in [(average,STATE),(history,HISTORY)]:
            assert frame.pitcher.eq(str(person['id'])).all()
            assert frame.p_throws.eq(person['throws']).all()
            assert not frame.duplicated(keys+['candidate_pitch']).any()
            assert np.isfinite(frame[P+['expected_batting_run_delta','erpa_runs_per_pitch']]).all().all()
            assert frame[P].ge(0).all().all() and np.allclose(frame[P].sum(axis=1),1,atol=1e-5)
            assert frame.groupby(keys)['rank'].min().eq(1).all()
            assert np.array_equal(frame.groupby(keys)['rank'].max().to_numpy(),frame.groupby(keys).size().to_numpy())
            assert frame.groupby(keys).expected_batting_run_delta.diff().dropna().ge(-1e-12).all()
            assert frame.regret_vs_best_runs.ge(-1e-12).all()
            assert np.allclose((frame.reference_mix_weight*frame.erpa_runs_per_pitch).groupby([frame[k] for k in keys]).sum(),0,atol=1e-10)
            idx=pd.MultiIndex.from_frame(frame[['balls','strikes','outs','base_mask']])
            erv=(frame[P].to_numpy()*values.reindex(idx).to_numpy()).sum(axis=1)
            assert np.allclose(erv,frame.expected_batting_run_delta)
            assert np.allclose(frame.usual_mix_batting_run_delta-frame.expected_batting_run_delta,frame.erpa_runs_per_pitch)
        for b in manifest['batters']:
            assert average.loc[average.batter.eq(str(b['id'])),'stand'].eq(batter_side(b['bat_side'],person['throws'])).all()
        for r in history[['balls','strikes','previous_pitch','previous_result']].drop_duplicates().itertuples(index=False):
            if r.previous_pitch=='START':assert (r.balls,r.strikes,r.previous_result)==(0,0,'START')
            elif r.previous_result=='ball':assert r.balls>=1
            else:assert r.strikes>=1
        probe=average[average.batter.eq(str(manifest['batters'][0]['id']))]
        variation=probe.groupby(['balls','strikes','candidate_pitch'])[P].max()-probe.groupby(['balls','strikes','candidate_pitch'])[P].min()
        checked.append(dict(id=person['id'],name=person['name'],count_situations=len(summary),
            candidate_comparisons=len(history),max_probability_change_across_base_outs=float(variation.to_numpy().max())))
        print('Verified',person['name'],flush=True)
    assert len(checked)==13
    result=dict(checked_at_utc=now(),status='passed',pitchers=checked,
        count_situations=sum(p['count_situations'] for p in checked),
        candidate_comparisons=sum(p['candidate_comparisons'] for p in checked),
        invariants='Complete unique states, legal histories, correct pitcher and batting side, finite normalized probabilities, ordered ranks, ERV matches outcome weights, own-mix ERPA zero')
    atomic_json(RUN/'validation.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='pitchers'},indent=2))


if __name__=='__main__':main()
