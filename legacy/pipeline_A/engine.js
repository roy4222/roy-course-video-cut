// Generic scene engine for the ML tutoring series. Reads window.LINES, window.DUR, window.SCENES, window.META.
const c=document.getElementById('c'),g=c.getContext('2d');
const F='"Noto Sans CJK TC","Noto Sans CJK JP",sans-serif', M='"DejaVu Sans Mono",monospace';
const BG='#0f1115',PANEL='#161a21',PANEL2='#1c212a',LINE='#2a2f37',INK='#e8eaed',DIM='#8b949e',A='#4c8dff',B='#f5a524',OK='#3fb950',BAD='#f85149',PUR='#a371f7',CY='#39c5cf';
const COL={A,B,OK,BAD,PUR,CY,INK,DIM};const cc=x=>COL[x]||x||A;
const cl=x=>Math.max(0,Math.min(1,x)), ease=x=>1-Math.pow(1-cl(x),3), k=(t,t0,d=0.5)=>ease((t-t0)/d);
const SC={},ORDER=[];LINES.forEach(l=>{if(!SC[l.sc]){SC[l.sc]=[];ORDER.push(l.sc);}SC[l.sc].push(l);});
const START=ORDER.map((s,i)=>i===0?0:SC[s][0].t0-0.9);
let ALPHA=1;
function rr(x,y,w,h,r){r=Math.min(r,h/2,w/2);g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath();}
function box(x,y,w,h,o={}){const a=(o.a??1)*ALPHA;if(a<=0)return;g.globalAlpha=a;rr(x,y,w,h,o.r??18);g.fillStyle=o.fill??PANEL;g.fill();if(o.stroke!==null){g.lineWidth=o.lw??2;g.strokeStyle=o.stroke??LINE;g.stroke();}g.globalAlpha=1;}
function T(s,x,y,size,col,o={}){const a=(o.a??1)*ALPHA;if(a<=0||s==null)return 0;s=String(s);const w=o.w??400;let sz=size;g.font=`${w} ${sz}px ${o.font??F}`;if(o.maxW){while(g.measureText(s).width>o.maxW&&sz>12){sz-=1;g.font=`${w} ${sz}px ${o.font??F}`;}}
  g.globalAlpha=a;g.fillStyle=col;g.textAlign=o.align??'left';g.textBaseline='middle';g.fillText(s,x,y);g.globalAlpha=1;return g.measureText(s).width;}
function tw(s,size,w=400){g.font=`${w} ${size}px ${F}`;return g.measureText(String(s)).width;}
function wrapW(s,size,maxW,w=400){g.font=`${w} ${size}px ${F}`;const out=[];let cur='';for(const ch of String(s)){if(ch==='\n'){out.push(cur);cur='';continue;}if(g.measureText(cur+ch).width>maxW&&cur){out.push(cur);cur=ch;}else cur+=ch;}if(cur)out.push(cur);
  for(let i=1;i<out.length;i++){while(out[i]&&'，。、；：！？」）,.'.includes(out[i][0])){out[i-1]+=out[i][0];out[i]=out[i].slice(1);}}return out.filter(x=>x!=='');}
// multi-line text block, shrinks font until it fits maxH
function TB(s,x,y,maxW,maxH,size,col,o={}){let sz=size,L;for(;;){L=wrapW(s,sz,maxW,o.w??400);if(L.length*sz*1.4<=maxH||sz<=16)break;sz-=2;}
  const lh=sz*1.4;const y0=o.valign==='middle'?y+(maxH-L.length*lh)/2:y;L.forEach((l,i)=>T(l,o.align==='center'?x+maxW/2:x,y0+lh/2+i*lh,sz,col,{a:o.a,w:o.w,align:o.align}));return L.length*lh;}
