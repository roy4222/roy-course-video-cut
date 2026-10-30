// epB engine: declarative Style-A renderer. Needs window.LINES, window.SCENES, window.EPMETA, window.DUR (timeline.js)
const c=document.getElementById('c'),g=c.getContext('2d');
const F='"Noto Sans CJK TC","Noto Sans CJK JP",sans-serif', M='"DejaVu Sans Mono","Noto Sans CJK TC",monospace';
const BG='#0f1115',PANEL='#161a21',PANEL2='#1c212a',LINE='#2a2f37',INK='#e8eaed',DIM='#8b949e';
const COL={A:'#4c8dff',B:'#f5a524',OK:'#3fb950',BAD:'#f85149',PUR:'#a371f7',INK:INK,DIM:DIM,LINE:LINE,CY:'#39c5cf'};
const col=x=>x?(COL[x]||x):null;
const cl=x=>Math.max(0,Math.min(1,x)), ease=x=>1-Math.pow(1-cl(x),3), k=(t,t0,d=0.5)=>ease((t-t0)/d);
const SC={},ORDER=[];LINES.forEach(l=>{if(!SC[l.sc]){SC[l.sc]=[];ORDER.push(l.sc);}SC[l.sc].push(l);});
const START=ORDER.map((s,i)=>i===0?0:SC[s][0].t0-0.9);
const SPEC={};SCENES.forEach(s=>SPEC[s.id]=s);
let ALPHA=1, TX=[], REC=false;
function rr(x,y,w,h,r){r=Math.min(r,h/2,w/2);g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath();}
function box(x,y,w,h,o={}){const a=(o.a??1)*ALPHA;if(a<=0.001)return;g.globalAlpha=a;rr(x,y,w,h,o.r??18);g.fillStyle=o.fill??PANEL;g.fill();if(o.stroke!==null){g.lineWidth=o.lw??2;g.strokeStyle=o.stroke??LINE;g.stroke();}g.globalAlpha=1;}
function T(s,x,y,size,cc,o={}){s=String(s);const a=(o.a??1)*ALPHA;if(a<=0.001)return 0;const w=o.w??400;let sz=size;const fn=o.font??F;g.font=`${w} ${sz}px ${fn}`;
  if(o.maxW){while(g.measureText(s).width>o.maxW&&sz>12){sz-=1;g.font=`${w} ${sz}px ${fn}`;}}
  g.globalAlpha=a;g.fillStyle=cc;g.textAlign=o.align??'left';g.textBaseline='middle';g.fillText(s,x,y);g.globalAlpha=1;const mw=g.measureText(s).width;
  const _m=g.getTransform();if(REC&&a>0.5&&_m.b===0&&_m.c===0){x+=_m.e;y+=_m.f;let x0=o.align==='center'?x-mw/2:o.align==='right'?x-mw:x;TX.push({text:s,x0,y0:y-sz*0.6,x1:x0+mw,y1:y+sz*0.6,sub:!!o.sub,id:o.id||''});}
  return mw;}
function tw(s,size,w=400,fn=F){g.font=`${w} ${size}px ${fn}`;return g.measureText(String(s)).width;}
function arrow(x1,y1,x2,y2,p,cc=DIM,a=1,lw=3){if(p<=0||a*ALPHA<=0)return;const x=x1+(x2-x1)*p,y=y1+(y2-y1)*p;g.globalAlpha=a*ALPHA;g.strokeStyle=cc;g.fillStyle=cc;g.lineWidth=lw;g.beginPath();g.moveTo(x1,y1);g.lineTo(x,y);g.stroke();
  if(p>0.95){const an=Math.atan2(y2-y1,x2-x1);g.beginPath();g.moveTo(x2,y2);g.lineTo(x2-16*Math.cos(an-0.45),y2-16*Math.sin(an-0.45));g.lineTo(x2-16*Math.cos(an+0.45),y2-16*Math.sin(an+0.45));g.closePath();g.fill();}g.globalAlpha=1;}
