'use strict';
/* User preferences are intentionally independent from the historical notebook. */
(()=>{const KEY='chance-ux-v2',banner=document.getElementById('latestDraw');if(!banner)return;
let settings;try{settings=JSON.parse(localStorage.getItem(KEY)||'{}')}catch{settings={}}
if(!['expanded','compact','hidden'].includes(settings.banner))settings.banner='compact';
const restore=document.createElement('button');restore.id='latestRestore';restore.type='button';restore.textContent='♠ הצג הגרלה אחרונה';restore.onclick=()=>setBanner('compact');banner.before(restore);
const toggle=document.createElement('button');toggle.type='button';toggle.className='latest-toggle';toggle.setAttribute('aria-label','שינוי גודל באנר ההגרלה האחרונה');
const hide=document.createElement('button');hide.type='button';hide.className='latest-toggle';hide.textContent='הסתר';
const toolbar=document.createElement('div');toolbar.className='latest-toolbar';toolbar.append(toggle,hide);
function persist(){try{localStorage.setItem(KEY,JSON.stringify(settings))}catch{}}
function apply(){banner.classList.toggle('latest-compact',settings.banner==='compact');banner.classList.toggle('latest-collapsed',settings.banner==='hidden');restore.classList.toggle('is-visible',settings.banner==='hidden');toggle.textContent=settings.banner==='expanded'?'▴ מזער':'▾ הרחב';toggle.setAttribute('aria-expanded',String(settings.banner==='expanded'));}
function setBanner(v){settings.banner=v;persist();apply()}
toggle.onclick=()=>setBanner(settings.banner==='expanded'?'compact':'expanded');hide.onclick=()=>setBanner('hidden');
const observer=new MutationObserver(()=>{if(toolbar.parentElement!==banner)banner.append(toolbar)});observer.observe(banner,{childList:true});banner.append(toolbar);apply();
const stage=document.getElementById('stage');if(stage){stage.tabIndex=0;stage.setAttribute('aria-label','ספר תוצאות: גלילה אנכית לקריאה, החלקה אופקית לדפדוף');}
})();
