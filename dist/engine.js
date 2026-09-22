(function(root) {
  'use strict';
  function score(model, values) {
    if (!Array.isArray(values) || values.length !== model.features.length || values.some(v => !Number.isFinite(v) || v < 0)) {
      throw new Error('Enter a non-negative number for every model input.');
    }
    if (model.kind === 'logistic') {
      const z = model.intercept + values.reduce((sum,v,i) => sum + ((Math.log1p(v)-model.mean[i])/model.scale[i])*model.coefficients[i],0);
      return 1/(1+Math.exp(-z));
    }
    if (model.kind !== 'forest') throw new Error('Unsupported model.');
    return model.trees.reduce((sum,t) => {
      let n=0;
      while(t.left[n] !== -1) n = Math.fround(values[t.feature[n]]) <= t.threshold[n] ? t.left[n] : t.right[n];
      return sum+t.p[n];
    },0)/model.trees.length;
  }
  function evaluate(rows, threshold) {
    if (!Number.isFinite(threshold) || threshold<0 || threshold>1) throw new Error('Threshold must be between 0 and 1.');
    let tp=0,fp=0,tn=0,fn=0;
    rows.forEach(r => {if(r.score>=threshold) r.y ? tp++ : fp++; else r.y ? fn++ : tn++;});
    return {tp,fp,tn,fn,precision:tp+fp ? tp/(tp+fp):null,recall:tp+fn ? tp/(tp+fn):null,
      flagged:tp+fp,n:rows.length};
  }
  function validate(values, data) {
    if (!Array.isArray(values) || values.length !== data.model.features.length) throw new Error('Provide all nine inputs.');
    values.forEach((v,i) => {
      const f=data.model.features[i], b=data.bounds[f];
      if(!Number.isFinite(v) || !Number.isInteger(v) || v<b.min || v>b.max) throw new Error(`${data.labels[i]} must be a whole number from ${b.min} to ${b.max}.`);
    });
    return values;
  }
  const api={score,evaluate,validate};
  if(typeof module!=='undefined') module.exports=api;
  root.ChurnEngine=api;
})(typeof globalThis!=='undefined' ? globalThis : this);