function chip(s,cx,cy,size,cc,a=1,fill=PANEL2){const w=tw(s,size,700)+size*1.4,h=size*1.8;box(cx-w/2,cy-h/2,w,h,{a,fill,stroke:cc,r:h/2});T(s,cx,cy+1,size,cc,{a,w:700,align:'center'});return w;}
function check(x,y,s,cc,a=1){if(a*ALPHA<=0)return;g.globalAlpha=a*ALPHA;g.strokeStyle=cc;g.lineWidth=5;g.lineCap='round';g.beginPath();g.moveTo(x-s*0.5,y);g.lineTo(x-s*0.12,y+s*0.38);g.lineTo(x+s*0.55,y-s*0.42);g.stroke();g.lineCap='butt';g.globalAlpha=1;}
function cross(x,y,s,cc,a=1){if(a*ALPHA<=0)return;g.globalAlpha=a*ALPHA;g.strokeStyle=cc;g.lineWidth=5;g.lineCap='round';g.beginPath();g.moveTo(x-s/2,y-s/2);g.lineTo(x+s/2,y+s/2);g.moveTo(x+s/2,y-s/2);g.lineTo(x-s/2,y+s/2);g.stroke();g.lineCap='butt';g.globalAlpha=1;}
function wrap(s,size,maxW,w=400,fn=F){g.font=`${w} ${size}px ${fn}`;const out=[];let cur='';for(const ch of s){if(ch==='\n'){out.push(cur);cur='';continue;}if(g.measureText(cur+ch).width>maxW&&cur){out.push(cur);cur=ch;}else cur+=ch;}if(cur)out.push(cur);
  for(let i=1;i<out.length;i++){while(out[i]&&'，。、；：！？」）,.)'.includes(out[i][0])){out[i-1]+=out[i][0];out[i]=out[i].slice(1);}}return out.filter(x=>x);}
function para(s,x,y,size,cc,maxW,o={}){const ls=wrap(s,size,maxW,o.w??400,o.font??F);const lh=o.lh??size*1.45;ls.forEach((l,i)=>T(l,o.align==='center'?x:x,y+i*lh,size,cc,{...o,maxW:maxW+2}));return ls.length*lh;}
// time helpers: at = line index (number) or [index, offset seconds]
let CUR=null;
function tAt(at){if(at==null)return -1;let i=at,off=0;if(Array.isArray(at)){i=at[0];off=at[1];}const L=SC[CUR];if(i<0)return START[ORDER.indexOf(CUR)]+0.3+off;return L[Math.min(i,L.length-1)].t0+off;}
function tEnd(i){const L=SC[CUR];return L[Math.min(i,L.length-1)].t1;}
function vis(t,e){let a=e.at==null?k(t,tAt(-1),0.5):k(t,tAt(e.at),e.fd??0.5);if(e.until!=null)a*=1-k(t,tAt(e.until)-0.2,0.4);return a;}
const R={};
R.text=(t,e,a)=>{if(e.wrap)para(e.s,e.x,e.y,e.size??32,col(e.col)??INK,e.wrap,{a,w:e.w??400,align:e.align,font:e.mono?M:F});else T(e.s,e.x,e.y,e.size??32,col(e.col)??INK,{a,w:e.w??400,align:e.align,maxW:e.maxW??(1760-(e.align==='center'?0:e.x)),font:e.mono?M:F});};
R.card=(t,e,a)=>{const cc=col(e.col)??LINE;box(e.x,e.y,e.w,e.h,{a,stroke:cc,fill:e.fill??PANEL,lw:e.lw??2});let y=e.y+(e.title?48:30);
  if(e.title){T(e.title,e.align==='center'?e.x+e.w/2:e.x+30,e.y+44,e.ts??36,col(e.tc)??((e.col&&e.col!=='LINE')?cc:INK),{a,w:700,align:e.align,maxW:e.w-50});y=e.y+(e.ts??36)+70;}
  if(e.sub){T(e.sub,e.align==='center'?e.x+e.w/2:e.x+30,e.y+(e.ts??36)+52,24,DIM,{a,align:e.align,maxW:e.w-50,font:e.subMono?M:F});y+=26;}
  (e.body||[]).forEach((b,i)=>{const bb=typeof b==='string'?{s:b}:b;const ba=a*(bb.at!=null?vis(t,bb):1);const sz=bb.size??e.bs??30;
    const h=para(bb.s,e.align==='center'?e.x+e.w/2:e.x+30,y,sz,col(bb.col)??INK,e.w-60,{a:ba,w:bb.w??400,align:e.align,font:bb.mono?M:F});y+=h+(e.bgap??10);});};
