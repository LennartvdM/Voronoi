/* Test the exact comparison bytes via intercepted requests, not a fake live deployment. */
const fs=require('fs'),path=require('path');const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package');
(async()=>{const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:process.env.PLAYWRIGHT_MODULE?{}:{executablePath:'/usr/bin/chromium'}),args:['--no-sandbox']}),p=await browser.newPage({viewport:{width:1600,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.evaluate(sources=>{window.fetch=async url=>({ok:!!sources[url],status:sources[url]?200:404,text:async()=>sources[url]});},Object.fromEntries(['astra-i.html','astra-iii.html'].map(f=>[f,fs.readFileSync(f,'utf8')])));
 await p.setContent(fs.readFileSync('astra-iii-compare.html','utf8'));await p.waitForFunction(()=>!document.querySelector('#step').disabled,null,{timeout:120000});
 await p.selectOption('#dt','4.166666666666667');await p.waitForFunction(()=>!document.querySelector('#step').disabled,null,{timeout:120000});
 await p.selectOption('#scene','hero');await p.click('#change');await p.click('#step');
 const first=await p.locator('#status').textContent();if(!first.includes('4.17 ms'))throw Error(first);
 const dimensions=await p.evaluate(()=>[...document.querySelectorAll('iframe')].map(f=>({width:f.contentWindow.innerWidth,height:f.contentWindow.innerHeight,canvasWidth:f.contentWindow.document.querySelector('canvas').clientWidth,canvasHeight:f.contentWindow.document.querySelector('canvas').clientHeight})));
 if(JSON.stringify(dimensions[0])!==JSON.stringify(dimensions[1]))throw Error(JSON.stringify(dimensions));
 await p.screenshot({path:process.argv[2].replace('.json','-comparison.png')});
 await p.click('#ten');const afterTen=await p.locator('#status').textContent();if(!afterTen.includes('45.83 ms'))throw Error(afterTen);
 await p.setViewportSize({width:780,height:1100});await p.waitForTimeout(100);const mobile=await p.evaluate(()=>[...document.querySelectorAll('iframe')].map(f=>f.contentWindow.innerWidth));if(mobile.some(w=>w!==1440))throw Error('Visual comparison resized simulation');
 if(errors.length)throw Error(errors.join('\n'));fs.writeFileSync(process.argv[2],JSON.stringify({first,afterTen,dimensions,mobile,errors,transport:'exact in-memory HTML with fetch shim; no live deployment requests'},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
