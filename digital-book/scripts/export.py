from pathlib import Path
import json,zipfile
root=Path(__file__).resolve().parent.parent;d=root/'web';data=json.loads((d/'data.json').read_text())
html=(d/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(d/'style.css').read_text()+'</style>')
html=html.replace('<script src="engine.js"></script>','<script>window.EMBEDDED_DATA='+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+';</script><script>'+(d/'engine.js').read_text().replace('</script','<\\/script')+'</script>')
html=html.replace('<script src="motion.js"></script>','<script>'+(d/'motion.js').read_text().replace('</script','<\\/script')+'</script>')
html=html.replace('<script src="app.js"></script>','<script>'+(d/'app.js').read_text().replace('</script','<\\/script')+'</script>');(d/'chance-book.html').write_text(html)
with zipfile.ZipFile(d/'chance-book-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for folder in ['web','scripts','worker','tests','api']:
  for p in sorted((root/folder).glob('*')):
   if p.is_file() and p.suffix!='.zip' and str(p.relative_to(root))!='worker/index.js':z.write(p,p.relative_to(root))
 for name in ['README.md','package.json','vercel.json','.openai/hosting.json']:
  if (root/name).exists():z.write(root/name,name)
