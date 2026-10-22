"""Versioned, pre-pitch base/out forecasts with lagged pitcher contact history.

Select on chronological regular-season development folds only. The October
sample is already known and is reported only as a retrospective diagnostic.
Original models and forecasts are preserved.
"""
import hashlib
import json
import shutil

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

import matchup_model as mm
from download_statcast import ROOT, atomic_json, now
from run_value import add_base_outs, reachable_states

RUN = ROOT / 'artifacts/miz_rays_20261023_v2'
BASE = ['outs', 'runner_1b', 'runner_2b', 'runner_3b']
DAMAGE = ['prior_pitch_contacts', 'prior_pitch_woba_contact',
          'prior_pitch_xwoba_contact', 'prior_pitch_hardhit_rate',
          'prior_pitch_recent_xwoba_contact']
FOLDS = [('2026-06-01', '2026-07-16'), ('2026-07-16', '2026-09-28')]


def audited_source():
    path=ROOT/'data/processed/matchup/model_frame.pkl'
    metrics=json.loads((mm.RUN/'metrics.json').read_text())
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != metrics['processed_frame_sha256']:
        raise ValueError('Original audited source frame changed')
    data=pd.read_pickle(path)
    manifest=json.loads((mm.RUN/'manifest.json').read_text())
    if data.game_date.max() > pd.Timestamp(manifest['as_of']):
        raise ValueError('Forecast contains observations after the acquisition cutoff')
    return data


def base_features(frame):
    result = add_base_outs(frame)
    for base, bit in [('1b', 1), ('2b', 2), ('3b', 4)]:
        result['runner_' + base] = (result.base_mask & bit).ne(0).astype(int)
    return result


def damage_priors(frame):
    """All features exclude the entire current date, including same-game pitches.

    Contact history is pooled toward fixed neutral priors (30 contacts). Recent
    contact damage uses a five-outing exponentially weighted numerator and
    denominator; no contact on an outing does not manufacture a zero-damage hit.
    Forecast queries have no observed outcomes and never enter the numerators.
    """
    result = frame.copy()
    keys = ['pitcher', 'pitch_type', 'game_date']
    temp = frame[keys].copy()
    contact = frame.description.eq('hit_into_play') & frame.outcome.notna()
    temp['contacts'] = contact.astype(int)
    for source, name in [('woba_value', 'woba'), ('estimated_woba_using_speedangle', 'xwoba'), ('launch_speed', 'ev')]:
        values = pd.to_numeric(frame[source], errors='coerce')
        valid = contact & values.notna()
        temp[name + '_n'] = valid.astype(int)
        temp[name] = values.where(valid, 0)
    temp['hardhit'] = (contact & pd.to_numeric(frame.launch_speed, errors='coerce').ge(95)).astype(int)
    cols = [c for c in temp if c not in keys]
    daily = temp.groupby(keys)[cols].sum().reset_index().sort_values(keys)
    groups = ['pitcher', 'pitch_type']
    prior = daily.groupby(groups)[cols].cumsum() - daily[cols]
    daily[DAMAGE[0]] = prior.contacts
    daily[DAMAGE[1]] = (prior.woba + 30*.32)/(prior.woba_n + 30)
    daily[DAMAGE[2]] = (prior.xwoba + 30*.32)/(prior.xwoba_n + 30)
    daily[DAMAGE[3]] = (prior.hardhit + 30*.35)/(prior.ev_n + 30)
    smooth = daily.groupby(groups)[['xwoba', 'xwoba_n']].transform(lambda x: x.ewm(span=5, adjust=False).mean())
    lagged = smooth.groupby([daily[k] for k in groups]).shift().fillna(0)
    daily[DAMAGE[4]] = (lagged.xwoba + 5*.32)/(lagged.xwoba_n + 5)
    joined = frame[keys].merge(daily[keys + DAMAGE], on=keys, how='left', sort=False)
    result[DAMAGE] = joined[DAMAGE].to_numpy()
    return result