function arrow(x1,y1,x2,y2,p,col=DIM,a=1,lw=3){if(p<=0||a*ALPHA<=0)return;const x=x1+(x2-x1)*p,y=y1+(y2-y1)*p;g.globalAlpha=a*ALPHA;g.strokeStyle=col;g.fillStyle=col;g.lineWidth=lw;g.beginPath();g.moveTo(x1,y1);g.lineTo(x,y);g.stroke();
  if(p>0.95){const an=Math.atan2(y2-y1,x2-x1);g.beginPath();g.moveTo(x2,y2);g.lineTo(x2-16*Math.cos(an-0.45),y2-16*Math.sin(an-0.45));g.lineTo(x2-16*Math.cos(an+0.45),y2-16*Math.sin(an+0.45));g.closePath();g.fill();}g.globalAlpha=1;}
function chip(s,cx,cy,size,col,a=1,fill=PANEL2){const w=tw(s,size,700)+size*1.4,h=size*1.8;box(cx-w/2,cy-h/2,w,h,{a,fill,stroke:col,r:h/2});T(s,cx,cy+1,size,col,{a,w:700,align:'center'});return w;}
function check(x,y,s,col,a=1){if(a*ALPHA<=0)return;g.globalAlpha=a*ALPHA;g.strokeStyle=col;g.lineWidth=5;g.lineCap='round';g.beginPath();g.moveTo(x-s*0.5,y);g.lineTo(x-s*0.12,y+s*0.38);g.lineTo(x+s*0.55,y-s*0.42);g.stroke();g.lineCap='butt';g.globalAlpha=1;}
function dot(x,y,r,col,a=1){if(a*ALPHA<=0)return;g.globalAlpha=a*ALPHA;g.fillStyle=col;g.beginPath();g.arc(x,y,r,0,7);g.fill();g.globalAlpha=1;}
function ring(x,y,r,col,a=1,lw=3,fillA=0){if(a*ALPHA<=0)return;g.globalAlpha=a*ALPHA;g.strokeStyle=col;g.lineWidth=lw;g.beginPath();g.arc(x,y,r,0,7);g.stroke();if(fillA){g.globalAlpha=a*ALPHA*fillA;g.fillStyle=col;g.fill();}g.globalAlpha=1;}

// ---------- components. Every component gets (o, t, s, R) where s(i)=t0 of scene line i, R=[x,y,w,h] region.
const CMP={};
const at=(o,t,s,d=0.5)=>o.at==null?1:k(t,s(o.at),d);
CMP.cards=(o,t,s,R)=>{const n=o.items.length,cols=o.cols||Math.min(n,n<=4?n:3),rows=Math.ceil(n/cols),gap=28;
  const W=(R[2]-gap*(cols-1))/cols,H=Math.min(o.h||400,(R[3]-gap*(rows-1))/rows);
  o.items.forEach((it,i)=>{const r=Math.floor(i/cols),cI=i%cols;const x=R[0]+cI*(W+gap),y=R[1]+r*(H+gap);const p=it.at==null?1:k(t,s(it.at),0.5);
    const col=cc(it.col);const hl=it.hl!=null?k(t,s(it.hl),0.4):0;
    box(x,y,W,H,{a:p,fill:PANEL,stroke:hl>0.5?col:(it.col?col+'99':LINE),lw:hl>0.5?4:2});
    let yy=y+28;if(it.tag){chip(it.tag,x+28+tw(it.tag,22,700)/2+15,yy+16,22,col,p);yy+=56;}
    const hs=o.hs||(H<230?34:40);T(it.h,x+28,yy+hs*0.6,hs,col,{a:p,w:700,maxW:W-56});yy+=hs*1.5;
    if(it.d)TB(it.d,x+28,yy,W-56,y+H-yy-20,o.ds||28,INK,{a:p});});};
