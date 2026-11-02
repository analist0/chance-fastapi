import {readFile,writeFile,readdir} from 'node:fs/promises';
const assets={};
for(const name of await readdir('web')){if(name.endsWith('.zip'))continue;const types={html:'text/html; charset=utf-8',css:'text/css; charset=utf-8',js:'application/javascript; charset=utf-8',json:'application/json; charset=utf-8',csv:'text/csv; charset=utf-8'};const type=types[name.split('.').at(-1)];if(!type)continue;assets[name]={type,content:await readFile('web/'+name,'utf8')};}
try{assets['chance-book-source.zip']={type:'application/zip',base64:true,content:(await readFile('web/chance-book-source.zip')).toString('base64')};}catch{}
const source=await readFile('worker/scraper.mjs','utf8'),handler=await readFile('worker/handler.mjs','utf8');
await writeFile('worker/index.js',source+'\n'+handler+'\nconst assets='+JSON.stringify(assets)+';\nexport default makeWorker(assets);\n');
