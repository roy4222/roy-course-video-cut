const { openDemo, closeServer } = await import(process.env.LEMO_PAGE_MJS || '/workspace/video_style/lemo-opuscar/core/render/page.mjs');
const dir=process.argv[2];const {browser,page}=await openDemo(dir,{warnings:true});
const res=await page.evaluate(()=>{const out=[];const ts=[];for(const L of window.LINES){ts.push([L.t0+0.9,L.sc]);ts.push([L.t1-0.05,L.sc]);}
  const ov=(a,b)=>Math.max(0,Math.min(a.x1,b.x1)-Math.max(a.x0,b.x0))*Math.max(0,Math.min(a.y1,b.y1)-Math.max(a.y0,b.y0));
  const seen=new Set();
  for(const [t,sc] of ts){const X=window.TEXTS(t);const sub=X.filter(x=>x.sub),ct=X.filter(x=>!x.sub);
    for(const x of ct){if(x.x0<20||x.x1>1900||x.y0<0||x.y1>1075){const k='oob'+x.text;if(!seen.has(k)){seen.add(k);out.push(`[${sc} t=${t.toFixed(1)}] OUT-OF-FRAME: ${x.text} (${x.x0|0},${x.y0|0},${x.x1|0},${x.y1|0})`);}}}
    for(let i=0;i<ct.length;i++)for(let j=i+1;j<ct.length;j++){const a=ct[i],b=ct[j];const o=ov(a,b);const m=Math.min((a.x1-a.x0)*(a.y1-a.y0),(b.x1-b.x0)*(b.y1-b.y0));if(o>0.15*m){const k='ov'+a.text+'|'+b.text;if(!seen.has(k)){seen.add(k);out.push(`[${sc} t=${t.toFixed(1)}] OVERLAP: "${a.text}" <> "${b.text}"`);}}}
    if(sub.length){const sy=Math.min(...sub.map(s=>s.y0))-12;for(const x of ct){if(x.y1>sy&&x.y0<1060){const k='sub'+x.text;if(!seen.has(k)){seen.add(k);out.push(`[${sc} t=${t.toFixed(1)}] UNDER-SUBTITLE: ${x.text} (y1=${x.y1|0} > ${sy|0})`);}}}}}
  return out;});
console.log(res.join('\n'));console.log(`layout issues: ${res.length}`);await browser.close();closeServer();