CMP.flow=(o,t,s,R)=>{const n=o.items.length,per=o.per||Math.min(n,n>5?Math.ceil(n/2):n),rows=Math.ceil(n/per),gx=70,gy=60;
  const W=(R[2]-gx*(per-1))/per,H=Math.min(o.h||200,(R[3]-gy*(rows-1))/rows);
  const pos=o.items.map((it,i)=>{const r=Math.floor(i/per),ci=i%per;return[R[0]+ci*(W+gx),R[1]+r*(H+gy)];});
  o.items.forEach((it,i)=>{const p=it.at==null?1:k(t,s(it.at),0.5);const[x,y]=pos[i];let hl=0;(o.hl||[]).forEach(h=>{if(h[1]===i)hl=Math.max(hl,k(t,s(h[0]),0.4));});
    const col=cc(it.col||'A');box(x,y,W,H,{a:p,fill:hl>0.5?'#132036':PANEL,stroke:hl>0.5?col:LINE,lw:hl>0.5?4:2});
    dot(x+36,y+40,20,col,p);T(String(i+1),x+36,y+41,22,'#fff',{a:p,w:700,align:'center',font:M});T(it.h,x+68,y+40,o.hs||32,INK,{a:p,w:700,maxW:W-84});
    if(it.d)TB(it.d,x+24,y+76,W-48,H-90,o.ds||24,DIM,{a:p});
    if(i<n-1){const[x2,y2]=pos[i+1];const pn=it.at==null?1:k(t,s(o.items[i+1].at??0),0.5);if(y2===y)arrow(x+W+8,y+H/2,x2-8,y2+H/2,pn,DIM,1);else arrow(x+W/2,y+H+6,x2+W/2,y2-8,pn,DIM,1);}});};
CMP.compare=(o,t,s,R)=>{const gap=o.vs===false?40:120,W=(R[2]-gap)/2;[o.left,o.right].forEach((P,j)=>{if(!P)return;const x=R[0]+j*(W+gap),y=R[1],H=R[3];const p=P.at==null?1:k(t,s(P.at),0.5);const col=cc(P.col||(j?'B':'A'));
    box(x,y,W,H,{a:p,stroke:col});T(P.h,x+W/2,y+52,P.hs||42,col,{a:p,w:700,align:'center',maxW:W-40});if(P.sub)T(P.sub,x+W/2,y+100,24,DIM,{a:p,align:'center',maxW:W-40});
    let yy=y+(P.sub?140:110);const n=P.items.length,ih=Math.min(o.ih||90,(y+H-yy-20)/n);
    P.items.forEach((it,i)=>{const s0=typeof it==='string'?{t:it}:it;const pi=s0.at==null?p:k(t,s(s0.at),0.5);box(x+24,yy,W-48,ih-14,{a:pi,fill:PANEL2,r:12});TB(s0.t,x+48,yy+6,W-96,ih-26,o.fs||28,INK,{a:pi,valign:'middle'});yy+=ih;});});
  if(o.vs!==false)T('vs',R[0]+R[2]/2,R[1]+R[3]/2,44,DIM,{a:k(t,s(o.right?.at??0),0.5),w:700,align:'center',font:M});};
CMP.table=(o,t,s,R)=>{const n=o.head.length,ws=o.widths?o.widths.map(w=>w*R[2]/o.widths.reduce((a,b)=>a+b,0)):Array(n).fill(R[2]/n);
  const hh=o.hh||70,rh=Math.min(o.rh||74,(R[3]-hh)/o.rows.length),W=R[2],x=R[0],y=R[1],a=o.at==null?1:k(t,s(o.at),0.5);if(a<=0)return;
  box(x,y,W,hh+rh*o.rows.length,{a,r:14});let cx=x;o.head.forEach((h,j)=>{T(h,cx+ws[j]/2,y+hh/2,o.hs||28,DIM,{a,w:700,align:'center',maxW:ws[j]-16});cx+=ws[j];});
  o.rows.forEach((r,i)=>{const ra=(o.rowAt?k(t,s(o.rowAt[i]),0.4):1)*a;cx=x;r.forEach((v,j)=>{T(v,cx+ws[j]/2,y+hh+i*rh+rh/2,o.fs||30,INK,{a:ra,align:'center',maxW:ws[j]-20});cx+=ws[j];});
    g.globalAlpha=a*ALPHA*0.8;g.strokeStyle=LINE;g.lineWidth=1;g.beginPath();g.moveTo(x,y+hh+i*rh);g.lineTo(x+W,y+hh+i*rh);g.stroke();g.globalAlpha=1;});
  (o.hl||[]).forEach(h=>{const p=k(t,s(h.at),0.4)*(h.until!=null?1-k(t,s(h.until),0.3):1);if(p<=0)return;const col=cc(h.col);g.globalAlpha=p*ALPHA;g.strokeStyle=col;g.lineWidth=4;
    if(h.row!=null){rr(x-4,y+hh+h.row*rh+2,W+8,rh-4,10);}else{let x0=x;for(let j=0;j<h.c0;j++)x0+=ws[j];let w=0;for(let j=h.c0;j<=(h.c1??h.c0);j++)w+=ws[j];rr(x0+4,y-4,w-8,hh+rh*o.rows.length+8,10);}
    g.stroke();g.globalAlpha=0.12*p*ALPHA;g.fillStyle=col;g.fill();g.globalAlpha=1;
    if(h.label){const ty=y+hh+rh*o.rows.length+34;let x0=x;if(h.c0!=null){for(let j=0;j<h.c0;j++)x0+=ws[j];}T(h.label,h.c0!=null?x0+8:x,ty,26,col,{a:p,w:700});}});};
