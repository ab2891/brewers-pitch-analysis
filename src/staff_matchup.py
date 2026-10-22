"""Train a shared staff model, then score each pitcher's own repertoire and mix.

No new independent postseason test is claimed. Chronological development folds
select architecture/features; previously inspected October outcomes are diagnostic.
"""
import argparse
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, mean_squared_error

import matchup_model as mm
from download_statcast import ROOT, atomic_json, now
from improve_matchup import BASE, DAMAGE, base_features, damage_priors, FOLDS
from run_value import fit_run_weights, reachable_states, run_values, base_label
from sequence import states_for, continuation

RUN=ROOT/'artifacts/brewers_rays_20261023_staff'
SOURCE=ROOT/'data/processed/staff_rays/manifest.json'
P=['p_'+x for x in mm.LABELS]
STATE=['batter','balls','strikes','outs','base_mask']
HISTORY=STATE+['previous_pitch','previous_result']
NAMES={'FF':'Four-seam fastball','SI':'Sinker','FC':'Cutter','CU':'Curveball','KC':'Knuckle curve',
       'SL':'Slider','ST':'Sweeper','CH':'Changeup','FS':'Splitter','FO':'Forkball','SV':'Slurve','KN':'Knuckleball'}


def batter_side(bat_side, throws):
    return ('L' if throws=='R' else 'R') if bat_side=='S' else bat_side


def prepare():
    data,manifest,info=mm.load_matchup(SOURCE)
    data=damage_priors(base_features(mm.with_priors(data)))
    if data.game_date.max()>pd.Timestamp(manifest['as_of']):raise ValueError('Future source observations')
    RUN.mkdir(parents=True,exist_ok=True)
    data.to_pickle(RUN/'model_frame.pkl')
    atomic_json(RUN/'manifest.json',manifest)
    info['frame_sha256']=hashlib.sha256((RUN/'model_frame.pkl').read_bytes()).hexdigest()
    atomic_json(RUN/'data_audit.json',info)
    return data,manifest