R.bullets=(t,e,a)=>{const sz=e.size??32,gap=e.gap??18,h=e.rh??sz*2.5;let y=e.y;e.items.forEach((it,i)=>{const ii=typeof it==='string'?{s:it}:it;const ia=a*(ii.at!=null?vis(t,ii):1);
  const lines=wrap(ii.s,sz,e.w-(e.num===false?60:110),ii.w??600);const hh=Math.max(h,lines.length*sz*1.4+sz*0.8);
  box(e.x,y,e.w,hh,{a:ia,fill:e.fill??PANEL2,r:14,stroke:ii.col?col(ii.col):(e.stroke??LINE)});
  if(e.num!==false){g.globalAlpha=ia*ALPHA;g.fillStyle=col(ii.col)??col(e.col)??COL.A;g.beginPath();g.arc(e.x+42,y+hh/2,20,0,7);g.fill();g.globalAlpha=1;T(ii.n??String(i+1),e.x+42,y+hh/2+1,22,'#fff',{a:ia,w:700,align:'center',font:M});}
  lines.forEach((l,j)=>T(l,e.x+(e.num===false?28:80),y+hh/2+(j-(lines.length-1)/2)*sz*1.4,sz,col(ii.tc)??INK,{a:ia,w:ii.w??600}));y+=hh+gap;});};
R.chips=(t,e,a)=>{const sz=e.size??28;const its=e.items.map(x=>typeof x==='string'?{s:x}:x);const ws=its.map(i=>tw(i.s,sz,700)+sz*1.4),gap=e.gap??24,tot=ws.reduce((p,q)=>p+q,0)+gap*(its.length-1);let x=(e.cx??960)-tot/2;
  its.forEach((it,i)=>{chip(it.s,x+ws[i]/2,e.y,sz,col(it.col)??col(e.col)??INK,a*(it.at!=null?vis(t,it):1));x+=ws[i]+gap;});};
R.formula=(t,e,a)=>{const sz=e.size??36,lh=e.lh??sz*1.7;const n=e.lines.length;const h=e.h??(n*lh+40);if(e.panel!==false)box(e.x,e.y,e.w,h,{a,fill:'#11161d',stroke:col(e.col)??LINE,r:16});
  if(e.label)T(e.label,e.x+24,e.y-22,24,DIM,{a,w:700});
  e.lines.forEach((l,i)=>{const ll=typeof l==='string'?{s:l}:l;const la=a*(ll.at!=null?vis(t,ll):1);T(ll.s,e.align==='center'?e.x+e.w/2:e.x+32,e.y+20+lh/2+i*lh,ll.size??sz,col(ll.col)??INK,{a:la,w:ll.w??500,font:ll.cjk?F:M,align:e.align,maxW:e.w-50});});};
R.table=(t,e,a)=>{const hh=e.hh??64,rh=e.rh??58,W=e.ws.reduce((p,q)=>p+q,0),x=e.x,y=e.y,fs=e.fs??28;box(x,y,W,hh+rh*e.rows.length,{a,fill:PANEL,r:14});
  e.rows.forEach((r,i)=>{let ra=a*(e.rowAt&&e.rowAt[i]!=null?k(t,tAt(e.rowAt[i]),0.4):1);(e.dim||[]).forEach(d=>{if(d.rows.includes(i))ra*=1-0.75*vis(t,d);});
    (e.fills||[]).forEach(f=>{if(f.row===i){const fa=vis(t,f);if(fa>0){g.globalAlpha=0.22*fa*ra*ALPHA;g.fillStyle=col(f.col);g.fillRect(x+2,y+hh+i*rh+2,W-4,rh-4);g.globalAlpha=1;}}});
    let cx=x;r.forEach((v,j)=>{let cc=INK;(e.cellCol||[]).forEach(cc2=>{if(cc2.row===i&&cc2.col===j&&vis(t,cc2)>0.5)cc=col(cc2.c);});T(v,cx+e.ws[j]/2,y+hh+i*rh+rh/2,fs,cc,{a:ra,align:'center',maxW:e.ws[j]-10,font:e.mono?M:F,w:(e.bold&&e.bold.includes(j))?700:400});cx+=e.ws[j];});
    g.globalAlpha=a*ALPHA*0.8;g.strokeStyle=LINE;g.lineWidth=1;g.beginPath();g.moveTo(x,y+hh+i*rh);g.lineTo(x+W,y+hh+i*rh);g.stroke();g.globalAlpha=1;});
  let cx=x;e.head.forEach((h,j)=>{T(h,cx+e.ws[j]/2,y+hh/2,e.hs??26,DIM,{a,align:'center',w:700,maxW:e.ws[j]-12});cx+=e.ws[j];});
  const hl=(x0,y0,w,h,cc,p)=>{if(p<=0)return;g.globalAlpha=p*ALPHA;g.strokeStyle=cc;g.lineWidth=4;rr(x0,y0,w,h,10);g.stroke();g.globalAlpha=0.10*p*ALPHA;g.fillStyle=cc;g.fill();g.globalAlpha=1;};
  (e.hl||[]).forEach(h=>{const p=vis(t,h)*a;const cc=col(h.col)??COL.B;const cx0=j=>x+e.ws.slice(0,j).reduce((p,q)=>p+q,0);
    if(h.row!=null&&h.c0==null)hl(x-6,y+hh+h.row*rh-2,W+12,rh*(h.n??1)+4,cc,p);
    else if(h.cols)hl(cx0(h.cols[0])+4,y-6,cx0(h.cols[1]+1)-cx0(h.cols[0])-8,hh+rh*e.rows.length+12,cc,p);
    else if(h.c0!=null)hl(cx0(h.c0)+3,y+hh+h.row*rh+3,cx0(h.c1+1)-cx0(h.c0)-6,rh*(h.n??1)-6,cc,p);});};