CMP.nested=(o,t,s,R)=>{const n=o.rings.length,cx=R[0]+(o.cx??R[3]*0.6),cy=R[1]+R[3]/2;o.rings.forEach((r,i)=>{const p=r.at==null?1:k(t,s(r.at),0.6);const rad=R[3]*0.5*(1-i*0.8/n);const col=cc(r.col);ring(cx,cy,rad*(0.9+0.1*p),col,p,4,0.08);
    T(r.label,cx,cy-rad+(i===n-1?rad:44),i===n-1?40:34,col,{a:p,w:700,align:'center',maxW:rad*1.6});});
  if(o.side){const x=R[0]+R[3]*1.25,W=R[0]+R[2]-x;let yy=R[1]+10;const ih=(R[3]-20)/o.side.length;o.side.forEach(it=>{const p=it.at==null?1:k(t,s(it.at),0.5);box(x,yy,W,ih-18,{a:p,fill:PANEL2,stroke:cc(it.col)+'aa'});T(it.h,x+24,yy+34,30,cc(it.col),{a:p,w:700,maxW:W-48});if(it.d)TB(it.d,x+24,yy+60,W-48,ih-90,24,INK,{a:p});yy+=ih;});}};
CMP.tree=(o,t,s,R)=>{const N={};o.nodes.forEach(n=>N[n.id]={...n,kids:[]});o.nodes.forEach(n=>{if(n.parent)N[n.parent].kids.push(n.id);});const root=o.nodes[0].id;
  const depth={},leaves=[];(function walk(id,d){depth[id]=d;if(!N[id].kids.length)leaves.push(id);N[id].kids.forEach(k2=>walk(k2,d+1));})(root,0);
  const maxD=Math.max(...Object.values(depth));const X={};leaves.forEach((id,i)=>X[id]=R[0]+R[2]*(i+0.5)/leaves.length);(function px(id){if(N[id].kids.length){N[id].kids.forEach(px);X[id]=N[id].kids.reduce((a,b)=>a+X[b],0)/N[id].kids.length;}})(root);
  const Y=id=>R[1]+40+depth[id]*(R[3]-80)/Math.max(1,maxD);const bw=o.bw||260,bh=o.bh||70;
  o.nodes.forEach(n=>{const p=n.at==null?1:k(t,s(n.at),0.5);if(n.parent){const pp=N[n.parent];arrow(X[n.parent],Y(n.parent)+bh/2,X[n.id],Y(n.id)-bh/2-4,p,DIM,1);if(n.edge)T(n.edge,(X[n.parent]+X[n.id])/2+(X[n.id]<X[n.parent]?-30:30),(Y(n.parent)+Y(n.id))/2,24,DIM,{a:p,align:'center'});}
    const col=cc(n.col||(n.kids?.length||N[n.id].kids.length?'A':'OK'));const hl=n.hl!=null?k(t,s(n.hl),0.4):0;box(X[n.id]-bw/2,Y(n.id)-bh/2,bw,bh,{a:p,fill:N[n.id].kids.length?'#132036':'#10201a',stroke:col,lw:hl>0.5?5:2});T(n.label,X[n.id],Y(n.id),28,INK,{a:p,w:700,align:'center',maxW:bw-20});});};
