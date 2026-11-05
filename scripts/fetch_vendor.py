from pathlib import Path
import urllib.request,json,hashlib
D=Path(__file__).resolve().parents[1]/'demo/vendor'
urls={'maplibre-gl.mjs':'https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl.mjs','maplibre-gl-worker.mjs':'https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl-worker.mjs','maplibre-gl.css':'https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl.css','pmtiles.js':'https://unpkg.com/pmtiles@3.2.0/dist/pmtiles.js','MapLibre-LICENSE.txt':'https://unpkg.com/maplibre-gl@6.16.0/LICENSE.txt','PMTiles-LICENSE.txt':'https://raw.githubusercontent.com/protomaps/PMTiles/main/LICENSE'}
manifest={}
for name,url in urls.items():
 data=urllib.request.urlopen(url,timeout=40).read();(D/name).write_bytes(data);manifest[name]={'url':url,'sha256':hashlib.sha256(data).hexdigest()};print(name,len(data))
(D/'manifest.json').write_text(json.dumps(manifest,indent=2))
