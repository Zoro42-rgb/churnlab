const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const E=require(path.join(root,'dist/engine.js'));
const context={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(root,'dist/data.js'),'utf8'),context);
const data=JSON.parse(JSON.stringify(context.window.CHURNLAB));
for(const row of [...data.examples,...data.validation_rows]){
 const actual=E.score(data.model,row.values);
 assert.ok(Math.abs(actual-(row.expected??row.score))<1e-10,`Python/browser scoring mismatch for ${row.id}`);
}
const computed=E.evaluate(data.validation_rows,data.threshold);
for(const key of ['tp','fp','tn','fn','flagged']) assert.equal(computed[key],data.validation[key],key);
assert.throws(()=>E.score(data.model,[NaN]));
assert.throws(()=>E.evaluate([],2));
assert.throws(()=>E.validate(Array(9).fill(-1),data));
const none=E.evaluate([{y:1,score:.1}],.9);
assert.equal(none.precision,null);assert.equal(none.recall,0);
console.log(`PASS: ${data.examples.length+data.validation_rows.length} Python/JavaScript prediction parity checks, metric reconciliation, and invalid-input checks.`);