R.tree=(t,e,a)=>{const N={};e.nodes.forEach(n=>N[n.id]=n);const nh=e.nh??78;
  const on=id=>(e.path||[]).some(p=>p.ids.includes(id)&&vis(t,p)>0.5);
  e.edges.forEach(ed=>{const A=N[ed.a],B=N[ed.b];const ea=a*(ed.at!=null?vis(t,ed):(B.at!=null?vis(t,B):1));if(ea<=0)return;const pa=on(ed.a)&&on(ed.b);
    arrow(A.x,A.y+nh/2+2,B.x,B.y-nh/2-4,1,pa?COL.OK:DIM,ea,pa?5:3);if(ed.label){const mx=(A.x+B.x)/2,my=(A.y+nh/2+B.y-nh/2)/2;const lw=tw(ed.label,24,700)+18;box(mx-lw/2,my-18,lw,36,{a:ea,fill:BG,stroke:null,r:8});T(ed.label,mx,my,24,pa?COL.OK:(col(ed.col)??COL.CY),{a:ea,w:700,align:'center'});}});
  e.nodes.forEach(n=>{const na=a*(n.at!=null?vis(t,n):1);if(na<=0)return;const w=n.w??(Math.max(tw(n.label,30,700),n.sub?tw(n.sub,24,400,M):0)+50);const h=n.sub?nh+10:nh;const leaf=n.leaf;
    const hc=(e.hl||[]).find(hh=>hh.id===n.id&&vis(t,hh)>0.5);const pc=on(n.id);const cc=hc?col(hc.col??'B'):pc?COL.OK:col(n.col)??(leaf?COL.B:COL.A);
    box(n.x-w/2,n.y-h/2,w,h,{a:na,fill:leaf?'#1f1a10':PANEL2,stroke:cc,lw:(hc||pc)?5:3,r:leaf?h/2:14});
    T(n.label,n.x,n.sub?n.y-15:n.y,n.fs??30,leaf?col(n.col)??COL.B:INK,{a:na,w:700,align:'center',maxW:w-16});if(n.sub)T(n.sub,n.x,n.y+20,24,DIM,{a:na,align:'center',font:M,maxW:w-16});});};
R.arrow=(t,e,a)=>arrow(e.x1,e.y1,e.x2,e.y2,k(t,tAt(e.at??-1),0.6),col(e.col)??DIM,a,e.lw??3);
R.line=(t,e,a)=>{g.globalAlpha=a*ALPHA;g.strokeStyle=col(e.col)??LINE;g.lineWidth=e.lw??2;if(e.dash)g.setLineDash(e.dash);g.beginPath();g.moveTo(e.x1,e.y1);g.lineTo(e.x2,e.y2);g.stroke();g.setLineDash([]);g.globalAlpha=1;};
R.flow=(t,e,a)=>{const n=e.items.length,gap=e.gap??60,w=e.bw??((e.w-(n-1)*gap)/n),h=e.h??130;e.items.forEach((it,i)=>{const ia=a*(it.at!=null?vis(t,it):1);const x=e.x+i*(w+gap);
  const hot=it.hot!=null&&vis(t,{at:it.hot,until:it.hotUntil})>0.5;box(x,e.y,w,h,{a:ia,fill:PANEL2,stroke:hot?COL.OK:(col(it.col)??col(e.col)??LINE),lw:hot?4:2});
  T(it.s,x+w/2,e.y+(it.sub?h/2-18:h/2),it.size??e.size??30,col(it.tc)??INK,{a:ia,w:700,align:'center',maxW:w-20});if(it.sub)T(it.sub,x+w/2,e.y+h/2+24,e.subSize??22,DIM,{a:ia,align:'center',maxW:w-20});
  if(i>0)arrow(x-gap+6,e.y+h/2,x-8,e.y+h/2,ia,DIM,ia);});};
