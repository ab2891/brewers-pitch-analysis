"""Build a self-contained situation explorer and readable run-value documentation."""
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from download_statcast import ROOT
from matchup_model import RUN, LABELS
from run_value import COUNTS

RUN=Path(os.environ.get('MATCHUP_RUN', RUN)).resolve()
OUT=RUN/'run_values'


def main():
    summary=pd.read_csv(OUT/'count_summary.csv')
    candidates=pd.read_csv(OUT/'count_candidates.csv.gz')
    history=pd.read_csv(OUT/'history_candidates.csv.gz')
    hs=pd.read_csv(OUT/'history_summary.csv.gz')
    metrics=json.loads((OUT/'metrics.json').read_text())
    players=summary[['batter','batter_name']].drop_duplicates().to_dict('records')
    index={p['batter']:i for i,p in enumerate(players)}
    pitches=['START','FF','FC','CU','SL']
    results=['START','ball','strike','whiff','foul']
    compact=[]
    for row in history.itertuples():
        compact.append([index[row.batter],row.balls,row.strikes,row.outs,row.base_mask,
            pitches.index(row.previous_pitch),results.index(row.previous_result),pitches.index(row.candidate_pitch),
            round(row.expected_batting_run_delta,8),round(row.erpa_runs_per_pitch,8),row.miz_count_pitch_support,row.miz_history_support,
            *([round(getattr(row,'p_'+label),8) for label in LABELS] if hasattr(row,'p_ball') else [])])
    marginal=[]
    for row in candidates.itertuples():
        marginal.append([index[row.batter],row.balls,row.strikes,row.outs,row.base_mask,
            pitches.index(row.candidate_pitch),round(row.expected_batting_run_delta,8),round(row.erpa_runs_per_pitch,8),
            row.miz_count_pitch_support,round(row.sparse_mapping_probability,5),
            *[round(getattr(row,'erpa_from_'+label),8) for label in LABELS],
            *[round(getattr(row,'p_'+label),8) for label in LABELS]])
    sparse=[[index[row.batter],row.balls,row.strikes,row.outs,row.base_mask,
             pitches.index(row.previous_pitch),results.index(row.previous_result),round(row.sparse_mapping_probability,5)]
            for row in hs.itertuples()]
    audit_path=RUN/'pitch_damage_audit.csv'
    audit=json.loads(pd.read_csv(audit_path).to_json(orient='records')) if audit_path.exists() else []
    payload={'players':players,'pitches':pitches,'results':results,'outcomes':LABELS,
        'marginal':marginal,'history':compact,'sparsity':sparse,'audit':audit}
    encoded=json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    html='''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Miz–Rays: expected pitch run values</title>
<style>
body{font:16px/1.5 system-ui,sans-serif;margin:auto;max-width:1100px;padding:24px;color:#102536;background:#f3f6f8}
h1{font-size:1.8rem;margin-bottom:8px}p{max-width:900px}.controls,.card{background:white;padding:18px;border-radius:12px;margin:16px 0;border:1px solid #d8e0e6}
.controls{display:flex;gap:16px;flex-wrap:wrap}label{display:flex;flex-direction:column;gap:4px}select,button{font:inherit;padding:8px;border:1px solid #aab9c3;border-radius:6px;background:white}
#counts{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}button.active{background:#123d57;color:white}.muted{color:#526776}.notice{border-left:4px solid #a66e17;padding-left:12px}
table{border-collapse:collapse;width:100%;font-size:.95rem}th,td{text-align:left;padding:10px 7px;border-bottom:1px solid #e1e7ec}th{background:#edf3f6} .scroll{overflow:auto}.good{color:#126244}.bad{color:#a33131}.big{font-size:1.5rem;font-weight:700}small{font-size:.8rem}tr.best{background:#e5f4eb;font-weight:650}caption{text-align:left;margin:12px 0}
@media(max-width:600px){body{padding:12px}table{font-size:.85rem}th,td{padding:8px 4px}#counts button{font-size:.85rem}}
</style>
<h1>Miz vs. Rays: every count, in runs</h1>
<p>14 hitters · 12 counts · 24 base/out states · HISTORY_COUNT legal history situations. Pregame data cutoff: October 20, 2026. Game 1 lineup remains provisional.</p>
<p><strong>ERPA = expected batting run value of Miz’s usual supported mix − expected batting run value of this pitch.</strong> Positive ERPA favors the pitcher. Values describe the next pitch; “per 100” is 100 equivalent situations, not a full game or season projection.</p>
<div class="controls"><label>Hitter<select id="batter"></select></label><label>Outs<select id="outs"><option value="0">0 outs</option><option value="1">1 out</option><option value="2">2 outs</option></select></label><label>Runners<select id="bases"><option value="0">Bases empty</option><option value="1">1st</option><option value="2">2nd</option><option value="3">1st + 2nd</option><option value="4">3rd</option><option value="5">1st + 3rd</option><option value="6">2nd + 3rd</option><option value="7">Bases loaded</option></select></label></div>
<div id="counts"></div>
<div class="controls"><label>Previous pitch/result<select id="history"></select></label></div>
<div class="card"><div id="headline" class="big"></div><p id="context"></p><p id="baseline"></p><p id="support" class="notice"></p><div class="scroll"><table><caption>Ranked best to worst by expected batting runs allowed on the next pitch. Lower is better for Miz. Runner and out selections update the probabilities and values.</caption><thead><tr><th>Rank</th><th>Pitch</th><th>Expected batting runs/pitch ↓</th><th>ERPA runs/100 ↑</th><th>Behind #1, runs/100 ↓</th><th>Hit %</th><th>HR %</th><th>Whiff %</th><th>Miz sample</th></tr></thead><tbody id="rankings"></tbody></table></div><small>Hit % includes the model’s single/error/reach group; HR % is per pitch, not per contact. Miz sample is season count/hand support, pooled across runners and outs.</small></div>
<div class="card" id="explanation"><h2>Why the top pitch leads</h2><p>Each row is (usual-mix outcome probability − candidate outcome probability) × the estimated run impact of that outcome. Positive contributions save runs. Their sum is ERPA.</p><table><thead><tr><th>Outcome</th><th>ERPA contribution, runs/100</th></tr></thead><tbody id="contributions"></tbody></table></div>
<div class="card" id="audit"><h2>Is the cutter overrated?</h2><p>The San Diego NLDS concern is supported: two of three cutters put in play were hard-hit singles, and the third was an RBI fielder’s choice. Season-long cutter contact results were better. Compare both samples before judging the pitch. These are observed results, not predictions for this hitter.</p><p id="damage-model"></p><div class="scroll"><table><thead><tr><th>Sample</th><th>Pitch</th><th>Pitches</th><th>In play</th><th>Hits</th><th>HR</th><th>Hard hits ≥95 mph</th><th>Mean EV</th><th>xwOBA/contact</th></tr></thead><tbody id="damage"></tbody></table></div><p>Fielder’s choices remain inside a broad outcome group; their actual run impact is pooled rather than treated as automatically zero. Contact and advancement estimates still have uncertainty.</p></div>
<div class="card"><h2>Interpretation and limits</h2><p>Run impact uses observed Statcast <code>delta_run_exp</code>, pooled by count, outs, runners and outcome. Sparse cells borrow information from larger count/outcome and base/out/outcome groups with a fixed smoothing strength of 20. This is an estimated run-value translation, not a newly measured inning run-expectancy matrix.</p><p class="notice">The transition model does not use runners or outs as probability inputs. Base/out context changes the run-impact weights here. Pitch selection and execution are observational; these numbers do not prove causal runs saved or an optimal pitch. Tiny differences should be treated as close options.</p><p>Previous-history averaging uses Miz’s observed 2026 count/handedness frequencies. The baseline pitch mix is normalized over supported candidates at that count. A single supported candidate has ERPA = 0; that is not proof that other pitches are worse.</p><p>The run-value translation’s diagnostic RMSE is 0.21577 versus 0.21579 for a constant baseline on an already-scored postseason sample. This is essentially no demonstrated run-value prediction advantage, and is not a new independent validation.</p><p><a href="count_summary.csv">All count/base/out summaries</a> · <a href="count_candidates.csv.gz">Candidate comparisons and explanations (.csv.gz)</a> · <a href="history_candidates.csv.gz">Exact-history candidate comparisons (.csv.gz)</a> · <a href="history_summary.csv.gz">Exact-history summaries (.csv.gz)</a> · <a href="run_value_weights.csv">Run-impact weights and sample counts</a></p></div>
<script id="data" type="application/json">PAYLOAD</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent), $=id=>document.getElementById(id);
const names={FF:'Four-seam fastball',FC:'Cutter',CU:'Curveball',SL:'Slider',START:'Start of PA'};
const M=new Map(), H=new Map(), S=new Map();
for(const r of D.marginal){const k=r.slice(0,5).join('|');if(!M.has(k))M.set(k,[]);M.get(k).push(r)}
for(const r of D.history){const k=r.slice(0,7).join('|');if(!H.has(k))H.set(k,[]);H.get(k).push(r)}
for(const r of D.sparsity)S.set(r.slice(0,7).join('|'),r[7]);
for(let i=0;i<D.players.length;i++){const o=new Option(D.players[i].batter_name,String(i));$('batter').add(o)}
let balls=0,strikes=0;const signed=x=>(x>=0?'+':'')+x.toFixed(3);
function key(){return [$('batter').value,balls,strikes,$('outs').value,$('bases').value].join('|')}
function historyMenu(){const old=$('history').value; $('history').replaceChildren(new Option('Average over reachable histories','MIX'));
const prefix=key()+'|';for(const k of H.keys()){if(!k.startsWith(prefix))continue;const a=k.split('|');const p=Number(a[5]),r=Number(a[6]);$('history').add(new Option(p===0?'Start of plate appearance':names[D.pitches[p]]+' → '+D.results[r],a.slice(5).join('|')))}
if([...$('history').options].some(o=>o.value===old))$('history').value=old;
}
function cell(row,text,cls){const td=document.createElement('td');td.textContent=text;if(cls)td.className=cls;row.append(td)}
function render(){
for(const button of $('counts').children)button.classList.toggle('active',button.dataset.b==balls && button.dataset.s==strikes);
const mode=$('history').value, mixed=mode==='MIX', k=key(), raw=mixed?M.get(k):H.get(k+'|'+mode);
if(!raw || !raw.length){$('headline').textContent='No supported situation';return}
const rows=raw.map(r=>mixed?{pitch:D.pitches[r[5]],rv:r[6],erpa:r[7],n:r[8],sparse:r[9],parts:r.slice(10,19),p:r.slice(19,28)}:{pitch:D.pitches[r[7]],rv:r[8],erpa:r[9],n:r[10],historySupport:r[11],sparse:S.get(k+'|'+mode),p:r.slice(12,21)}).sort((a,b)=>a.rv-b.rv);
const best=rows[0], reference=best.rv+best.erpa;
$('headline').textContent='#1 '+names[best.pitch]+' · '+signed(best.erpa*100)+' expected runs/100 vs usual mix';
$('context').textContent=D.players[Number($('batter').value)].batter_name+' · '+balls+'–'+strikes+' count · '+$('outs').selectedOptions[0].text+' · '+$('bases').selectedOptions[0].text;
$('baseline').textContent='Usual supported mix: '+reference.toFixed(5)+' batting runs/pitch. Top pitch: '+best.rv.toFixed(5)+'. Lower batting run value favors Miz.';
const gap=rows.length>1?rows[1].rv-best.rv:null;
let note=rows.length===1?'Only one supported candidate; ERPA is zero.':('Modeled lead over #2 '+names[rows[1].pitch]+': '+(gap*100).toFixed(3)+' runs/100. '+(gap<.001?'Small modeled margin: treat the leading pitches as close options.':'Point-estimate ranking; no causal or statistical guarantee for this action difference.'));
if(best.n<20)note+=' Miz has fewer than 20 observations of this pitch in this handedness/count group.';
if(!mixed && best.historySupport<5)note+=' This previous-pitch/count history has only '+best.historySupport+' Miz observations; the model is extrapolating.';
note+=' '+(100*best.sparse).toFixed(1)+'% of the predicted outcome probability uses run-impact cells with fewer than 20 observations.';
$('support').textContent=note;
$('rankings').replaceChildren();rows.forEach((r,i)=>{const tr=document.createElement('tr');if(i===0)tr.className='best';cell(tr,String(i+1));cell(tr,names[r.pitch]+(i===0?' · best modeled':''));cell(tr,r.rv.toFixed(5));cell(tr,signed(r.erpa*100),r.erpa>=0?'good':'bad');cell(tr,((r.rv-best.rv)*100).toFixed(3));cell(tr,r.p.length===9?((r.p[5]+r.p[6]+r.p[7])*100).toFixed(1):'—');cell(tr,r.p.length===9?(r.p[7]*100).toFixed(2):'—');cell(tr,r.p.length===9?(r.p[2]*100).toFixed(1):'—');cell(tr,String(r.n));$('rankings').append(tr)});
$('explanation').hidden=!mixed;$('contributions').replaceChildren();if(mixed){D.outcomes.forEach((label,i)=>{const tr=document.createElement('tr');cell(tr,label);cell(tr,signed(best.parts[i]*100),best.parts[i]>=0?'good':'bad');$('contributions').append(tr)})}
}
for(const r of D.audit){const tr=document.createElement('tr');for(const v of [r.scope,names[r.pitch],r.pitches,r.balls_in_play,r.hits,r.home_runs,r.hard_hits,r.mean_exit_velocity?.toFixed(1)??'—',r.xwoba_on_contact?.toFixed(3)??'—'])cell(tr,String(v));$('damage').append(tr)}$('audit').hidden=D.audit.length===0;
for(let b=0;b<4;b++)for(let s=0;s<3;s++){const button=document.createElement('button');button.textContent=b+'–'+s;button.dataset.b=b;button.dataset.s=s;button.onclick=()=>{balls=b;strikes=s;$('history').value='MIX';historyMenu();render()};$('counts').append(button)}
for(const id of ['batter','outs','bases'])$(id).onchange=()=>{historyMenu();render()};$('history').onchange=render;historyMenu();render();
</script></html>'''
    html=html.replace('HISTORY_COUNT',f"{metrics['history_situations']:,}")
    conditional=metrics.get('probabilities_condition_on_base_outs',False)
    model_metrics=json.loads((RUN/'metrics.json').read_text())
    diagnostic=metrics['diagnostic']
    if conditional:
        html=html.replace('The transition model does not use runners or outs as probability inputs. Base/out context changes the run-impact weights here.',
            'The transition model uses pre-pitch outs and occupancy of each base as probability inputs. Both outcome probabilities and run-impact weights respond to the selected situation.')
        html=html.replace('The run-value translation’s diagnostic RMSE is 0.21577 versus 0.21579 for a constant baseline on an already-scored postseason sample. This is essentially no demonstrated run-value prediction advantage, and is not a new independent validation.',
            f"Retrospective run-value RMSE: {diagnostic['projected_run_value_rmse']:.5f}, versus {diagnostic['training_mean_rmse']:.5f} for a constant baseline. This previously seen postseason sample is a diagnostic, not independent validation. Development folds select the model; action rankings remain unproven.")
        selected=model_metrics['selected']
        damage_note=('The selected probability model includes strictly prior-date pitcher/pitch contact count, observed and expected contact damage, hard-hit rate and recent expected contact damage.'
            if model_metrics.get('damage_selected') else 'Pitch-specific contact-history inputs were tested on chronological development folds but did not improve log loss. The selected model uses runners and outs; the contact audit is descriptive and is not a manual penalty on the cutter.')
        damage_note+=f" Mean development log loss: {selected['mean_loss']:.5f}; original model: {model_metrics['original_development_loss']:.5f}. Lower is better."
        html=html.replace('<p id="damage-model"></p>','<p id="damage-model">'+damage_note+'</p>')
    (OUT/'explorer.html').write_text(html.replace('PAYLOAD',encoded),encoding='utf-8')
    root=summary[(summary.outs==0)&(summary.base_mask==0)]
    lines=['# Every-count matchup and expected runs prevented','','Completed all 12 counts through 3–2 for 14 active Rays hitters and all 24 legal base/out states: **4,032 count situations**. Reachable previous-pitch/result context expands this to **HISTORY_TOTAL history situations**, with **COMPARISON_TOTAL supported candidate comparisons**. Impossible histories, such as a previous strike at 0–0, are excluded.','','Open the [interactive explorer](artifacts/miz_rays_20261023/run_values/explorer.html) to choose the hitter, count, outs, runners, and previous pitch/result. It is self-contained and needs no server.','','## The score','','**ERPA is a project definition: Expected Runs Prevented Above Miz’s usual supported pitch mix.** It is not claimed as an established baseball acronym. The underlying standard concept is pitch run value: the change in run expectancy associated with a pitch.','','For situation s and candidate a:','','```text','ERV(s,a) = sum over outcomes: predicted probability × estimated batting run-expectancy change','ERPA(s,a) = ERV(s, Miz usual supported mix) − ERV(s,a)','ERPA per 100 = 100 × ERPA(s,a)','```','','The target is Statcast `delta_run_exp`, with positive values favoring the batter. A negative expected batting delta favors the pitcher. Positive ERPA means the candidate projects to allow fewer runs than the stated reference mix. This is runs per next pitch; it is neither earned-run average nor the expected total runs in the game.','','The source concept is [Statcast pitch run value](https://baseballsavant.mlb.com/leaderboard/swing-take?group=Pitcher) and the [CSV delta_run_exp definition](https://baseballsavant.mlb.com/csv-docs). The standard run-expectancy accounting is runs scored plus expectancy after minus expectancy before, described in [FanGraphs RE24](https://library.fangraphs.com/misc/re24/). This implementation averages observed pitch delta_RE by outcome/context; it does not reconstruct a new full-inning RE24 table.','','## Baseline, coverage and objective','','The reference is Miz’s observed 2026 pitch frequencies for the batter’s handedness and count, restricted and normalized to supported candidates. It is held the same across previous-pitch histories. The summary averages over reachable prior histories using his observed frequencies; exact-history comparisons are also exported. A single supported pitch has ERPA zero and no runner-up claim.','','All candidates share the same run-value weights at a given count/base/out situation. Their values differ through predicted outcome probabilities. Each comparison includes the runner-up gap, observed pitch support, and the fraction of forecast probability relying on sparse run-impact cells. The expected ERPA of the reference mix itself is exactly zero.','','This ranks **immediate next-pitch run value**, using historical run-expectancy continuation. It differs from the earlier optimized approximate terminal-wOBA sequence objective; recommendations can change. The earlier table is not overwritten.','','## Worked example: Caminero, 0–0, bases empty, no outs','','| Pitch | Expected batting run change | ERPA vs usual mix, runs/pitch | ERPA runs/100 | Miz count/hand sample |','|---|---:|---:|---:|---:|']
    example=candidates[(candidates.batter==691406)&(candidates.balls==0)&(candidates.strikes==0)&(candidates.outs==0)&(candidates.base_mask==0)].sort_values('expected_batting_run_delta')
    for r in example.itertuples():lines.append(f'| {r.candidate_pitch} | {r.expected_batting_run_delta:+.5f} | {r.erpa_runs_per_pitch:+.5f} | {r.erpa_runs_per_100:+.3f} | {r.miz_count_pitch_support} |')
    first=example.iloc[0]
    lines+=['',f"The usual supported mix projects {first.usual_mix_batting_run_delta:+.5f} batting runs/pitch here. The leading candidate projects {first.expected_batting_run_delta:+.5f}, a difference of {first.erpa_runs_per_pitch:+.5f} runs/pitch. The per-100 number is a rescaling across equivalent situations, not guaranteed runs saved in this game.",'','## Every count: bases empty, no outs','','Each cell shows the top point-estimate pitch and ERPA runs/100 versus the supported usual mix. These are history-averaged summaries, not a fixed pitch order. All other runner/out contexts and exact histories are in the explorer and CSVs.','','| Hitter | '+' | '.join(f'{b}–{s}' for b,s in COUNTS)+' |','|---|'+'---:|'*12]
    for person in players:
        part=root[root.batter==person['batter']].set_index(['balls','strikes'])
        lines.append('| '+person['batter_name']+' | '+' | '.join(f"{part.loc[(b,s),'best_pitch']} ({part.loc[(b,s),'best_erpa_runs_per_100']:+.2f})" for b,s in COUNTS)+' |')
    d=metrics['diagnostic']
    lines+=['','FF = four-seam fastball; FC = cutter; CU = curveball; SL = slider. A +0.00 cell can reflect a single supported candidate; consult candidate_count before treating that as evidence.','','## Limits and diagnostic','','Run-impact means are estimated from the acquired 2025–26 matchup cohort, using a fixed smoothing pseudo-count of 20. Sparse full cells borrow from larger count/outcome and base/out/outcome groups. Unobserved cells retain full_cell_n = 0 rather than invented sample support. This is not a complete league RE288 estimate.','','The frozen transition model does not include runners or outs as prediction inputs. Those states affect the run-value translation here; they do not change the predicted outcome probabilities. Baserunning and execution can also affect the observed delta_RE within an outcome group. Location intent, catcher calls, adaptation, and selection effects are not causally controlled.','',f"A diagnostic on the previously scored postseason set gives run-value RMSE {d['projected_run_value_rmse']:.5f}, versus {d['training_mean_rmse']:.5f} for a constant mean. This is essentially no established advantage in predicting realized run value. The sample was already used, so this is not new independent validation and was not used for tuning.",'','The outcome model’s predictive evidence does not validate these action-level differences or policy improvements. No causal confidence interval is claimed. Tiny runner-up gaps and low candidate support should remain close options, not instructions. Do not sum ERPA across mutually exclusive scenarios.','','## Files and reproduction','','```bash','.venv/bin/python src/score_erpa.py','.venv/bin/python src/build_erpa_report.py','```','','- [Interactive explorer](artifacts/miz_rays_20261023/run_values/explorer.html)','- [4,032 count/base/out summaries](artifacts/miz_rays_20261023/run_values/count_summary.csv)','- [Candidate values and outcome contributions](artifacts/miz_rays_20261023/run_values/count_candidates.csv.gz)','- [Reachable-history candidate values](artifacts/miz_rays_20261023/run_values/history_candidates.csv.gz)','- [Reachable-history summaries](artifacts/miz_rays_20261023/run_values/history_summary.csv.gz)','- [Run-impact means and actual support counts](artifacts/miz_rays_20261023/run_values/run_value_weights.csv)']
    text='\n'.join(lines).replace('HISTORY_TOTAL',f"{metrics['history_situations']:,}").replace('COMPARISON_TOTAL',f"{metrics['history_candidate_comparisons']:,}")
    if conditional:
        text=text.replace('The frozen transition model does not include runners or outs as prediction inputs. Those states affect the run-value translation here; they do not change the predicted outcome probabilities.',
            'The version 2 transition model uses outs and occupancy of first, second and third as pre-pitch probability inputs. These states change predicted outcome probabilities as well as the run-value translation.')
        text=text.replace('This is essentially no established advantage in predicting realized run value.',
            'This retrospective diagnostic does not establish action-ranking accuracy or causal runs saved.')
        text=text.replace('The earlier table is not overwritten.', 'The original model and outputs are preserved in the original run directory.')
        text=text.replace('artifacts/miz_rays_20261023/',str(RUN.relative_to(ROOT))+'/')
        text+='\n\n## Contact history and development comparison\n\n'+damage_note+'\n\nSee [pitch contact audit]('+str((RUN/'PITCH_DAMAGE_AUDIT.md').relative_to(ROOT))+').\n'
        text=text.replace('.venv/bin/python src/score_erpa.py',f'MATCHUP_RUN={RUN.relative_to(ROOT)} .venv/bin/python src/score_erpa.py')
        text=text.replace('.venv/bin/python src/build_erpa_report.py',f'MATCHUP_RUN={RUN.relative_to(ROOT)} .venv/bin/python src/build_erpa_report.py')
        snapshot=text.replace(str(RUN.relative_to(ROOT))+'/', '')
        (RUN/'ERPA_MATCHUP.md').write_text(snapshot+'\n')
    (ROOT/'ERPA_MATCHUP.md').write_text(text+'\n')
    print('Explorer:',OUT/'explorer.html','bytes:',(OUT/'explorer.html').stat().st_size)


if __name__=='__main__':
    main()
