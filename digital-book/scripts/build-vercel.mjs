import {cp,mkdir} from 'node:fs/promises';
await mkdir('public',{recursive:true});
await cp('web','public',{recursive:true});
console.log('Vercel static book prepared; /api/results runs on Node.js');