R.bars=(t,e,a)=>{const n=e.items.length,bw=e.bw??Math.min(140,(e.w-40)/n*0.6),sp=(e.w-40)/n;g.globalAlpha=a*ALPHA;g.strokeStyle=LINE;g.lineWidth=2;g.beginPath();g.moveTo(e.x,e.y+e.h);g.lineTo(e.x+e.w,e.y+e.h);g.stroke();g.globalAlpha=1;
  e.items.forEach((it,i)=>{const ia=a*(it.at!=null?vis(t,it):1);const gr=it.at!=null?k(t,tAt(it.at),0.8):1;const bh=e.h*it.v/e.max*gr;const cx=e.x+20+sp*(i+0.5);
    box(cx-bw/2,e.y+e.h-bh,bw,Math.max(bh,1),{a:ia,fill:col(it.col)??COL.A,stroke:null,r:6});T(it.vs??String(it.v),cx,e.y+e.h-bh-22,e.vsz??26,INK,{a:ia,w:700,align:'center',font:M});T(it.label,cx,e.y+e.h+30,e.lsz??24,DIM,{a:ia,align:'center',maxW:sp-6});});
  if(e.title)T(e.title,e.x,e.y-30,24,DIM,{a,w:700});};
R.plot=(t,e,a)=>{const X=v=>e.x+(v-e.xr[0])/(e.xr[1]-e.xr[0])*e.w,Y=v=>e.y+e.h-(v-e.yr[0])/(e.yr[1]-e.yr[0])*e.h;
  box(e.x-10,e.y-10,e.w+20,e.h+20,{a,fill:'#11161d',stroke:LINE,r:10});g.globalAlpha=a*ALPHA*0.5;g.strokeStyle=LINE;g.lineWidth=1;for(let i=1;i<(e.grid??5);i++){const u=i/(e.grid??5);g.beginPath();g.moveTo(e.x+u*e.w,e.y);g.lineTo(e.x+u*e.w,e.y+e.h);g.moveTo(e.x,e.y+u*e.h);g.lineTo(e.x+e.w,e.y+u*e.h);g.stroke();}g.globalAlpha=1;
  if(e.diag){g.globalAlpha=a*ALPHA;g.setLineDash([10,8]);g.strokeStyle=DIM;g.lineWidth=2;g.beginPath();g.moveTo(X(e.xr[0]),Y(e.yr[0]));g.lineTo(X(e.xr[1]),Y(e.yr[1]));g.stroke();g.setLineDash([]);g.globalAlpha=1;}
  if(e.xlab)T(e.xlab,e.x+e.w/2,e.y+e.h+(e.ticks?62:36),24,DIM,{a,align:'center'});if(e.ylab){g.save();g.translate(e.x-(e.ticks?62:36),e.y+e.h/2);g.rotate(-Math.PI/2);T(e.ylab,0,0,24,DIM,{a,align:'center'});g.restore();}
  if(e.ticks){e.ticks.x.forEach(v=>T(String(v),X(v),e.y+e.h+28,20,DIM,{a,align:'center',font:M}));e.ticks.y.forEach(v=>T(String(v),e.x-16,Y(v),20,DIM,{a,align:'right',font:M}));}
  (e.fillUnder||[]).forEach(fu=>{const fa=vis(t,fu)*a;if(fa<=0)return;const s=e.series[fu.si];g.globalAlpha=0.18*fa*ALPHA;g.fillStyle=col(fu.col)??COL.A;g.beginPath();g.moveTo(X(s.pts[0][0]),Y(e.yr[0]));s.pts.forEach(p=>g.lineTo(X(p[0]),Y(p[1])));g.lineTo(X(s.pts[s.pts.length-1][0]),Y(e.yr[0]));g.closePath();g.fill();g.globalAlpha=1;});
  e.series.forEach(s=>{const sa=a*(s.at!=null?vis(t,s):1);if(sa<=0)return;let p=1;if(s.draw){p=cl((t-tAt(s.at))/s.draw);}const n=s.pts.length;const upto=Math.max(1,Math.floor(p*(n-1))+1);
    g.globalAlpha=sa*ALPHA;g.strokeStyle=col(s.col)??COL.A;g.lineWidth=s.lw??4;if(s.dash)g.setLineDash(s.dash);g.beginPath();s.pts.slice(0,upto).forEach((q,i)=>{i?g.lineTo(X(q[0]),Y(q[1])):g.moveTo(X(q[0]),Y(q[1]));});g.stroke();g.setLineDash([]);
    if(s.dots){g.fillStyle=col(s.col)??COL.A;s.pts.slice(0,upto).forEach(q=>{g.beginPath();g.arc(X(q[0]),Y(q[1]),s.dots,0,7);g.fill();});}g.globalAlpha=1;
    if(s.label&&p>=1)T(s.label,X(s.pts[n-1][0])+(s.lx??10),Y(s.pts[n-1][1])+(s.ly??0),22,col(s.col)??COL.A,{a:sa,w:700,align:s.la??'left'});});
  (e.marks||[]).forEach(m=>{const ma=a*vis(t,m);if(ma<=0)return;g.globalAlpha=ma*ALPHA;g.fillStyle=col(m.col)??COL.B;g.beginPath();g.arc(X(m.x),Y(m.y),m.r??10,0,7);g.fill();g.globalAlpha=1;if(m.label)T(m.label,X(m.x)+(m.dx??16),Y(m.y)+(m.dy??-20),m.size??22,col(m.col)??COL.B,{a:ma,w:700,align:m.align??'left',font:m.mono?M:F});});
  (e.vlines||[]).forEach(v=>{const va=a*vis(t,v);if(va<=0)return;g.globalAlpha=va*ALPHA;g.strokeStyle=col(v.col)??COL.B;g.lineWidth=3;g.setLineDash([8,6]);g.beginPath();if(v.x!=null){g.moveTo(X(v.x),e.y);g.lineTo(X(v.x),e.y+e.h);}else{g.moveTo(e.x,Y(v.y));g.lineTo(e.x+e.w,Y(v.y));}g.stroke();g.setLineDash([]);g.globalAlpha=1;
    if(v.label)T(v.label,v.x!=null?X(v.x)+8:e.x+e.w-8,v.x!=null?e.y+20:Y(v.y)-18,20,col(v.col)??COL.B,{a:va,w:700,align:v.x!=null?'left':'right'});});
  (e.pts||[]).forEach(p=>{const pa=a*(p.at!=null?vis(t,p):1);if(pa<=0)return;g.globalAlpha=pa*ALPHA;g.fillStyle=col(p.col)??COL.A;g.strokeStyle=g.fillStyle;g.lineWidth=3;const x=X(p.x),y=Y(p.y);
    if(p.m==='x'){g.beginPath();g.moveTo(x-8,y-8);g.lineTo(x+8,y+8);g.moveTo(x+8,y-8);g.lineTo(x-8,y+8);g.stroke();}else if(p.m==='o'){g.beginPath();g.arc(x,y,8,0,7);g.stroke();}else{g.beginPath();g.arc(x,y,p.r??8,0,7);g.fill();}g.globalAlpha=1;});
  (e.rects||[]).forEach(r=>{const ra=a*vis(t,r);if(ra<=0)return;g.globalAlpha=0.16*ra*ALPHA;g.fillStyle=col(r.col);g.fillRect(X(r.x0),Y(r.y1),X(r.x1)-X(r.x0),Y(r.y0)-Y(r.y1));g.globalAlpha=1;});
  (e.segs||[]).forEach(s=>{const sa=a*vis(t,s);if(sa<=0)return;g.globalAlpha=sa*ALPHA;g.strokeStyle=col(s.col)??COL.B;g.lineWidth=s.lw??5;if(s.dash)g.setLineDash(s.dash);g.beginPath();s.pts.forEach((q,i)=>{i?g.lineTo(X(q[0]),Y(q[1])):g.moveTo(X(q[0]),Y(q[1]));});g.stroke();g.setLineDash([]);g.globalAlpha=1;});};
