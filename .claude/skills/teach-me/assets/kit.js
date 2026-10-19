window.Kit={steps(total,show,opts={}){if(Kit._stop)Kit._stop();let i=Math.min(opts.start||0,total-1),timer=0;const ms=opts.interval||1200;
const q=n=>document.querySelector('[data-kit="'+n+'"]');
const sync=()=>{const p=q('play');if(p)p.textContent=timer?'Pause':(i>=total-1?'Replay':'Play');const c=q('count');if(c)c.textContent=(i+1)+' / '+total;};
const go=n=>{i=Math.max(0,Math.min(total-1,n));show(i);sync();};
const stop=()=>{clearInterval(timer);timer=0;sync();};
const play=()=>{if(timer)return stop();if(i>=total-1)go(0);timer=setInterval(()=>{if(i>=total-1)stop();else go(i+1);},ms);sync();};
q('play')&&(q('play').onclick=play);
q('step')&&(q('step').onclick=()=>{stop();go(i>=total-1?0:i+1);});
Kit._stop=stop;go(i);return{go,play,stop,get index(){return i;}};}};