def train():
    if (RUN/'forecast.joblib').exists():raise ValueError('Preserve the fitted staff run; select a new version for retraining')
    RUN.mkdir(parents=True,exist_ok=True)
    atomic_json(RUN/'protocol.json',dict(created_at_utc=now(),folds=FOLDS,
        candidates=['shape_base_outs','pitcher_identity','pitcher_identity_damage'],depth=3,sequence=True,
        selection='minimum mean regular-season chronological development log loss',
        postseason='known sample; retrospective diagnostic only, never selects model',
        support=dict(season_total=50,hand_total=20,last_four_outings=3,count_hand=5),
        reference='Each pitcher own 2026 count/hand frequencies, normalized over supported candidates',
        objective='Immediate next-pitch expected batting run delta, not win probability or full-game optimization'))
    data,manifest=prepare()
    candidates=[('shape_base_outs',BASE,[]),('pitcher_identity',BASE,['pitcher']),
                ('pitcher_identity_damage',BASE+DAMAGE,['pitcher'])]
    scores=[]
    for name,numeric,categorical in candidates:
        folds=[]
        for begin,end in FOLDS:
            training=data[data.game_date.lt(begin)]
            validation=data[data.game_date.between(begin,end,inclusive='left')]
            model,encoder,features=mm.fit_model(training,validation,True,3,extra_numeric=numeric,extra_categorical=categorical)
            p=model.predict_proba(encoder.transform(validation[features]))
            baseline=mm.baseline_fit(training)
            folds.append(dict(log_loss=float(log_loss(validation.label,p,labels=range(len(mm.LABELS)))),
                context_log_loss=float(log_loss(validation.label,mm.baseline_predict(baseline,validation),labels=range(len(mm.LABELS)))),
                rounds=int(model.best_iteration+1),rows=len(validation),games=int(validation.game_pk.nunique())))
        record=dict(name=name,numeric=numeric,categorical=categorical,folds=folds,
            mean_log_loss=float(np.mean([f['log_loss'] for f in folds])))
        scores.append(record);atomic_json(RUN/'development_progress.json',scores)
        print(json.dumps(record),flush=True)
    selected=min(scores,key=lambda s:s['mean_log_loss'])
    rounds=int(np.median([f['rounds'] for f in selected['folds']]))
    atomic_json(RUN/'selection.json',dict(candidates=scores,selected=selected,rounds=rounds,selected_at=now()))
    training=data[data.game_date.lt('2026-10-01')];test=data[data.game_date.ge('2026-10-01')]
    model,encoder,features=mm.fit_model(training,None,True,3,rounds,selected['numeric'],selected['categorical'])
    bundle=dict(model=model,encoder=encoder,features=features,scorer='xgboost')
    joblib.dump(bundle,RUN/'evaluation.joblib')
    probability=mm.predict(bundle,test)
    baseline=mm.baseline_fit(training); context=mm.baseline_predict(baseline,test)
    mapping=fit_run_weights(training).pivot(index=['balls','strikes','outs','base_mask'],columns='outcome',values='expected_batting_run_delta').reindex(columns=mm.LABELS)
    weights=mapping.reindex(pd.MultiIndex.from_frame(test[['balls','strikes','outs','base_mask']])).to_numpy()
    rv=run_values(probability,weights); target=pd.to_numeric(test.delta_run_exp,errors='coerce').to_numpy();finite=np.isfinite(target)
    mean=pd.to_numeric(training.delta_run_exp,errors='coerce').mean()
    per_pitcher=[]
    for person in manifest['pitchers']:
        mask=test.pitcher.eq(str(person['id'])).to_numpy()
        per_pitcher.append(dict(**person,diagnostic_rows=int(mask.sum()),
            diagnostic_games=int(test.loc[mask,'game_pk'].nunique()),
            diagnostic_log_loss=float(log_loss(test.loc[mask,'label'],probability[mask],labels=range(len(mm.LABELS)))) if mask.any() else None,
            context_log_loss=float(log_loss(test.loc[mask,'label'],context[mask],labels=range(len(mm.LABELS)))) if mask.any() else None))
    scored=test[list(mm.KEY)+['game_date','pitcher','batter','outcome']].copy()
    scored[P]=probability;scored.to_csv(RUN/'postseason_diagnostic.csv',index=False)
    model,encoder,features=mm.fit_model(data,None,True,3,rounds,selected['numeric'],selected['categorical'])
    joblib.dump(dict(model=model,encoder=encoder,features=features,scorer='xgboost'),RUN/'forecast.joblib')
    atomic_json(RUN/'metrics.json',dict(selected=selected,rounds=rounds,rows=len(data),as_of=manifest['as_of'],
        retrospective_diagnostic=dict(note='Previously inspected October data; not an independent test or action-policy validation',rows=len(test),games=int(test.game_pk.nunique()),
            log_loss=float(log_loss(test.label,probability,labels=range(len(mm.LABELS)))),
            context_log_loss=float(log_loss(test.label,context,labels=range(len(mm.LABELS)))),
            run_value_rmse=float(np.sqrt(mean_squared_error(target[finite],rv[finite]))),
            constant_run_value_rmse=float(np.sqrt(mean_squared_error(target[finite],np.full(finite.sum(),mean))))),
        per_pitcher=per_pitcher,frame_sha256=hashlib.sha256((RUN/'model_frame.pkl').read_bytes()).hexdigest()))
    print('Staff training complete',flush=True)


def support_inventory(data,person,batters):
    """Separate action support from history support; never manufacture a repertoire."""
    pitcher=data[data.pitcher.eq(str(person['id'])) & data.game_date.ge('2026-01-01')]
    dates=sorted(pitcher.game_date.unique())[-4:]
    recent=pitcher[pitcher.game_date.isin(dates)]
    totals=pitcher.groupby('pitch_type').size();recent_n=recent.groupby('pitch_type').size()
    rows=[]; exclusions=[]
    for batter in batters:
        side=batter_side(batter['bat_side'],person['throws'])
        subset=pitcher[pitcher.stand.eq(side)]
        by_hand=subset.groupby('pitch_type').size()
        actions=[a for a,n in totals.items() if n>=50 and by_hand.get(a,0)>=20 and recent_n.get(a,0)>=3]
        for a in totals.index:
            if a not in actions:
                exclusions.append(dict(batter=batter['id'],stand=side,pitch=a,season_n=int(totals[a]),
                    hand_n=int(by_hand.get(a,0)),recent_n=int(recent_n.get(a,0))))
        if not actions:
            raise ValueError(f"No supported repertoire for {person['name']} vs {side}; do not invent a ranking")
        count_n=subset.groupby(['balls','strikes','pitch_type']).size()
        histories=subset.groupby(['balls','strikes','previous_pitch_type','previous_result']).size()
        inventory=[]
        for b,s,previous,result in states_for(actions):
            allowed=[a for a in actions if count_n.get((b,s,a),0)>=5]
            fallback=not allowed
            if fallback:allowed=[max(actions,key=lambda a:count_n.get((b,s,a),0))]
            for action in allowed:
                inventory.append(dict(pitcher=str(person['id']),pitcher_name=person['name'],p_throws=person['throws'],
                    batter=str(batter['id']),batter_name=batter['name'],stand=side,balls=b,strikes=s,
                    previous_pitch=previous,previous_result=result,candidate_pitch=action,
                    pitcher_count_pitch_support=int(count_n.get((b,s,action),0)),
                    pitcher_history_support=int(histories.get((b,s,previous,result),0)),
                    recent_pitch_support=int(recent_n.get(action,0)),support_fallback=fallback))
        frame=pd.DataFrame(inventory);legal=reachable_states(frame)
        frame=frame.loc[[tuple(s) in legal for s in frame[['balls','strikes','previous_pitch','previous_result']].itertuples(index=False,name=None)]].copy()
        contexts=frame[['balls','strikes','previous_pitch','previous_result','pitcher_history_support']].drop_duplicates()
        total=contexts.groupby(['balls','strikes']).pitcher_history_support.transform('sum')
        count=contexts.groupby(['balls','strikes']).pitcher_history_support.transform('size')
        contexts['history_weight']=np.where(total.gt(0),contexts.pitcher_history_support/total,1/count)
        frame=frame.merge(contexts.drop(columns='pitcher_history_support'),on=['balls','strikes','previous_pitch','previous_result'],validate='many_to_one')
        rows.append(frame)
    inventory=pd.concat(rows,ignore_index=True)
    return inventory,dict(**person,season_pitches=len(pitcher),last_appearance=str(pitcher.game_date.max().date()),
        recent_dates=[str(pd.Timestamp(d).date()) for d in dates],recent_pitches=len(recent),
        repertoire=sorted(inventory.candidate_pitch.unique()),excluded_pitch_hand_pairs=exclusions)