R.blocks=(t,e,a)=>{const bw=e.bw??120,bh=e.bh??60,gap=e.gap??10;e.rows.forEach((r,i)=>{const ra=a*(r.at!=null?vis(t,r):1);if(ra<=0)return;const y=e.y+i*(bh+(e.rgap??22));
  if(r.label)T(r.label,e.x-20,y+bh/2,e.lsz??26,DIM,{a:ra,w:700,align:'right'});let _o=0;r.cells.forEach((c2,j)=>{const cc=typeof c2==='string'?{s:c2}:c2;const x=e.x+_o*(bw+gap);_o+=(cc.span??1);const w=(cc.span??1)*bw+((cc.span??1)-1)*gap;box(x,y,w,bh,{a:ra,fill:col(cc.fill)??PANEL2,stroke:col(cc.col)??LINE,r:10,lw:cc.col?3:2});
    T(cc.s,x+w/2,y+bh/2,e.fs??24,cc.tc?col(cc.tc):INK,{a:ra,w:700,align:'center',maxW:w-10});});
  if(r.note)T(r.note,e.x+r.cells.reduce((p,c3)=>p+((typeof c3==='object'&&c3.span)||1),0)*(bw+gap)+20,y+bh/2,e.nsz??26,col(r.ncol)??INK,{a:ra,w:600});});};