def cutter_audit(data):
    miz = data[data.pitcher.eq(mm.MIZ) & data.game_date.ge('2026-01-01')].copy()
    rows = []
    for scope, part in [('Regular season', miz[miz.game_type.eq('R')]),
                        ('San Diego NLDS', miz[miz.game_pk.astype(str).eq('849830')]),
                        ('NLCS', miz[miz.game_type.eq('L')])]:
        for pitch, group in part.groupby('pitch_type'):
            if pitch not in ['FF', 'FC', 'CU', 'SL']:
                continue
            bip = group[group.description.eq('hit_into_play')]
            numeric = lambda col: pd.to_numeric(bip[col], errors='coerce')
            rows.append(dict(scope=scope, pitch=pitch, pitches=len(group), balls_in_play=len(bip),
                hits=int(bip.events.isin(['single','double','triple','home_run']).sum()),
                home_runs=int(bip.events.eq('home_run').sum()),
                mean_exit_velocity=numeric('launch_speed').mean(),
                hard_hits=int(numeric('launch_speed').ge(95).sum()),
                xwoba_on_contact=numeric('estimated_woba_using_speedangle').mean()))
    table = pd.DataFrame(rows)
    table.to_csv(RUN/'pitch_damage_audit.csv', index=False)
    display=table.round(3).fillna('—')
    markdown=['| '+' | '.join(display.columns)+' |','|'+'---|'*len(display.columns)]
    markdown+=['| '+' | '.join(map(str,row))+' |' for row in display.itertuples(index=False,name=None)]
    notes = ['# Miz pitch contact audit', '',
        'Descriptive results, not estimates of what a different pitch would have done. Hard hit means exit velocity ≥95 mph. Contact-only averages exclude missing measurements.', '', *markdown, '',
        'The NLDS cutter allowed two hard-hit singles in three balls in play. The third was an RBI fielder’s choice. This supports concern about that outing, but the regular-season cutter did not have the worst contact results.', '',
        'The classifier’s broad `out` category includes fielder’s choices; it does not imply zero run impact. Actual outcome-associated delta_run_exp is used in valuation. Advancement and fielder’s-choice risk are still pooled within that category. This remains a model limitation.', '',
        'Source: audited local Statcast data; https://baseballsavant.mlb.com/csv-docs']
    (RUN/'PITCH_DAMAGE_AUDIT.md').write_text('\n'.join(notes)+'\n')


def main():
    if (RUN/'forecast.joblib').exists():
        raise SystemExit('Version already trained; preserve its development selection')
    RUN.mkdir(exist_ok=True, parents=True)
    atomic_json(RUN/'protocol.json', dict(created_at=now(), folds=FOLDS,
        candidates=['original', 'base_outs', 'base_outs_damage'], depth=3, sequence=True,
        selection='minimum mean chronological development log loss among base/out candidates; original is a comparator',
        postseason='already seen, retrospective diagnostic only; never used for selection',
        label_note='Unchanged nine outcome classes for comparable scoring; out includes fielder choices'))
    raw = audited_source()
    data = damage_priors(base_features(raw))
    data.to_pickle(RUN/'model_frame.pkl')
    cutter_audit(data)
    scores=[]
    for name, extra in [('original', []), ('base_outs', BASE), ('base_outs_damage', BASE+DAMAGE)]:
        results=[]
        for start, end in FOLDS:
            train=data[data.game_date.lt(start)]
            val=data[data.game_date.between(start,end,inclusive='left')]
            model, encoder, features=mm.fit_model(train,val,True,3,extra_numeric=extra)
            p=model.predict_proba(encoder.transform(val[features]))
            results.append(dict(loss=float(log_loss(val.label,p,labels=range(len(mm.LABELS)))),
                                rounds=model.best_iteration+1,rows=len(val)))
        record=dict(name=name,extra=extra,folds=results,mean_loss=float(np.mean([r['loss'] for r in results])))
        scores.append(record)
        atomic_json(RUN/'development_progress.json',scores)
        print(json.dumps(record),flush=True)
    selected=min(scores[1:],key=lambda s:s['mean_loss'])
    rounds=int(np.median([r['rounds'] for r in selected['folds']]))
    atomic_json(RUN/'selection.json',dict(candidates=scores,selected=selected,rounds=rounds,selected_at=now()))
    train=data[data.game_date.lt('2026-10-01')]; test=data[data.game_date.ge('2026-10-01')]
    model,encoder,features=mm.fit_model(train,None,True,3,rounds,selected['extra'])
    p=model.predict_proba(encoder.transform(test[features]))
    scored=test[list(mm.KEY)+['game_date','pitcher','batter','outcome']].copy()
    for i,label in enumerate(mm.LABELS):scored['p_'+label]=p[:,i]
    scored.to_csv(RUN/'postseason_predictions.csv',index=False)
    joblib.dump(dict(model=model,encoder=encoder,features=features,scorer='xgboost'),RUN/'evaluation.joblib')
    model,encoder,features=mm.fit_model(data,None,True,3,rounds,selected['extra'])
    joblib.dump(dict(model=model,encoder=encoder,features=features,scorer='xgboost'),RUN/'forecast.joblib')
    digest=hashlib.sha256((RUN/'model_frame.pkl').read_bytes()).hexdigest()
    atomic_json(RUN/'metrics.json',dict(selected=selected,rounds=rounds,processed_frame_sha256=digest,
        original_development_loss=scores[0]['mean_loss'],
        retrospective_postseason_loss=float(log_loss(test.label,p,labels=range(len(mm.LABELS)))),
        postseason_note='Previously seen sample, diagnostic only. No independent validation of v2 or action ranking.',
        probability_inputs='Count, outs, three runner occupancy indicators, candidate, batter/hand, prior pitch/result and strictly lagged profiles',
        damage_selected=selected['name']=='base_outs_damage'))
    shutil.copyfile(mm.RUN/'manifest.json',RUN/'manifest.json')
    print('Saved version 2 model',flush=True)


