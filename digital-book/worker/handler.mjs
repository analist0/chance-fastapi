export function makeWorker(assets) {return {async fetch(request,env,ctx){
  const url=new URL(request.url);
  if(request.method!=='GET'&&request.method!=='HEAD')return new Response('Method not allowed',{status:405,headers:{Allow:'GET, HEAD'}});
  if(url.pathname==='/api/results'){
    const page=Number(url.searchParams.get('page')||1);
    if(!Number.isInteger(page)||page<1||page>200)return Response.json({error:'invalid_page'},{status:400});
    try{const result=await fetchArchive(page,ctx);return Response.json({...result,verified:false},{headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});}
    catch(e){return Response.json({error:'source_unavailable',message:'מקור התוצאות אינו זמין כרגע. התוצאות שכבר נשמרו לא שונו.',detail:String(e.message).slice(0,80)},{status:502,headers:{'Cache-Control':'no-store'}});}
  }
  const name=url.pathname==='/'?'index.html':url.pathname.slice(1);
  const asset=assets[name];if(!asset)return new Response('Not found',{status:404});
  const bytes=asset.base64?Uint8Array.from(atob(asset.content),c=>c.charCodeAt(0)):asset.content;
  return new Response(request.method==='HEAD'?null:bytes,{headers:{'content-type':asset.type,'cache-control':name==='data.json'?'no-cache':'no-store','x-content-type-options':'nosniff','referrer-policy':'strict-origin-when-cross-origin'}});
}};}