R.code=(t,e,a)=>{box(e.x,e.y,e.w,e.h,{a,fill:'#0b0d12',stroke:'#30363d',r:12});g.globalAlpha=a*ALPHA;g.fillStyle='#161b22';rr(e.x,e.y,e.w,44,12);g.fill();g.fillRect(e.x,e.y+30,e.w,14);g.globalAlpha=1;
  ['#f85149','#f5a524','#3fb950'].forEach((cc,i)=>{g.globalAlpha=a*ALPHA;g.fillStyle=cc;g.beginPath();g.arc(e.x+26+i*24,e.y+22,7,0,7);g.fill();g.globalAlpha=1;});T(e.title??'A3_titanic.ipynb',e.x+e.w/2,e.y+22,20,DIM,{a,align:'center',font:M});
  let y=e.y+70;const sz=e.size??24,lh=sz*1.5;const KW=/\b(import|from|as|for|in|def|return|print|if|else|None|True|False)\b/g;
  e.cells.forEach((cel,ci)=>{const ca=a*(cel.at!=null?vis(t,cel):1);if(ca<=0){y+=0;return;}T(`In [${ci+1}]:`,e.x+18,y+lh/2-2,sz*0.8,'#3fb950',{a:ca,font:M});
    const h=cel.code.length*lh+16;box(e.x+130,y-8,e.w-150,h,{a:ca,fill:'#161b22',stroke:'#30363d',r:8});
    cel.code.forEach((ln,i)=>{const isC=ln.trim().startsWith('#');T(ln,e.x+146,y+lh/2+i*lh,sz,isC?'#8b949e':'#e6edf3',{a:ca,font:M,maxW:e.w-180});});y+=h+10;
    if(cel.out){const oa=ca*(cel.oat!=null?k(t,tAt(cel.oat),0.4):1);cel.out.forEach((ln,i)=>T(ln,e.x+146,y+lh/2+i*lh,sz*0.92,cel.ocol?col(cel.ocol):'#c9d1d9',{a:oa,font:M,maxW:e.w-180}));y+=cel.out.length*lh+14;}y+=8;});};
R.quiz=(t,e,a)=>{const L=SC[CUR];e.qs.forEach((q,i)=>{const lq=L[q.qi],la=L[q.ai],y=e.y+i*(e.dy??205);const pq=k(t,lq.t0,0.5),pa=k(t,la.t0,0.4);
  box(160,y,1600,180,{a:pq,stroke:pa>0.5?COL.OK:LINE});T(q.q,200,y+55,34,INK,{a:pq,w:700,maxW:1390});para('答：'+q.a,200,y+118,29,COL.OK,1390,{a:pa,w:700,lh:38});
  if(t>lq.t1&&t<la.t0+0.4){const p=cl((t-lq.t1)/(la.t0-lq.t1));g.globalAlpha=pq*ALPHA;g.strokeStyle=COL.B;g.lineWidth=8;g.beginPath();g.arc(1680,y+90,36,-Math.PI/2,-Math.PI/2+Math.PI*2*(1-p));g.stroke();g.globalAlpha=1;
    T(String(Math.max(1,Math.ceil((la.t0-t)))),1680,y+91,30,COL.B,{a:pq,w:700,align:'center',font:M});}
  if(pa>0)check(1680,y+90,44,COL.OK,pa);});};
R.titlecard=(t,e,a)=>{chip(e.ep,960,280,32,COL.A,k(t,0.2,0.6));T(e.title,960,410,e.size??84,INK,{a:k(t,0.4,0.8),w:700,align:'center',maxW:1700});
  T(e.sub,960,520,38,DIM,{a:k(t,0.8,0.8),align:'center',maxW:1600});};