CMP.scatter=(o,t,s,R)=>{const p0=o.at==null?1:k(t,s(o.at),0.6);const x0=R[0]+60,y0=R[1]+R[3]-50,W=R[2]-90,H=R[3]-80;
  g.globalAlpha=p0*ALPHA;g.strokeStyle=DIM;g.lineWidth=2;g.beginPath();g.moveTo(x0,R[1]+10);g.lineTo(x0,y0);g.lineTo(x0+W,y0);g.stroke();g.globalAlpha=1;
  if(o.axes){T(o.axes[0],x0+W,y0+30,24,DIM,{a:p0,align:'right'});T(o.axes[1],x0+10,R[1]+10,24,DIM,{a:p0});}
  const colAt=o.colorAt!=null?k(t,s(o.colorAt),0.6):1;
  o.pts.forEach((q,i)=>{const pa=k(t,(o.at==null?0:s(o.at))+i*0.03,0.4);const ci=q[2]!=null?['A','B','OK','PUR','BAD'][q[2]]:'DIM';dot(x0+q[0]*W,y0-q[1]*H,o.dr||11,colAt>0.5?cc(ci):DIM,pa);});
  (o.groups||[]).forEach(gr=>{const p=k(t,s(gr.at),0.6);ring(x0+gr.x*W,y0-gr.y*H,gr.r*W,cc(gr.col),p,3,0.06);if(gr.label)T(gr.label,x0+gr.x*W,y0-gr.y*H-gr.r*W-22,26,cc(gr.col),{a:p,w:700,align:'center'});});
  (o.lines||[]).forEach(L=>{const p=k(t,s(L.at),0.8);arrow(x0+L.x1*W,y0-L.y1*H,x0+(L.x1+(L.x2-L.x1)*p)*W,y0-(L.y1+(L.y2-L.y1)*p)*H,1,cc(L.col||'B'),p>0?1:0,4);if(L.label)T(L.label,x0+L.x2*W,y0-L.y2*H-24,24,cc(L.col||'B'),{a:p,align:'right'});});
  (o.marks||[]).forEach(m=>{const p=k(t,s(m.at),0.5);ring(x0+m.x*W,y0-m.y*H,22,cc(m.col||'BAD'),p,4);if(m.label)T(m.label,x0+m.x*W+30,y0-m.y*H,26,cc(m.col||'BAD'),{a:p,w:700});});};
CMP.bars=(o,t,s,R)=>{const n=o.items.length,gap=30,bw=(R[2]-gap*(n-1))/n,mx=o.max||Math.max(...o.items.map(i=>i.v));const base=R[1]+R[3]-50,H=R[3]-110;
  o.items.forEach((it,i)=>{const p=it.at==null?1:k(t,s(it.at),0.8);const x=R[0]+i*(bw+gap),h=H*it.v/mx*p;box(x,base-h,bw,Math.max(h,2),{a:p>0?1:0,fill:cc(it.col||'A'),stroke:null,r:8});
    T(it.label,x+bw/2,base+28,24,INK,{a:p>0?1:0,align:'center',maxW:bw});T(it.vl??String(it.v),x+bw/2,base-h-24,26,cc(it.col||'A'),{a:p,w:700,align:'center',font:M,maxW:bw});});};
CMP.formula=(o,t,s,R)=>{const n=o.lines.length;const lh=Math.min(o.lh||110,R[3]/n);o.lines.forEach((L,i)=>{const p=L.at==null?1:k(t,s(L.at),0.5);const y=R[1]+lh*i;
    if(L.box!==false)box(R[0],y,R[2],lh-18,{a:p,fill:L.fill||PANEL,stroke:L.col?cc(L.col):LINE});T(L.t,R[0]+(L.align==='left'?36:R[2]/2),y+(lh-18)/2,L.size||40,cc(L.col||'INK'),{a:p,w:L.w??700,align:L.align||'center',font:L.mono?M:F,maxW:R[2]-60});});};
