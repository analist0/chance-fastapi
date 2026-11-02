const ranks = new Set(['7','8','9','10','J','Q','K','A']);
const decode = s => s.replace(/&#(\d+);/g,(_,n)=>String.fromCodePoint(+n)).replace(/&#x([0-9a-f]+);/gi,(_,n)=>String.fromCodePoint(parseInt(n,16))).replace(/&nbsp;|&#160;/g,' ').replace(/&spades;/g,'♠').replace(/&hearts;/g,'♥').replace(/&diams;/g,'♦').replace(/&clubs;/g,'♣').replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();
export function parseArchive(html) {
  const rows=[],seen=new Set;let rejected=0;
  const anchor=/<a\b[^>]*href=["'](?:https:\/\/hatulbul\.com)?\/chance\/(\d+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  for(const match of html.matchAll(anchor)) {
    const id=Number(match[1]),t=decode(match[2]);
    const title=t.match(/הגרלה\s+(\d+)/),d=t.match(/(\d{2})\/(\d{2})\/(\d{4})/),time=t.match(/\b([012]\d:[0-5]\d)\b/);
    const cards=['♠','♥','♦','♣'].map(s=>t.match(new RegExp('(10|[789JQKA])\\s*'+s))?.[1]);
    const date=d?`${d[3]}-${d[2]}-${d[1]}`:'';
    const validDate=/^\d{4}-\d{2}-\d{2}$/.test(date)&&!isNaN(Date.parse(date))&&new Date(date).toISOString().slice(0,10)===date;
    if(!Number.isSafeInteger(id)||id<=0||!title||+title[1]!==id||!validDate||cards.some(c=>!ranks.has(c))||(time&&+time[1].slice(0,2)>23)){rejected++;continue;}
    if(seen.has(id))continue;seen.add(id);rows.push({id,date,time:time?.[1]||'',cards});
  }
  const pagination=decode(html).match(/עמוד\s+\d+\s+מתוך\s+(\d+)/);
  return {rows:rows.sort((a,b)=>b.id-a.id),totalPages:pagination?Math.min(200,+pagination[1]):null,rejected};
}
export function mergeRows(existing,incoming) {
  const map=new Map(existing.map(r=>[r.id,r]));let added=0,conflicts=0,enriched=0;
  for(const r of incoming){const old=map.get(r.id);if(!old){map.set(r.id,r);added++;}else if(old.date!==r.date||old.cards.join(',')!==r.cards.join(',')){conflicts++;}else if(!old.time&&r.time){map.set(r.id,{...old,time:r.time});enriched++;}}
  return {rows:[...map.values()].sort((a,b)=>b.id-a.id),added,conflicts,enriched};
}
const sourceMemo=new Map();
export async function fetchArchive(page,ctx,fetcher=fetch,cache=null) {
  const url=page===1?'https://hatulbul.com/chance/archive':`https://hatulbul.com/chance/archive/${page}`;
  const memo=fetcher===fetch?sourceMemo.get(url):null;
  if(memo&&memo.expires>Date.now())return {...memo.data,cached:true};
  const key=new Request(url);const cached=cache?await cache.match(key):null;
  if(cached)return {...await cached.json(),cached:true};
  const response=await fetcher(url,{headers:{accept:'text/html'},redirect:'follow',signal:AbortSignal.timeout(10000)});
  if(!response.ok)throw Error('upstream_http_'+response.status);
  if(!response.url||!['hatulbul.com','www.hatulbul.com'].includes(new URL(response.url).hostname))throw Error('upstream_redirect');
  const text=await response.text();if(text.length>2000000)throw Error('upstream_size');
  const parsed=parseArchive(text);if(!parsed.rows.length||parsed.rejected)throw Error('upstream_format');
  const data={...parsed,source:url,fetchedAt:new Date().toISOString(),cached:false};
  if(fetcher===fetch)sourceMemo.set(url,{data,expires:Date.now()+120000});
  if(cache){const put=cache.put(key,Response.json(data,{headers:{'Cache-Control':'public, max-age=120'}}));if(ctx?.waitUntil)ctx.waitUntil(put);else await put;}
  return data;
}