R.hl=(t,e,a)=>{if(a<=0)return;g.globalAlpha=a*ALPHA;g.strokeStyle=col(e.col)??COL.B;g.lineWidth=e.lw??4;rr(e.x,e.y,e.w,e.h,e.r??12);g.stroke();g.globalAlpha=0.08*a*ALPHA;g.fillStyle=col(e.col)??COL.B;g.fill();g.globalAlpha=1;};
R.check=(t,e,a)=>check(e.x,e.y,e.s??40,col(e.col)??COL.OK,a);
R.cross=(t,e,a)=>cross(e.x,e.y,e.s??36,col(e.col)??COL.BAD,a);
R.dots=(t,e,a)=>{(e.items).forEach((d,i)=>{const cc=col(d.c);const r=e.r??14;const da=a*(d.at!=null?vis(t,d):1);if(da<=0)return;const x=d.x,y=d.y;g.globalAlpha=da*ALPHA;g.fillStyle=cc;g.beginPath();if(d.sq)g.rect(x-r,y-r,2*r,2*r);else g.arc(x,y,r,0,7);g.fill();g.globalAlpha=1;});};
R.circle=(t,e,a)=>{g.globalAlpha=a*ALPHA;g.strokeStyle=col(e.col)??COL.A;g.lineWidth=e.lw??3;g.beginPath();g.arc(e.x,e.y,e.r,0,7);if(e.fill){g.fillStyle=col(e.fill);g.globalAlpha=a*ALPHA*(e.fa??0.15);g.fill();g.globalAlpha=a*ALPHA;}g.stroke();g.globalAlpha=1;};
function drawEls(t,els){els.forEach(e=>{const a=vis(t,e);if(a<=0.001)return;R[e.type](t,e,a);});}
window.render=(t)=>{TX=[];g.fillStyle=BG;g.fillRect(0,0,1920,1080);
  g.strokeStyle='#151920';g.lineWidth=1;for(let x=0;x<1920;x+=80){g.beginPath();g.moveTo(x,0);g.lineTo(x,1080);g.stroke();}for(let y=0;y<1080;y+=80){g.beginPath();g.moveTo(0,y);g.lineTo(1920,y);g.stroke();}
  let si=0;START.forEach((v,i)=>{if(t>=v)si=i;});const sc=ORDER[si],st=START[si],en=si+1<ORDER.length?START[si+1]:DUR+1;CUR=sc;
  ALPHA=k(t,st,0.6)*(1-k(t,en-0.45,0.45));const sp=SPEC[sc]||{els:[]};
  if(!sp.noHeader){T(EPMETA.head,150,70,24,DIM,{});T(sp.title||'',150,128,48,INK,{w:700,maxW:1500});
    g.fillStyle=COL[EPMETA.accent||'A'];g.globalAlpha=ALPHA;g.fillRect(150,162,80,5);g.globalAlpha=1;T(`${String(si).padStart(2,'0')} / ${ORDER.length-1}`,1770,70,24,DIM,{align:'right',font:M});
    if(sp.tag)chip(sp.tag,1770-tw(sp.tag,22,700)/2-16,128,22,col(sp.tagCol)??COL.B,1);}
  drawEls(t,sp.els);ALPHA=1;
  g.fillStyle='#1f2630';g.fillRect(0,0,1920,6);g.fillStyle=COL[EPMETA.accent||'A'];g.fillRect(0,0,1920*t/DUR,6);
  for(const L of LINES){if(t>=L.t0-0.05&&t<=L.t1+0.3){const a=k(t,L.t0-0.05,0.15)*(1-k(t,L.t1+0.1,0.2));const lines=wrap(L.text,38,1600);const lh=52,h=lines.length*lh+24,y0=1052-h;
    let w=0;g.font=`400 38px ${F}`;lines.forEach(l=>w=Math.max(w,g.measureText(l).width));g.globalAlpha=0.78*a;g.fillStyle='#000';rr(960-w/2-28,y0,w+56,h,12);g.fill();g.globalAlpha=1;
    lines.forEach((l,i)=>T(l,960,y0+12+lh/2+i*lh,38,'#fff',{a,align:'center',sub:true}));}}
};
window.TEXTS=(t)=>{REC=true;window.render(t);REC=false;return TX;};
document.fonts.load('700 40px "Noto Sans CJK TC"').then(()=>document.fonts.load('400 30px "DejaVu Sans Mono"')).then(()=>document.fonts.ready).then(()=>{window.render(0);window.READY=true;});
