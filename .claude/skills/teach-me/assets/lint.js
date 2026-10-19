addEventListener('load',()=>setTimeout(()=>{const P=[],de=document.documentElement,W=de.clientWidth;
if(de.scrollWidth>W+2)P.push('the figure is '+de.scrollWidth+'px wide in a '+W+'px frame, so it scrolls sideways');
const hidden=el=>{for(let e=el;e&&e!==de;e=e.parentElement){const s=getComputedStyle(e);if(s.visibility==='hidden'||+s.opacity<0.15)return true;}return false;};
const name=t=>'"'+(t.length>40?t.slice(0,40)+'…':t)+'"',at=b=>' (at x '+Math.round(b.left)+', y '+Math.round(b.top)+')';
const boxes=[],small=new Set(),shrunk=new Set(),cut=new Set(),pairs=new Set();
const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
while((n=w.nextNode())){const t=n.textContent.replace(/\s+/g,' ').trim();const el=n.parentElement;
if(!t||!el||el.closest('script,style,noscript')||hidden(el))continue;
const r=document.createRange();r.selectNodeContents(n);const rs=[...r.getClientRects()].filter(b=>b.width>1&&b.height>1);if(!rs.length)continue;
let px=parseFloat(getComputedStyle(el).fontSize)||13;const svg=el.ownerSVGElement;
if(el instanceof SVGGraphicsElement){const m=el.getScreenCTM();if(m)px*=Math.hypot(m.a,m.b);}
if(px<10.5&&!el.closest('math')){small.add(name(t)+' ('+Math.round(px)+'px)');
const vb=svg&&svg.viewBox&&svg.viewBox.baseVal;const sw=svg&&svg.getBoundingClientRect().width;
if(vb&&vb.width&&sw&&sw<vb.width*0.95)shrunk.add('an SVG drawn '+Math.round(vb.width)+' units wide is shown at '+Math.round(sw)+'px, so its text shrinks');}
for(const b of rs){if(b.right>W+2||b.left<-2)cut.add(name(t)+at(b));boxes.push({b,t,el});}}
for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){const a=boxes[i],c=boxes[j];if(a.el===c.el)continue;
const x=Math.min(a.b.right,c.b.right)-Math.max(a.b.left,c.b.left),y=Math.min(a.b.bottom,c.b.bottom)-Math.max(a.b.top,c.b.top);
if(x>2&&y>2&&x*y>0.25*Math.min(a.b.width*a.b.height,c.b.width*c.b.height))pairs.add(name(a.t)+' overlaps '+name(c.t)+at(a.b));}
pairs.forEach(p=>P.push(p));cut.forEach(t=>P.push(t+' is cut off at the edge'));
if(small.size)P.push('text too small to read: '+[...small].slice(0,4).join(', '));shrunk.forEach(s=>P.push(s));
parent.postMessage({layoutProblems:P.slice(0,10)},'*');},1200));
