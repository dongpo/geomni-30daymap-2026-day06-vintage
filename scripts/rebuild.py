from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/clean.py')],check=True)
subprocess.run([sys.executable,str(R/'scripts/prepare_tiles.py')],check=True)
layers=['names','landuse','road_primary','road_unknown','road_footpath','road_minor','railway']
cmd=['tippecanoe','-o',str(R/'demo/bomap.pmtiles'),'-Z','6','-z','15','--no-feature-limit','--no-tile-size-limit','--force','--name','Taiwan historical map – Tainan local review','--description','BoMapData.zip; redistribution license unverified; local review only']
for name in layers:cmd+=['-L',name+':'+str(R/('tile-input' if name=='landuse' else 'clean')/f'{name}.geojson')]
import json
(R/'audit/tiles-command.json').write_text(json.dumps(cmd,ensure_ascii=False,indent=2))
with (R/'audit/tippecanoe.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=f,check=True)
for script in ['paper_texture.py','build_demo.py','package_standalone.py','render_preview.py','validate.py','report.py']:
 subprocess.run([sys.executable,str(R/'scripts'/script)],check=True)
subprocess.run(['pmtiles','verify',str(R/'demo/bomap.pmtiles')],check=True)
