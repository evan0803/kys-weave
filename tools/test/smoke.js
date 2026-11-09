const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1500,height:900}});
const errs=[];const fs=require('fs');const base=require('path').resolve(__dirname,'../../node_modules/three')+'/';
await p.route(/jsdelivr/,r=>{const u=r.request().url();const f=u.includes('OrbitControls')?'examples/js/controls/OrbitControls.js':'build/three.min.js';r.fulfill({body:fs.readFileSync(base+f),contentType:'application/javascript'})});await p.route(/fonts\.g/,r=>r.fulfill({body:'',contentType:'text/css'}));p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('file://'+require('path').resolve(__dirname,'../../index.html'));await p.waitForTimeout(2500);
await p.click('#bAuto');await p.waitForTimeout(800);await p.click('#aRun');await p.waitForTimeout(4000);
await p.screenshot({path:require('path').resolve(__dirname,'../../out/run.png')});await p.waitForTimeout(6000);await p.screenshot({path:require('path').resolve(__dirname,'../../out/done.png')});
console.log(JSON.stringify(errs.slice(0,5)));await b.close()})();