CMP.statement=(o,t,s,R)=>{const n=o.items.length;const lh=R[3]/n;o.items.forEach((L,i)=>{const p=L.at==null?1:k(t,s(L.at),0.5);TB(L.t,R[0],R[1]+lh*i,R[2],lh-10,L.size||52,cc(L.col||'INK'),{a:p,w:L.w??700,align:'center',valign:'middle'});});};
CMP.note=(o,t,s,R)=>{const p=o.at==null?1:k(t,s(o.at),0.5);const col=cc(o.col||'A');box(R[0],R[1],R[2],R[3],{a:p,fill:'#11161d',stroke:col,lw:3});TB(o.t,R[0]+30,R[1]+10,R[2]-60,R[3]-20,o.size||32,col,{a:p,w:700,align:'center',valign:'middle'});};
CMP.chips=(o,t,s,R)=>{let x=R[0],y=R[1]+30;o.items.forEach(it=>{const s0=typeof it==='string'?{t:it}:it;const w=tw(s0.t,o.size||30,700)+(o.size||30)*1.4;if(x+w>R[0]+R[2]){x=R[0];y+=(o.size||30)*2.6;}chip(s0.t,x+w/2,y,o.size||30,cc(s0.col||'INK'),s0.at==null?1:k(t,s(s0.at),0.4));x+=w+24;});};
CMP.quiz=(o,t,s,R)=>{const n=o.qs.length,hgt=Math.min(190,(R[3]-20*(n-1))/n);o.qs.forEach((q,i)=>{const lq=SC[o._sc][q.q],la=SC[o._sc][q.a],y=R[1]+i*(hgt+20);const pq=k(t,lq.t0,0.5),pa=k(t,la.t0,0.4);
    box(R[0],y,R[2],hgt,{a:pq,stroke:pa>0.5?OK:LINE});T(`Q${i+1}　`+q.qt,R[0]+40,y+hgt*0.32,34,INK,{a:pq,w:700,maxW:R[2]-220});T('答：'+q.at,R[0]+40,y+hgt*0.7,30,OK,{a:pa,w:700,maxW:R[2]-220});
    const cx=R[0]+R[2]-80,cy=y+hgt/2;if(t>lq.t1&&t<la.t0+0.4){const p=cl((t-lq.t1)/(la.t0-lq.t1));g.globalAlpha=pq*ALPHA;g.strokeStyle=B;g.lineWidth=8;g.beginPath();g.arc(cx,cy,36,-Math.PI/2,-Math.PI/2+Math.PI*2*(1-p));g.stroke();g.globalAlpha=1;
      T(String(Math.max(1,Math.ceil(la.t0-t))),cx,cy+1,30,B,{a:pq,w:700,align:'center',font:M});}if(pa>0)check(cx,cy,44,OK,pa);});};
CMP.recap=(o,t,s,R)=>{const n=o.items.length,ih=Math.min(100,(R[3]-110)/n);o.items.forEach((r,i)=>{const p=k(t,s(i+1),0.5),y=R[1]+i*ih;box(R[0],y,R[2],ih-16,{a:p,fill:PANEL2,r:14});dot(R[0]+50,y+(ih-16)/2,22,A,p);
    T(String(i+1),R[0]+50,y+(ih-16)/2+1,24,'#fff',{a:p,w:700,align:'center',font:M});T(r,R[0]+96,y+(ih-16)/2,32,INK,{a:p,w:700,maxW:R[2]-130});});
  if(o.next){const pn=k(t,s(SC[o._sc].length-1),0.5),y=R[1]+n*ih+10;box(R[0],y,R[2],86,{a:pn,fill:'#11161d',stroke:A,lw:3});T(o.next,R[0]+R[2]/2,y+43,34,A,{a:pn,w:700,align:'center',maxW:R[2]-40});}};
CMP.icons=(o,t,s,R)=>{const n=o.items.length,W=R[2]/n;o.items.forEach((it,i)=>{const p=it.at==null?1:k(t,s(it.at),0.5),cx=R[0]+W*(i+0.5),cy=R[1]+R[3]*0.38,col=cc(it.col);ring(cx,cy,Math.min(W*0.32,110),col,p,4,0.08);T(it.icon,cx,cy,Math.min(W*0.28,90),col,{a:p,w:700,align:'center'});
    T(it.h,cx,cy+Math.min(W*0.32,110)+46,34,INK,{a:p,w:700,align:'center',maxW:W-30});if(it.d)TB(it.d,cx-W/2+20,cy+Math.min(W*0.32,110)+80,W-40,R[1]+R[3]-(cy+Math.min(W*0.32,110)+80),24,DIM,{a:p,align:'center'});});};
