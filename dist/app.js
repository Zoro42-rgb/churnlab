'use strict';
(() => {
 const D=window.CHURNLAB, E=window.ChurnEngine, $=id=>document.getElementById(id);
 if(!D || !E || !window.d3){$('fatal').hidden=false;$('fatal').textContent='A required project file did not load. Keep all files in the dist folder together and reopen index.html.';return;}
 const pct=n=>n===null?'—':`${(n*100).toFixed(1)}%`;
 let threshold=D.threshold;
 const rows=D.validation_rows;
 $('threshold').value=Math.round(threshold*100);
 $('validation-context').textContent=`${rows.length} validation profiles · ${rows.filter(r=>r.y).length} actual churners · ${D.selected_model}`;
 function setView(name){
   if(!['decision','score','evidence'].includes(name))throw new Error('Unknown view.');
   document.querySelectorAll('.view').forEach(el=>el.hidden=el.id!==name);
   document.querySelectorAll('[data-view]').forEach(el=>{el.classList.toggle('active',el.dataset.view===name);el.setAttribute('aria-pressed',String(el.dataset.view===name));});
   $('breadcrumb').textContent={decision:'Decision lab',score:'Score a customer',evidence:'Model evidence'}[name];
 }
 document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view)));
 function renderChart(){
   const svg=d3.select('#tradeoff');svg.selectAll('*').remove();
   const x=d3.scaleLinear().domain([0,1]).range([44,681]), y=d3.scaleLinear().domain([0,1]).range([218,15]);
   const points=d3.range(.01,1,.01).map(t=>({t,...E.evaluate(rows,t)}));
   svg.append('g').attr('transform','translate(44,0)').call(d3.axisLeft(y).ticks(4).tickFormat(d3.format('.0%')).tickSize(-637)).call(g=>g.select('.domain').remove()).call(g=>g.selectAll('.tick line').attr('stroke','#e9eef5'));
   svg.append('g').attr('transform','translate(0,218)').call(d3.axisBottom(x).ticks(5).tickFormat(d3.format('.0%')).tickSize(0)).call(g=>g.selectAll('text').attr('dy','1.4em'));
   for(const [key,color] of [['recall','#275edc'],['precision','#07857a']]){
    svg.append('path').datum(points).attr('fill','none').attr('stroke',color).attr('stroke-width',2.6)
      .attr('d',d3.line().defined(d=>d[key]!==null).x(d=>x(d.t)).y(d=>y(d[key])));
   }
   svg.append('line').attr('id','threshold-line').attr('y1',12).attr('y2',218).attr('stroke','#596a80').attr('stroke-dasharray','4 4');
   svg.append('text').attr('x',363).attr('y',256).attr('text-anchor','middle').text('Model score threshold');
 }
 function filteredRows(){const tariff=$('tariff-filter').value;return rows.filter(r=>tariff==='all'||String(r.tariff)===tariff).slice().sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id));}
 function renderTable(){
   const current=filteredRows();
   $('priority-rows').innerHTML=current.slice(0,8).map(r=>`<tr><td>${r.id}</td><td>${r.tariff===1?'Pay-as-you-go':'Contractual'}</td><td>${r.complains?'Yes':'No'}</td><td class="row-score">${pct(r.score)}</td><td><span class="pill ${r.score>=threshold?'flag':''}">${r.score>=threshold?'Flagged':'Not flagged'}</span></td><td><span class="pill ${r.y?'yes':''}">${r.y?'Churned':'Stayed'}</span></td></tr>`).join('');
   $('table-note').textContent=`Showing ${Math.min(8,current.length)} of ${current.length} profiles in this tariff filter. Export includes all ${current.filter(r=>r.score>=threshold).length} flagged profiles in this filter. Summary cards use the full validation cohort.`;
 }
 function updateThreshold(value){
   if(!Number.isFinite(value)||value<.01||value>.99)throw new Error('Choose a threshold between 0.01 and 0.99.');
   threshold=value;$('threshold').value=Math.round(value*100);$('threshold-value').textContent=value.toFixed(2);
   const m=E.evaluate(rows,value);
   $('recall').textContent=pct(m.recall);$('precision').textContent=pct(m.precision);$('flagged').textContent=m.flagged;$('missed').textContent=m.fn;
   $('recall-detail').textContent=`${m.tp} of ${m.tp+m.fn} actual churners`;
   $('precision-detail').textContent=m.flagged?`${m.tp} correct flags out of ${m.flagged}`:'No customers flagged at this threshold';
   $('flagged-detail').textContent=`${pct(m.flagged/m.n)} of validation customers`;
   ['tp','fp','tn','fn'].forEach(k=>$(k).textContent=m[k]);
   const x=44+637*value;d3.select('#threshold-line').attr('x1',x).attr('x2',x);
   renderTable();if($('profile-score').textContent!=='—') scoreProfile(false);
   return m;
 }
 $('threshold').addEventListener('input',e=>updateThreshold(Number(e.target.value)/100));
 $('reset').addEventListener('click',()=>updateThreshold(D.threshold));
 $('tariff-filter').addEventListener('change',renderTable);
 $('export').addEventListener('click',()=>{
   const lines=['record_id,tariff_plan,complaint_indicator,model_score,threshold,actual_churn',...filteredRows().filter(r=>r.score>=threshold).map(r=>[r.id,r.tariff,r.complains,r.score.toFixed(6),threshold.toFixed(2),r.y].join(','))];
   const url=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/csv'}));const a=document.createElement('a');a.href=url;a.download='churnlab-validation-flags.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 });
 // Model evidence is immutable after training, independent of the interactive threshold.
 $('test-ap').textContent=D.test.average_precision.toFixed(3);$('test-recall').textContent=pct(D.test.recall);$('test-precision').textContent=pct(D.test.precision);$('test-lift').textContent=`${D.test.top10_lift.toFixed(2)}×`;
 $('test-threshold').textContent=`Fixed threshold ${D.threshold.toFixed(2)} · ${D.test.n} test profiles`;
 $('comparison').innerHTML=D.comparison.map(m=>`<tr><td>${m.name}${m.name===D.selected_model?' <span class="pill">Selected</span>':''}</td><td>${m.average_precision.toFixed(3)}</td><td>${pct(m.recall)}</td><td>${pct(m.precision)}</td></tr>`).join('');
 $('selection-note').textContent=`${D.selected_model} selected by validation average precision. Threshold ${D.threshold.toFixed(2)} selected by validation F2, which emphasizes recall. Dummy-baseline precision is reported as zero when it flags nobody.`;
 $('split-bars').innerHTML=Object.entries(D.splits).map(([k,v])=>`<div class="split-row"><span>${k[0].toUpperCase()+k.slice(1)}</span><div><i style="width:${100*v.n/D.rows}%"></i></div><span>${v.n}</span></div>`).join('');
 $('quality-note').textContent=`${D.missing_cells} missing cells · ${D.raw_duplicate_rows} repeated full rows retained · ${D.repeated_feature_rows} repeated input profiles grouped · no input-profile overlap between splits. Record IDs are generated references, not source customer IDs.`;
 const maximum=Math.max(...D.importance.map(r=>r.importance),.001);
 $('importance').innerHTML=D.importance.slice(0,6).map(r=>`<div class="importance-row"><div class="importance-label"><span>${r.label}</span><span>${r.importance.toFixed(3)}</span></div><div class="importance-track"><div style="width:${Math.max(0,100*r.importance/maximum)}%"></div></div></div>`).join('');
 const observed=rows.slice().sort((a,b)=>a.score-b.score);
 const presets=[observed[Math.floor(observed.length*.1)],observed[Math.floor(observed.length*.5)],observed[Math.floor(observed.length*.95)]];
 $('example').innerHTML=presets.map((r,i)=>`<option value="${i}">${['Lower-scoring','Middle-scoring','Higher-scoring'][i]} profile · ${r.id}</option>`).join('');
 $('input-fields').innerHTML=D.model.features.map((f,i)=>`<label for="f-${f}">${D.labels[i]}<input id="f-${f}" name="${f}" type="number" step="1" min="${D.bounds[f].min}" max="${D.bounds[f].max}" required><small>Observed range ${D.bounds[f].min.toLocaleString()}–${D.bounds[f].max.toLocaleString()}</small></label>`).join('');
 function scoreProfile(showError=true){
   try{
     const values=D.model.features.map(f=>{const s=$('f-'+f).value;return s.trim()===''?NaN:Number(s);});E.validate(values,D);
     const p=E.score(D.model,values);$('profile-score').textContent=pct(p);$('score-fill').style.width=`${p*100}%`;
     $('profile-decision').textContent=p>=threshold?'Flagged at the current threshold':'Below the current threshold';
     $('profile-threshold').textContent=`Threshold ${threshold.toFixed(2)} · ${D.selected_model}`;
     $('input-error').textContent='';return {score:p,threshold,flagged:p>=threshold};
   }catch(err){if(showError)$('input-error').textContent=err.message;return null;}
 }
 function loadPreset(){const r=presets[Number($('example').value)];D.model.features.forEach((f,i)=>$('f-'+f).value=r.values[i]);scoreProfile();}
 $('example').addEventListener('change',loadPreset);
 $('score-form').addEventListener('submit',e=>{e.preventDefault();scoreProfile();});
 // Make changes explicit: edited values invalidate the previous displayed score.
 $('score-form').addEventListener('input',()=>{$('profile-score').textContent='—';$('profile-decision').textContent='Inputs changed. Calculate the updated score.';$('score-fill').style.width='0';$('profile-threshold').textContent='';$('input-error').textContent='';});
 renderChart();updateThreshold(D.threshold);loadPreset();
 if(document.modelContext?.registerTool){
   const lifecycle=new AbortController();window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});
   const register=tool=>{try{Promise.resolve(document.modelContext.registerTool(tool,{signal:lifecycle.signal})).catch(()=>{});}catch{}};
   register({name:'set_churn_threshold',description:'Set the validation decision threshold and update visible metrics. Does not change locked test results.',inputSchema:{type:'object',properties:{threshold:{type:'number',minimum:.01,maximum:.99}},required:['threshold'],additionalProperties:false},annotations:{readOnlyHint:false},execute:input=>{if(!input||typeof input.threshold!=='number')throw new Error('A numeric threshold is required.');const result=updateThreshold(input.threshold);setView('decision');return result;}});
   register({name:'score_churn_profile',description:'Score a profile using nine observed-window inputs; show the result in the customer scoring view. Nothing is stored.',inputSchema:{type:'object',properties:{values:{type:'array',items:{type:'integer'},minItems:9,maxItems:9,description:D.labels.join(', ')}},required:['values'],additionalProperties:false},annotations:{readOnlyHint:false},execute:input=>{E.validate(input?.values,D);D.model.features.forEach((f,i)=>$('f-'+f).value=input.values[i]);const result=scoreProfile();setView('score');return result;}});
 }
})();
