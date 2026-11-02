(function(root){'use strict';
function progress(dx,width){return Math.min(1,Math.max(0,Math.abs(dx)/Math.max(1,width)));}
function commit(dx,width,velocity){return Math.abs(dx)>=Math.max(45,width*.2)||(Math.abs(dx)>=32&&Math.sign(velocity)===Math.sign(dx)&&Math.abs(velocity)>.5);}
function duration(p,finish,velocity){const distance=finish?1-p:p;return Math.round(Math.max(130,Math.min(360,140+distance*230-Math.min(.7,Math.abs(velocity))*70)));}
function poses(p,dir,width){return {front:`translate3d(${(dir*p*(width+12)).toFixed(2)}px,0,0) rotateY(${(p===0||p===1?0:-dir*Math.sin(Math.PI*p)*2.5).toFixed(3)}deg)`,back:`translate3d(${(-dir*(1-p)*width*.12).toFixed(2)}px,0,0)`};}
const api={progress,commit,duration,poses};if(typeof module!=='undefined'&&module.exports)module.exports=api;root.ChanceMotion=api;
})(typeof globalThis!=='undefined'?globalThis:this);