def add_erp_columns(frame):
    """ERP is the expected reduction in run expectancy, not mix-relative gain.

    Negative values are retained: a pitch can increase expected scoring.
    Legacy erpa columns retain their original mix-relative meaning.
    """
    result=frame.copy()
    result['erp_runs_per_pitch']=-result.expected_batting_run_delta
    result['erp_runs_per_100']=100*result.erp_runs_per_pitch
    result['usual_mix_erp_runs_per_pitch']=-result.usual_mix_batting_run_delta
    result['improvement_over_usual_mix_runs_per_pitch']=result.erp_runs_per_pitch-result.usual_mix_erp_runs_per_pitch
    result['improvement_over_usual_mix_runs_per_100']=100*result.improvement_over_usual_mix_runs_per_pitch
    return result


def rank_candidates(frame,keys):
    result=frame.copy()
    keys=(['pitcher'] if 'pitcher' in result and 'pitcher' not in keys else [])+list(keys)
    mix=result.pitcher_count_pitch_support.astype(float)
    total=mix.groupby([result[k] for k in keys]).transform('sum')
    n=result.groupby(keys).candidate_pitch.transform('size')
    result['reference_mix_weight']=np.where(total.gt(0),mix/total,1/n)
    ref=(result.reference_mix_weight*result.expected_batting_run_delta).groupby([result[k] for k in keys]).transform('sum')
    result['usual_mix_batting_run_delta']=ref
    result['erpa_runs_per_pitch']=ref-result.expected_batting_run_delta
    result['erpa_runs_per_100']=100*result.erpa_runs_per_pitch
    result['regret_vs_best_runs']=result.expected_batting_run_delta-result.groupby(keys).expected_batting_run_delta.transform('min')
    result['rank']=result.groupby(keys).expected_batting_run_delta.rank(method='first').astype(int)
    result=add_erp_columns(result)
    return result.sort_values(keys+['rank']).reset_index(drop=True)


