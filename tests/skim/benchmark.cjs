// CPU work in the real animation tick. Canvas calls and DOM writes are no-ops;
// this is not a browser FPS or GPU benchmark. Alternate order to limit bias.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {performance}=require('node:perf_hooks');
const {loadEngine}=require('./probe.cjs');
const files={buoy:path.join(__dirname,'buoy.html'),skim:path.resolve(__dirname,'../../skim.html')};
const cases=[
 {name:'default transitions',count:12,fields:.55,moving:true},
 {name:'dense transitions',count:24,fields:1,moving:true},
 {name:'settled sidebar',count:12,fields:0,moving:false}
];
const median=a=>[...a].sort((a,b)=>a-b)[Math.floor(a.length/2)];
const percentile=(a,p)=>[...a].sort((a,b)=>a-b)[Math.floor((a.length-1)*p)];
function workload(e,capture,moving){
 const durations=[];let ms=1000;
 if(!moving){e.scene('sidebar');for(let f=0;f<600;f++){e.advance(ms);ms+=1000/60;}}
 const t=performance.now();
 for(let f=0;f<1600;f++){
  // Include the actual scene-change work in the total, as well as frames.
  if(moving){
   const scene={200:'frame',500:'sidebar',800:'hero',1100:'sidebar',1350:'flock'}[f];
   if(scene)e.scene(scene);
   if(f===450||f===740)e.pointer(350,350);
   if(f===490||f===790)e.pointer(-1e9,-1e9);
  }
  const start=capture?performance.now():0;e.advance(ms);ms+=1000/60;
  if(capture)durations.push(performance.now()-start);
 }
 return{totalMs:performance.now()-t,meanFrameMs:durations.reduce((a,b)=>a+b,0)/1600,p95FrameMs:percentile(durations,.95),p99FrameMs:percentile(durations,.99)};
}
const rows=[];
for(const cfg of cases){
 for(let w=0;w<2;w++)for(const name of ['buoy','skim'])workload(loadEngine(files[name],cfg),false,cfg.moving);
 const samples={buoy:[],skim:[]};
 for(let rep=0;rep<5;rep++)for(const name of rep%2?['skim','buoy']:['buoy','skim'])samples[name].push(workload(loadEngine(files[name],cfg),true,cfg.moving));
 const medians=Object.fromEntries(Object.entries(samples).map(([name,r])=>[name,Object.fromEntries(Object.keys(r[0]).map(k=>[k,median(r.map(x=>x[k]))]))]));
 const row={...cfg,framesPerRun:1600,repeats:5,medians,reductionPct:100*(1-medians.skim.totalMs/medians.buoy.totalMs),samples};
 rows.push(row);console.log(JSON.stringify({name:cfg.name,medians,reductionPct:row.reductionPct}));
}
const result={scope:'Full tick JavaScript CPU computation; native Canvas, GPU, browser layout and compositor excluded. Includes diagnostic cadence, content anchors and hover. Median of five alternating-order paired runs after two warmups per mark/workload. No instrumentation wrappers.',runtime:process.version,cpu:os.cpus()[0]?.model,platform:process.platform,rows};
fs.writeFileSync(path.join(__dirname,'benchmark.json'),JSON.stringify(result,null,2)+'\n');
