import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
const port=Number(process.env.PORT||4173);
createServer(async(req,res)=>{try{const source=await readFile('worker/index.js','utf8');const worker=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));const response=await worker.default.fetch(new Request('http://localhost:'+port+req.url,{method:req.method}),{},{});res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));}catch{res.writeHead(500);res.end('Preview error');}}).listen(port,'0.0.0.0',()=>console.log('Chance book dev server on '+port));
