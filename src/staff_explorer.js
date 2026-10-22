'use strict';
const D=JSON.parse(document.getElementById('meta').textContent),$=id=>document.getElementById(id);
const names=D.pitch_names,labels={ball:'Ball',strike:'Called / other strike',whiff:'Swinging miss',foul:'Foul',out:'In-play out / choice',single:'Single / error',extra_base:'Double / triple',home_run:'Home run',hbp:'Hit by pitch'};
let M=new Map(),H=new Map(),menus=new Map(),active=null,balls=0,strikes=0,rows=[],loadId=0;
const signed=(n,d=3)=>(n>=0?'+':'')+n.toFixed(d),pitchName=p=>names[p]||p;
function cell(row,value,cls){const td=document.createElement('td');td.textContent=value;if(cls)td.className=cls;row.append(td);return td}
function key(){return [$('batter').value,balls,strikes,$('outs').value,$('bases').value].join('|')}
function decoded(r,exact){return exact?{pitch:D.pitches[r[7]],rv:r[8],erp:-r[8],improvement:r[9],n:r[10],history:r[11],sparse:r[12],p:r.slice(13,22),fallback:r[22]}:{pitch:D.pitches[r[5]],rv:r[6],erp:-r[6],improvement:r[7],n:r[8],sparse:r[9],p:r.slice(10,19),fallback:r[19]}}
function historyMenu(){const old=$('history').value;$('history').replaceChildren(new Option('Average over reachable histories','MIX'));for(const suffix of menus.get(key())||[]){const [p,r]=suffix.split('|').map(Number);$('history').add(new Option(p===0?'Start of plate appearance':pitchName(D.pitches[p])+' → '+D.results[r],suffix))}if([...$('history').options].some(o=>o.value===old))$('history').value=old}
function explain(){
 const row=rows.find(r=>r.pitch===$('explain-pitch').value)||rows[0];if(!row)return;
 const total=rows.reduce((sum,r)=>sum+r.n,0),mix=rows.map(r=>total?r.n/total:1/rows.length);
 const referenceP=D.outcomes.map((_,j)=>rows.reduce((sum,r,i)=>sum+mix[i]*r.p[j],0));
 const w=D.weights[[balls,strikes,$('outs').value,$('bases').value].join('|')];
 const reference=row.rv+row.improvement;
 $('calculation').textContent=pitchName(row.pitch)+': ERP = −('+signed(row.rv,6)+' expected batting run change) = '+signed(row.erp,6)+' runs/pitch ('+signed(100*row.erp)+' runs/100). Usual-mix ERP: '+signed(-reference,6)+' runs/pitch. Improvement over usual mix: '+signed(row.improvement*100)+' runs/100.';
 $('contributions').replaceChildren();let sum=0;
 D.outcomes.forEach((label,j)=>{const contribution=-row.p[j]*w[j],improvement=(referenceP[j]-row.p[j])*w[j];sum+=contribution;const tr=document.createElement('tr');cell(tr,labels[label]);cell(tr,(100*referenceP[j]).toFixed(2)+'%','num');cell(tr,(100*row.p[j]).toFixed(2)+'%','num');cell(tr,signed(w[j],5),'num');cell(tr,signed(contribution*100),contribution>=0?'good num':'bad num');cell(tr,signed(improvement*100),improvement>=0?'good num':'bad num');$('contributions').append(tr)});
 $('contribution-total').textContent=signed(sum*100)+' runs/100';
}
function render(){
 if(!active)return;for(const button of $('counts').children)button.classList.toggle('active',Number(button.dataset.b)===balls&&Number(button.dataset.s)===strikes);
 const mode=$('history').value,exact=mode!=='MIX';const raw=exact?H.get(key()+'|'+mode):M.get(key());
 if(!raw?.length){$('headline').textContent='No supported candidates for this history';$('rankings').replaceChildren();return}
 rows=raw.map(r=>decoded(r,exact)).sort((a,b)=>a.rv-b.rv);
 const best=rows[0],person=D.pitchers.find(p=>String(p.id)===$('pitcher').value),batter=D.batters[Number($('batter').value)];
 const side=batter.bat_side==='S'?(person.throws==='R'?'L':'R'):batter.bat_side;
 const gap=rows.length>1?rows[1].rv-best.rv:null,reference=best.rv+best.improvement;
 $('headline').textContent='#1 '+pitchName(best.pitch)+' · '+signed(best.erp*100)+' ERP runs/100';
 $('context').textContent=person.name+' ('+person.throws+'HP) vs '+batter.name+' (bats '+side+') · '+balls+'–'+strikes+' · '+$('outs').selectedOptions[0].text+' · '+$('bases').selectedOptions[0].text;
 $('baseline').textContent='ERP is the expected reduction in batting run expectancy on this pitch. Usual supported mix: '+signed(-reference*100)+' ERP runs/100. Leading pitch: '+signed(best.erp*100)+'. Improvement over that mix: '+signed(best.improvement*100)+' runs/100. Higher ERP favors the pitcher.';
 let note=gap===null?'One supported candidate: ERP can be nonzero, but improvement over usual mix is zero and no alternative comparison is available.':'Modeled lead over #2 '+pitchName(rows[1].pitch)+': '+(100*gap).toFixed(3)+' runs/100. '+(gap<.001?'Close options; the model does not clearly separate them.':'Point-estimate preference, not a statistical guarantee.');
 if(best.erp<0)note+=' Even the leading pitch projects an increase in batting run expectancy here; it is the smallest increase among supported choices.';
 if(best.fallback)note+=' Count support fallback: no pitch passed the five-pitch count/hand gate.';
 if(best.n<20)note+=' Fewer than 20 observations for this pitch/count/side.';
 if(exact&&best.history<5)note+=' Only '+best.history+' observations of this pitcher/count/side/history; the forecast extrapolates.';
 note+=' '+(best.sparse*100).toFixed(1)+'% of predicted outcome probability uses run-impact cells with fewer than 20 direct observations.';
 $('support').textContent=note;
 const total=rows.reduce((n,r)=>n+r.n,0);$('rankings').replaceChildren();
 rows.forEach((r,i)=>{const tr=document.createElement('tr');if(i===0)tr.className='best';cell(tr,String(i+1));cell(tr,pitchName(r.pitch)+(i===0?' · best modeled':''));cell(tr,signed(r.erp*100),r.erp>=0?'good num':'bad num');cell(tr,signed(r.improvement*100),r.improvement>=0?'good num':'bad num');cell(tr,((r.rv-best.rv)*100).toFixed(3),'num');cell(tr,((r.p[5]+r.p[6]+r.p[7])*100).toFixed(1),'num');cell(tr,(r.p[7]*100).toFixed(2),'num');cell(tr,(r.p[2]*100).toFixed(1),'num');cell(tr,String(r.n),'num');cell(tr,(100*(total?r.n/total:1/rows.length)).toFixed(1),'num');$('rankings').append(tr)});
 const old=$('explain-pitch').value;$('explain-pitch').replaceChildren(...rows.map(r=>new Option(pitchName(r.pitch),r.pitch)));if(rows.some(r=>r.pitch===old))$('explain-pitch').value=old;explain();
}
function overview(){
 $('overview').replaceChildren();const person=D.pitchers.find(p=>String(p.id)===$('pitcher').value);
 D.batters.forEach((b,i)=>{const tr=document.createElement('tr'),td=cell(tr,'');const button=document.createElement('button');button.textContent=b.name;button.onclick=()=>{$('batter').value=String(i);balls=0;strikes=0;$('outs').value='0';$('bases').value='0';$('history').value='MIX';historyMenu();render();$('headline').scrollIntoView({behavior:'smooth',block:'center'})};td.append(button);cell(tr,b.bat_side==='S'?(person.throws==='R'?'L':'R'):b.bat_side);for(const [balls,strikes] of [[0,0],[0,2],[3,2]]){const rr=M.get([i,balls,strikes,0,0].join('|')).map(r=>decoded(r,false)).sort((a,b)=>a.rv-b.rv);cell(tr,rr[0].pitch+' ('+signed(rr[0].erp*100,2)+')')} $('overview').append(tr)})
}
async function loadPitcher(){
 const token=++loadId,id=$('pitcher').value,person=D.pitchers.find(p=>String(p.id)===id);
 $('status').hidden=false;$('status').textContent='Loading '+person.name+'’s matchup probabilities…';$('analysis').hidden=true;
 try{
  if(location.protocol==='file:')throw new Error('Open http://localhost:8765/explorer.html in a browser while the local preview server is running. This staff explorer loads one pitcher at a time and needs HTTP.');
  let response,payload;if(typeof DecompressionStream==='function'){response=await fetch('data/'+id+'.json.gz');if(!response.ok)throw new Error('Pitcher data request failed: '+response.status);payload=await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json()}else{response=await fetch('data/'+id+'.json');if(!response.ok)throw new Error('Pitcher data request failed: '+response.status);payload=await response.json()}
  if(token!==loadId)return;M=new Map();H=new Map();menus=new Map();active=payload;
  for(const r of payload.marginal){const k=r.slice(0,5).join('|');if(!M.has(k))M.set(k,[]);M.get(k).push(r)}
  for(const r of payload.history){const prefix=r.slice(0,5).join('|'),suffix=r.slice(5,7).join('|'),k=prefix+'|'+suffix;if(!H.has(k)){H.set(k,[]);if(!menus.has(prefix))menus.set(prefix,[]);menus.get(prefix).push(suffix)}H.get(k).push(r)}
  $('pitcher-profile').textContent=person.name+' · '+person.throws+'HP · '+person.season_pitches.toLocaleString()+' source-season pitches';
  $('repertoire').textContent='Supported arsenal across batting sides: '+person.repertoire.map(pitchName).join(', ')+'.';
  const diagnostic=D.metrics.per_pitcher.find(p=>String(p.id)===id);
  const diagnosticText=diagnostic.diagnostic_rows?' October outcome log loss: '+diagnostic.diagnostic_log_loss.toFixed(4)+' vs contextual baseline '+diagnostic.context_log_loss.toFixed(4)+' (lower is better).'+(diagnostic.diagnostic_log_loss>=diagnostic.context_log_loss?' The model did not beat that baseline on this pitcher’s small diagnostic sample.':''):' No October observations are available for this pitcher’s diagnostic.';
  $('availability').textContent='Last recorded appearance: '+person.last_appearance+'. Latest four outings: '+person.recent_pitches+' pitches. These records do not establish today’s health, rest or game availability. This pitcher’s retrospective October diagnostic has '+diagnostic.diagnostic_rows+' pitches in '+diagnostic.diagnostic_games+' games; this is not independent validation.'+diagnosticText;
  const unique=new Map();for(const e of person.excluded_pitch_hand_pairs)unique.set(e.stand+'|'+e.pitch,e);$('exclusions').replaceChildren();for(const e of unique.values()){const tr=document.createElement('tr');for(const v of [e.stand,pitchName(e.pitch),e.season_n,e.hand_n,e.recent_n])cell(tr,String(v));$('exclusions').append(tr)}
  $('downloads').replaceChildren();for(const [label,file] of [['Count summaries','count_summary.csv'],['All ranked count candidates','count_candidates.csv.gz'],['Exact-history comparisons','history_candidates.csv.gz']]){const a=document.createElement('a');a.textContent=label;a.href='pitchers/'+id+'/'+file;$('downloads').append(a,document.createTextNode(' · '))}
  $('history').value='MIX';historyMenu();overview();render();$('status').hidden=true;$('analysis').hidden=false;
 }catch(error){if(token===loadId){active=null;$('status').textContent=error.message}}
}
for(const p of D.pitchers)$('pitcher').add(new Option(p.name+' · '+p.throws+'HP',String(p.id)));
for(let i=0;i<D.batters.length;i++)$('batter').add(new Option(D.batters[i].name,String(i)));
for(let b=0;b<4;b++)for(let s=0;s<3;s++){const button=document.createElement('button');button.textContent=b+'–'+s;button.dataset.b=b;button.dataset.s=s;button.onclick=()=>{balls=b;strikes=s;$('history').value='MIX';historyMenu();render()};$('counts').append(button)}
$('scope').textContent=D.pitchers.length+' pitchers × '+D.batters.length+' hitters × 12 counts × 24 runner/out states = '+D.count_situations.toLocaleString()+' count situations, plus '+D.history_situations.toLocaleString()+' exact-history situations. Source cutoff: '+D.as_of+'.';
const diagnostic=D.metrics.retrospective_diagnostic;
$('evidence').textContent='Selected shared model: '+D.metrics.selected.name+'. Mean chronological development log loss: '+D.metrics.selected.mean_log_loss.toFixed(5)+'. October is an already-seen retrospective diagnostic, not independent validation: outcome log loss '+diagnostic.log_loss.toFixed(5)+' vs contextual baseline '+diagnostic.context_log_loss.toFixed(5)+'; run-value RMSE '+diagnostic.run_value_rmse.toFixed(5)+' vs constant '+diagnostic.constant_run_value_rmse.toFixed(5)+'. Action rankings have not been causally validated.';
$('pitcher').onchange=loadPitcher;for(const id of ['batter','outs','bases'])$(id).onchange=()=>{if(active){historyMenu();render()}};$('history').onchange=render;$('explain-pitch').onchange=explain;
const requested=new URLSearchParams(location.search).get('pitcher');if(D.pitchers.some(p=>String(p.id)===requested))$('pitcher').value=requested;else $('pitcher').value='694819';loadPitcher();