CMP.title=(o,t,s,R)=>{chip(META.ep+' · '+(o.tag||META.part),960,290,32,A,k(t,0.2,0.6));T(o.title||META.title,960,420,o.size||88,INK,{a:k(t,0.4,0.8),w:700,align:'center',maxW:1700});
  T(o.sub||META.series,960,530,40,DIM,{a:k(t,0.8,0.8),align:'center',maxW:1600});const items=o.chips||[];if(items.length){T('今天的地圖',960,615,26,DIM,{a:k(t,s(o.chipsAt??1)-0.2,0.4),align:'center'});
    let ws=items.map(i=>tw(i,28,700)+28*1.4),gap=22,tot=ws.reduce((a,b)=>a+b,0)+gap*(items.length-1);let rows=[[]],rw=[0];items.forEach((it,i)=>{if(rw[rw.length-1]+ws[i]>1700){rows.push([]);rw.push(0);}rows[rows.length-1].push(i);rw[rw.length-1]+=ws[i]+gap;});
    rows.forEach((r,ri)=>{let x=960-(rw[ri]-gap)/2;r.forEach(i=>{chip(items[i],x+ws[i]/2,680+ri*70,28,INK,k(t,s(o.chipsAt??1)+i*0.3,0.4));x+=ws[i]+gap;});});}};
const DEF=[150,215,1620,650];
window.render=(t)=>{g.fillStyle=BG;g.fillRect(0,0,1920,1080);
  g.strokeStyle='#151920';g.lineWidth=1;for(let x=0;x<1920;x+=80){g.beginPath();g.moveTo(x,0);g.lineTo(x,1080);g.stroke();}for(let y=0;y<1080;y+=80){g.beginPath();g.moveTo(0,y);g.lineTo(1920,y);g.stroke();}
  let si=0;START.forEach((v,i)=>{if(t>=v)si=i;});const sc=ORDER[si],st=START[si],en=si+1<ORDER.length?START[si+1]:DUR+1;
  ALPHA=k(t,st,0.6)*(1-k(t,en-0.45,0.45));
  const s=i=>{const L=SC[sc];return L[Math.min(i,L.length-1)].t0;};const S=SCENES[sc]||{v:[]};
  if(!S.isTitle){T(META.ep+' '+META.short,150,70,24,DIM,{maxW:1400});T(S.title||'',150,128,48,INK,{w:700,maxW:1500});
    g.fillStyle=A;g.globalAlpha=ALPHA;g.fillRect(150,162,80,5);g.globalAlpha=1;T(`${String(si).padStart(2,'0')} / ${ORDER.length-1}`,1770,70,24,DIM,{align:'right',font:M});
    if(S.ref)T('講義：'+S.ref,1770,128,22,DIM,{align:'right',maxW:700});}
  (S.v||[]).forEach(o=>{o._sc=sc;const R=o.r||DEF;CMP[o.k](o,t,s,R);});ALPHA=1;
  g.fillStyle='#1f2630';g.fillRect(0,0,1920,6);g.fillStyle=A;g.fillRect(0,0,1920*t/DUR,6);
  for(const L of LINES){if(t>=L.t0-0.05&&t<=L.t1+0.3){const a=k(t,L.t0-0.05,0.15)*(1-k(t,L.t1+0.1,0.2));const lines=wrapW(L.text,38,1600);const lh=52,h=lines.length*lh+24,y0=1052-h;
    let w=0;g.font=`400 38px ${F}`;lines.forEach(l=>w=Math.max(w,g.measureText(l).width));g.globalAlpha=0.78*a;g.fillStyle='#000';rr(960-w/2-28,y0,w+56,h,12);g.fill();g.globalAlpha=1;
    lines.forEach((l,i)=>T(l,960,y0+12+lh/2+i*lh,38,'#fff',{a,align:'center'}));}}
};
document.fonts.load('700 40px "Noto Sans CJK TC"').then(()=>document.fonts.ready).then(()=>{window.render(0);window.READY=true;});
