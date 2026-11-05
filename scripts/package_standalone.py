from pathlib import Path
import base64,json
R=Path(__file__).resolve().parents[1];D=R/'demo'
s=(D/'app.js').read_text()
font64=base64.b64encode((D/'fonts/I.Ming-8.10.ttf').read_bytes()).decode()
main64=base64.b64encode((D/'vendor/maplibre-gl.mjs').read_bytes()).decode()
s=s.replace("'./vendor/maplibre-gl.mjs'",json.dumps('data:text/javascript;base64,'+main64))
s=s.replace("maplibregl.setWorkerUrl(new URL('./vendor/maplibre-gl-worker.mjs',import.meta.url).href);", "const workerURL=URL.createObjectURL(new Blob([document.querySelector('#worker-data').textContent],{type:'text/javascript'}));maplibregl.setWorkerUrl(workerURL);")
s=s.replace("const style=await (await fetch('style.json')).json();style.sources.bomap.url='pmtiles://'+new URL('bomap.pmtiles',location.href).href;", "const bytes=Uint8Array.from(atob(document.querySelector('#tile-data').textContent.trim()),c=>c.charCodeAt(0));const fileSource=new pmtiles.FileSource(new File([bytes],'bomap.pmtiles'));const archive=new pmtiles.PMTiles(fileSource);protocol.add(archive);const style=JSON.parse(document.querySelector('#style-data').textContent);style.sources.bomap.url='pmtiles://'+fileSource.getKey();")
s=s.replace("(await (await fetch('../clean/names.geojson')).json()).features", "JSON.parse(document.querySelector('#name-data').textContent).features")
s=s.replace("await (await fetch('classes.json')).json()", "JSON.parse(document.querySelector('#class-data').textContent)")
h=(D/'index.html').read_text().replace('<link rel="stylesheet" href="screen.css">','<style>'+(D/'screen.css').read_text()+'</style>')
h=h.replace('<link rel="stylesheet" href="vendor/maplibre-gl.css">','<style>'+(D/'vendor/maplibre-gl.css').read_text()+'</style>')
h=h.replace('<script src="vendor/pmtiles.js"></script>','<script>'+(D/'vendor/pmtiles.js').read_text().replace('</script','<\\/script')+'</script>')
h=h.replace('<link rel="stylesheet" href="paper-texture.css">','<style>'+(D/'paper-texture.css').read_text()+'</style>')
h=h.replace("url('fonts/I.Ming-8.10.ttf')","url('data:font/ttf;base64,"+font64+"')")
embedded='<script id="tile-data" type="application/octet-stream">'+base64.b64encode((D/'bomap.pmtiles').read_bytes()).decode()+'</script>'
for name,path in [('style-data',D/'style.json'),('name-data',R/'clean/names.geojson'),('class-data',D/'classes.json'),('worker-data',D/'vendor/maplibre-gl-worker.mjs')]:embedded+='<script id="'+name+'" type="application/octet-stream">'+path.read_text().replace('</script','<\\/script')+'</script>'
h=h.replace('<script type="module" src="app.js"></script>',embedded+'<script type="module">'+s+'</script>')
licenses=(D/'fonts/IPA_Font_License_Agreement_v1.0.md').read_text()+'\n'+(D/'fonts/readme.md').read_text()+'\n'+'\n'.join((D/'vendor'/n).read_text() for n in ['MapLibre-LICENSE.txt','PMTiles-LICENSE.txt'])
h=h.replace('</body>','<script type="text/plain" id="third-party-licenses">'+licenses.replace('</script','<\\/script')+'</script></body>')
(D/'standalone.html').write_text(h)