def score(forecast_date):
    data=pd.read_pickle(RUN/'model_frame.pkl');manifest=json.loads((RUN/'manifest.json').read_text())
    metrics=json.loads((RUN/'metrics.json').read_text())
    if hashlib.sha256((RUN/'model_frame.pkl').read_bytes()).hexdigest()!=metrics['frame_sha256']:raise ValueError('Training frame changed')
    if pd.Timestamp(forecast_date)<=pd.Timestamp(manifest['as_of']):raise ValueError('Forecast date must follow frozen history')
    bundle=joblib.load(RUN/'forecast.joblib')
    weights=fit_run_weights(data)
    target_index=['balls','strikes','outs','base_mask']
    values=weights.pivot(index=target_index,columns='outcome',values='expected_batting_run_delta').reindex(columns=mm.LABELS)
    support=weights.pivot(index=target_index,columns='outcome',values='full_cell_n').reindex(columns=mm.LABELS)
    weights.to_csv(RUN/'run_value_weights.csv',index=False)
    people=[]
    for person in manifest['pitchers']:
        out=RUN/'pitchers'/str(person['id']);out.mkdir(parents=True,exist_ok=True)
        inventory,profile=support_inventory(data,person,manifest['batters'])
        queries=inventory.rename(columns={'candidate_pitch':'pitch_type','previous_pitch':'previous_pitch_type'}).copy()
        queries['game_date']=pd.Timestamp(forecast_date);queries['outcome']=None;queries['description']='';queries['woba_value']=np.nan
        queries['outs_when_up']=0
        for col in mm.MEASURE+['on_1b','on_2b','on_3b','launch_speed','estimated_woba_using_speedangle']:queries[col]=np.nan
        combined=pd.concat([data,queries],ignore_index=True)
        enriched=damage_priors(base_features(mm.with_priors(combined))).iloc[len(data):].reset_index(drop=True)
        batches=[]
        for outs in range(3):
            for bases in range(8):
                q=enriched.copy();q['outs']=outs
                for base,bit in [('1b',1),('2b',2),('3b',4)]:q['runner_'+base]=int(bool(bases&bit))
                probability=mm.predict(bundle,q)
                part=inventory.copy();part['outs']=outs;part['base_mask']=bases
                part[P]=probability
                idx=pd.MultiIndex.from_frame(part[target_index])
                part['expected_batting_run_delta']=run_values(probability,values.reindex(idx).to_numpy())
                part['sparse_mapping_probability']=(probability*(support.reindex(idx).to_numpy()<20)).sum(axis=1)
                batches.append(part)
        detail=rank_candidates(pd.concat(batches,ignore_index=True),HISTORY)
        # Marginalize probabilities over this pitcher's count/hand history frequencies.
        grouping=STATE+['candidate_pitch']
        weighted=detail[P].mul(detail.history_weight,axis=0)
        weighted[grouping]=detail[grouping]
        average=weighted.groupby(grouping,sort=False)[P].sum().reset_index()
        info=detail.groupby(grouping,sort=False)[['pitcher','pitcher_name','batter_name','p_throws','stand',
            'pitcher_count_pitch_support','recent_pitch_support','support_fallback']].first().reset_index()
        average=average.merge(info,on=grouping,validate='one_to_one')
        idx=pd.MultiIndex.from_frame(average[target_index]);v=values.reindex(idx).to_numpy()
        average['expected_batting_run_delta']=run_values(average[P].to_numpy(),v)
        average['sparse_mapping_probability']=(average[P].to_numpy()*(support.reindex(idx).to_numpy()<20)).sum(axis=1)
        average=rank_candidates(average,STATE)
        summary=average[average['rank'].eq(1)].copy()
        sizes=average.groupby(STATE).candidate_pitch.transform('size')
        average['candidate_count']=sizes
        summary=summary.merge(average[average['rank'].eq(2)][STATE+['candidate_pitch','regret_vs_best_runs']].rename(
            columns={'candidate_pitch':'runner_up','regret_vs_best_runs':'advantage_vs_runner_up_runs'}),on=STATE,how='left',validate='one_to_one')
        summary['candidate_count']=average.groupby(STATE).size().reindex(pd.MultiIndex.from_frame(summary[STATE])).to_numpy()
        assert len(summary)==len(manifest['batters'])*12*24
        assert np.allclose(average[P].sum(axis=1),1,atol=1e-5)
        assert np.allclose((detail.reference_mix_weight*detail.erpa_runs_per_pitch).groupby([detail[k] for k in HISTORY]).sum(),0,atol=1e-10)
        average.to_csv(out/'count_candidates.csv.gz',index=False,compression='gzip')
        summary.to_csv(out/'count_summary.csv',index=False)
        detail.to_csv(out/'history_candidates.csv.gz',index=False,compression='gzip')
        profile.update(count_situations=len(summary),history_situations=detail[HISTORY].drop_duplicates().shape[0],
            candidate_comparisons=len(detail),single_candidate_situations=int(summary.candidate_count.eq(1).sum()),
            forecast_date=forecast_date)
        atomic_json(out/'profile.json',profile);people.append(profile)
        print(f"Scored {person['name']}: {len(summary)} situations; {len(detail)} history comparisons",flush=True)
    atomic_json(RUN/'forecast_manifest.json',dict(generated_at_utc=now(),as_of=manifest['as_of'],forecast_date=forecast_date,
        pitchers=people,batters=manifest['batters'],count_situations=sum(p['count_situations'] for p in people),
        history_situations=sum(p['history_situations'] for p in people),
        candidate_comparisons=sum(p['candidate_comparisons'] for p in people),
        caveat='Roster snapshot, not final game availability. Immediate observational run-value rankings, not a causal optimum.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['train','score']);parser.add_argument('--forecast-date',default='2026-10-23')
    args=parser.parse_args()
    train() if args.phase=='train' else score(args.forecast_date)