def forecast():
    """Reuse the audited support inventory, score probabilities separately for all 24 states."""
    raw=audited_source()
    metrics=json.loads((RUN/'metrics.json').read_text())
    if hashlib.sha256((RUN/'model_frame.pkl').read_bytes()).hexdigest()!=metrics['processed_frame_sha256']:
        raise ValueError('Version 2 training frame changed after fitting')
    inventory=pd.read_csv(mm.RUN/'count_policies.csv',dtype={'batter':str})
    usable=[]
    for _,group in inventory.groupby('batter',sort=False):
        legal=reachable_states(group)
        usable.append(group.loc[[tuple(s) in legal for s in group[['balls','strikes','previous_pitch','previous_result']].itertuples(index=False,name=None)]])
    inventory=pd.concat(usable,ignore_index=True)
    queries=inventory[['batter','stand','balls','strikes','candidate_pitch','previous_pitch','previous_result']].rename(
        columns={'candidate_pitch':'pitch_type','previous_pitch':'previous_pitch_type'}).copy()
    queries['pitcher']=mm.MIZ; queries['p_throws']='R'; queries['game_date']=pd.Timestamp('2026-10-23')
    queries['outcome']=None; queries['description']=''; queries['woba_value']=np.nan
    queries['outs_when_up']=0
    for col in mm.MEASURE+['on_1b','on_2b','on_3b','launch_speed','estimated_woba_using_speedangle']:
        queries[col]=np.nan
    combined=pd.concat([raw,queries],ignore_index=True)
    enriched=damage_priors(base_features(mm.with_priors(combined))).iloc[len(raw):].reset_index(drop=True)
    bundle=joblib.load(RUN/'forecast.joblib')
    parts=[]
    for outs in range(3):
        for bases in range(8):
            q=enriched.copy(); q['outs']=outs; q['base_mask']=bases
            for base,bit in [('1b',1),('2b',2),('3b',4)]:q['runner_'+base]=int(bool(bases&bit))
            p=mm.predict(bundle,q)
            part=inventory.copy(); part['outs']=outs;part['base_mask']=bases
            for i,label in enumerate(mm.LABELS):part['p_'+label]=p[:,i]
            parts.append(part)
    pd.concat(parts,ignore_index=True).to_csv(RUN/'count_policies.csv',index=False)
    print('Saved base/out-specific forecast inventory',flush=True)


if __name__=='__main__':
    import sys
    forecast() if '--forecast' in sys.argv else main()
