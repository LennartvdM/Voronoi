// Attribution only: wrappers add overhead. Use benchmark.cjs for speed claims.
const fs=require('node:fs'),path=require('node:path');
const {loadEngine,run}=require('./probe.cjs');
const result=[];
for(const [count,fields] of [[12,.55],[24,1]]) for(const name of ['buoy','skim']) {
 const file=name==='buoy'?path.join(__dirname,'buoy.html'):path.resolve(__dirname,'../../skim.html');
 const e=loadEngine(file,{count,fields,profile:true});run(e);
 result.push({name,count,fields,frames:1600,stats:e.stats});
}
fs.writeFileSync(path.join(__dirname,'profile.json'),JSON.stringify(result,null,2)+'\n');
console.log('Saved instrumented attribution to profile.json');
