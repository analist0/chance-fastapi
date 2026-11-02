'use strict';
/* Advanced historical research. Never presents descriptive patterns as forecasts. */
(()=>{
const ranks=['7','8','9','10','J','Q','K','A'],suits=['♠','♥','♦','♣'];
const $=id=>document.getElementById(id);
const selectors=Array.from({length:4},(_,i)=>'<label>'+suits[i]+'<select class="cp-rank" data-pos="'+i+'"><option value="*">כל ערך</option><option value="low">נמוך 7–9</option><option value="mid">אמצע 10–Q</option><option value="high">גבוה K–A</option>'+ranks.map(r=>'<option>'+r+'</option>').join('')+'</select></label>').join('');
const panel=document.createElement('section');panel.id='chancePro';panel.hidden=true;panel.innerHTML='<div class="cp-head"><div><small>CHANCE RESEARCH STUDIO</small><h2>ספר הדפוסים החכם</h2><p>ניתוח היסטורי מתוך התוצאות הטעונות בספר</p></div><button id="cpClose" aria-label="סגירה">✕ חזרה לספר</button></div><div class="cp-grid"><aside class="cp-controls"><h3>בונה דפוסים</h3><p>בחרו ערך או אזור לכל סדרה</p><div class="cp-selectors">'+selectors+'</div><label>מספר הגרלות לפני תוצאה<input id="cpLookback" type="number" min="1" max="20" value="5"></label><button id="cpRun" class="cp-primary">חפש דפוס בספר</button><button id="cpReset">נקה בחירה</button><hr><h3>גילוי אוטומטי</h3><p>הצירופים החוזרים ביותר בארכיון</p><div id="cpDiscover"></div></aside><div class="cp-main"><div class="cp-metrics" id="cpMetrics"></div><div class="cp-pages"><article class="cp-paper"><h3>הופעות היסטוריות</h3><div id="cpMatches"></div></article><article class="cp-paper"><h3>מפת חום · ערך לפי סדרה</h3><div id="cpHeat"></div><h3>רצפים ופערים</h3><div id="cpGaps"></div><h3>מה קדם להופעות?</h3><div id="cpBefore"></div></article></div><div class="cp-disclaimer">הנתונים מתארים הגרלות קודמות בלבד. ריבוי חיפושים יוצר דפוסים מקריים; אין כאן תחזית או יתרון מוכח בהגרלה הבאה.</div></div></div>';
document.querySelector('main').append(panel);
const trigger=document.createElement('button');trigger.textContent='✦ ספר חכם';trigger.className='cp-launch';document.querySelector('.book-actions').append(trigger);
function source(){return window.ChanceBookData?window.ChanceBookData():[];}
function ordered(){return [...source()].sort((a,b)=>a.id-b.id);}
function match(r,sel){return sel.every((v,i)=>v==='*'||v==='low'&&ranks.indexOf(r.cards[i])<=2||v==='mid'&&ranks.indexOf(r.cards[i])>=3&&ranks.indexOf(r.cards[i])<=5||v==='high'&&ranks.indexOf(r.cards[i])>=6||r.cards[i]===v);}
const fmt=n=>Number(n).toLocaleString('he-IL'),percent=(a,b)=>b?(100*a/b).toFixed(2)+'%':'—';
function show(){document.querySelector('#bookView').hidden=true;document.querySelector('#analysisView').hidden=true;document.querySelector('#guideView').hidden=true;panel.hidden=false;document.querySelector('.tabs')?.scrollIntoView({behavior:'smooth'});run();}
function close(){panel.hidden=true;document.querySelector('#bookView').hidden=false;}
trigger.onclick=show;$('cpClose').onclick=close;
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{panel.hidden=true;}));
$('cpReset').onclick=()=>{document.querySelectorAll('.cp-rank').forEach(x=>x.value='*');run();};
$('cpRun').onclick=run;
function run(){const rows=ordered(),sel=[...document.querySelectorAll('.cp-rank')].map(x=>x.value),hits=rows.filter(r=>match(r,sel)),n=rows.length,positions=hits.map(h=>rows.findIndex(r=>r.id===h.id)),gaps=[];for(let i=1;i<hits.length;i++)gaps.push(hits[i].id-hits[i-1].id-1);
const avg=gaps.length?(gaps.reduce((a,b)=>a+b,0)/gaps.length).toFixed(1):'—',max=gaps.length?Math.max(...gaps):'—';
const p=sel.reduce((acc,s)=>acc*(s==='*'?1:s==='low'||s==='mid'?3/8:s==='high'?2/8:1/8),1),expected=n*p;
$('cpMetrics').innerHTML=[['הגרלות במאגר',fmt(n)],['התאמות',fmt(hits.length)],['שכיחות',percent(hits.length,n)],['צפוי במודל אחיד',expected.toFixed(2)]].map(([a,b])=>'<div class="cp-metric"><small>'+a+'</small><strong>'+b+'</strong></div>').join('');
$('cpMatches').innerHTML=hits.length?'<div class="cp-list">'+hits.slice().reverse().slice(0,100).map(r=>'<button class="cp-draw" data-id="'+r.id+'"><span>#'+r.id+' · '+r.date+'</span><b>'+r.cards.map((c,i)=>'<span class="'+(i===1||i===2?'cp-red':'')+'">'+c+suits[i]+'</span>').join(' ')+'</b></button>').join('')+'</div><p>מוצגות עד 100 התאמות אחרונות מתוך '+fmt(hits.length)+'.</p>':'<p>לא נמצאו התאמות לבחירה.</p>';
$('cpMatches').querySelectorAll('[data-id]').forEach(b=>b.onclick=()=>{const id=Number(b.dataset.id);const search=$('drawSearch');if(search){search.value=id;close();if(typeof applyFilters==='function')applyFilters();}});
const counts=Array.from({length:4},(_,s)=>ranks.map(rank=>rows.filter(r=>r.cards[s]===rank).length));
$('cpHeat').innerHTML='<div class="cp-heat">'+counts.map((arr,s)=>'<div class="cp-heatrow"><b>'+suits[s]+'</b>'+arr.map((count,i)=>'<button title="'+suits[s]+' '+ranks[i]+': '+count+'" style="--heat:'+Math.max(.08,count/(n/8||1)*.55).toFixed(2)+'" data-s="'+s+'" data-r="'+ranks[i]+'">'+ranks[i]+'<small>'+count+'</small></button>').join('')+'</div>').join('')+'</div>';
$('cpHeat').querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>{document.querySelectorAll('.cp-rank')[Number(b.dataset.s)].value=b.dataset.r;run();});
$('cpGaps').innerHTML='<p>פער ממוצע בין הופעות: <b>'+avg+'</b> הגרלות · פער מרבי: <b>'+max+'</b></p><p>מספר הופעות: '+fmt(hits.length)+' · סטייה מהצפוי: '+(hits.length-expected).toFixed(2)+'</p><p class="cp-hint">פערים מחושבים לפי מזהי הגרלות; מזהים חסרים במאגר עשויים להשפיע על המדידה.</p>';
const lookback=Math.max(1,Math.min(20,Number($('cpLookback').value)||5)),prior=Array.from({length:4},()=>Object.fromEntries(ranks.map(r=>[r,0])));let windows=0;
for(const index of positions){if(index<lookback)continue;const segment=rows.slice(index-lookback,index);if(segment.some((r,j)=>j&&r.id!==segment[j-1].id+1)||segment.at(-1).id!==rows[index].id-1)continue;windows++;segment.forEach(r=>r.cards.forEach((c,s)=>prior[s][c]++));}
$('cpBefore').innerHTML='<p>חלונות רציפים תקינים: <b>'+windows+'</b> · '+lookback+' הגרלות לפני כל התאמה.</p>'+(windows?'<div class="cp-before">'+prior.map((o,s)=>'<div><b>'+suits[s]+'</b> '+ranks.map(r=>r+': '+o[r]).join(' · ')+'</div>').join('')+'</div>':'<p>אין מספיק חלונות רציפים לניתוח.</p>')+'<p class="cp-hint">אלו ספירות תיאוריות, ללא תיקון לריבוי בדיקות וללא טענת חיזוי.</p>';
const combos=new Map;rows.forEach(r=>{const k=r.cards.join(' ');combos.set(k,(combos.get(k)||0)+1);});
$('cpDiscover').innerHTML=[...combos].sort((a,b)=>b[1]-a[1]).slice(0,8).map(([key,count])=>'<button class="cp-combo" data-combo="'+key+'">'+key+' <b>'+count+' הופעות</b></button>').join('');
$('cpDiscover').querySelectorAll('[data-combo]').forEach(b=>b.onclick=()=>{b.dataset.combo.split(' ').forEach((v,i)=>document.querySelectorAll('.cp-rank')[i].value=v);run();});
}
})();