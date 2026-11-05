from pathlib import Path
import json,geopandas as gpd
R=Path(__file__).resolve().parents[1]
g=gpd.read_parquet(R/'clean/landuse.parquet')
colors={2:'#9fb9b6',1:'#e8dec7',22:'#e8dec7',23:'#e8dec7',3:'#e4d2a9',9:'#d1d3b3',11:'#b4bda1',14:'#9cae92',16:'#d9cfb4',19:'#b28c72',20:'#c3b9a6',21:'#9fb9b6',25:'#e6d4ac',26:'#e6d4ac'}
sem={'farm':'田地','forest':'竹林','wood':'樹林','heath':'荒地','cemetery':'墓地','grassland':'草地','beach':'沙灘','residential':'居住地','river':'河川'}
classes=[]
for code in list(range(1,27))+[999]:
 d=g[g.raw_type==code];tags={k:sorted(d['raw_'+k].dropna().unique().tolist()) for k in ['landuse','natural','waterway']};tag=next((v[0] for v in tags.values() if v),'');label=f'{code:02d} · '+sem.get(tag,'') if len(d) else f'{code:02d} · 本檔無記錄'
 if code==2:label='02 · 海域'
 if code==999:label='999 · 不輸出圖磚'
 if tag=='residential' and code!=19:label=f'{code:02d} · 背景'
 classes.append({'type':code,'count':len(d),'tags':tags,'label':label,'color':colors.get(code),'render':code in colors and len(d)>0,'evidence':'merge.dbf tags; display groups and sea interpretation per latest user clarification; unreviewed TYPEunreviewed 999 excluded; Anping harbor reviewed as sea; Anping harbor corrected separately'})
(R/'audit/class_dictionary.json').write_text(json.dumps(classes,ensure_ascii=False,indent=2))
import pandas as pd
pd.DataFrame([{'TYPE':x['type'],'count':x['count'],**{k:'|'.join(v) for k,v in x['tags'].items()},'label':x['label'],'fill':x['color'] or ''} for x in classes]).to_csv(R/'audit/class_dictionary.csv',index=False,encoding='utf-8-sig')
# Display grouping preserves source TYPE values and geometries.
display=[]
for codes,key,label in [([1,22,23],'background','背景'),([2],'sea','海域'),([3],'3','田地'),([9],'9','草地'),([11],'11','樹林'),([14],'14','竹林'),([16],'16','荒地'),([19],'19','居住地'),([20],'20','墓地'),([21],'21','河川'),([25,26],'beach','沙灘')]:
 members=[c for c in classes if c['type'] in codes]
 first=members[0]
 display.append({**first,'id':key,'types':codes,'label':label,'count':sum(c['count'] for c in members),'render':True})
display[1]['count'] += len(json.loads((R/'audit/manual_classification_corrections.json').read_text()))
(R/'demo/classes.json').write_text(json.dumps(display,ensure_ascii=False,indent=2))
(R/'audit/display_groups.json').write_text(json.dumps(display,ensure_ascii=False,indent=2))
layers=[{'id':'paper','type':'background','paint':{'background-color':'#f1e6cc'}}]
for c in display:
 if not c['render']:continue
 code=c['id']; filt=['in',['coalesce',['get','display_type'],['get','raw_type']],['literal',c['types']]];tag=next((v[0] for v in c['tags'].values() if v),'')
 layers.append({'id':f'land-{code}','type':'fill','source':'bomap','source-layer':'landuse','filter':filt,'paint':{'fill-color':c['color'],'fill-opacity':.90,'fill-antialias':False}})
 if tag in ['farm','forest','wood','heath','cemetery','grassland']:
  layers.append({'id':f'pattern-{code}','type':'fill','source':'bomap','source-layer':'landuse','minzoom':11,'filter':filt,'paint':{'fill-pattern':tag,'fill-opacity':['interpolate',['linear'],['zoom'],11,.20,13,.34,16,.44],'fill-antialias':False}})
# Simplified symbols traced from the supplied PDF pp.5–7 (items 50,54,55,58,61).
road_specs={
 'road_primary':{'label':'一等','pdf_item':58,'symbol':'continuous casing plus inner stroke; round joins and caps; no offset','parts':[{'offset':0,'width':4,'color':'#62513b'},{'offset':0,'width':2.5,'color':'#f1e6cc'}]},
 'road_unknown':{'label':'不明路','pdf_item':55,'symbol':'double dashed','parts':[{'offset':-1.5,'dash':[4,3]},{'offset':1.5,'dash':[4,3]}]},
 'road_footpath':{'label':'小徑','pdf_item':54,'symbol':'single dashed','parts':[{'offset':0,'dash':[4,3]}]},
 'road_minor':{'label':'小路','pdf_item':61,'symbol':'solid plus dashed','parts':[{'offset':-1.3},{'offset':1.3,'dash':[4,3]}]},
 'railway':{'label':'鐵路','pdf_item':50,'symbol':'outlined rail with alternating dark/light blocks','parts':[{'offset':-1.7},{'offset':1.7},{'offset':0,'width':3.4,'dash':[3,3]}]}}
for k in ['road_footpath','road_unknown','road_minor','road_primary','railway']:
 spec=road_specs[k]
 for i,part in enumerate(spec['parts']):
  width=part.get('width',1.0)
  paint={'line-color':part.get('color','#5b503e'),'line-width':['interpolate',['linear'],['zoom'],8,width*.55,12,width,16,width*1.5],'line-offset':['interpolate',['linear'],['zoom'],8,part['offset']*.55,12,part['offset'],16,part['offset']*1.5]}
  if 'dash' in part:paint['line-dasharray']=part['dash']
  layers.append({'id':f'{k}-{i}','type':'line','source':'bomap','source-layer':k,'layout':{'line-cap':'round' if k=='road_primary' else 'butt','line-join':'round'},'paint':paint})
(R/'audit/road_symbols.json').write_text(json.dumps(road_specs,ensure_ascii=False,indent=2))
layers.append({'id':'places','type':'circle','source':'bomap','source-layer':'names','minzoom':9,'paint':{'circle-radius':1.7,'circle-color':'#684a35'}})
style={'version':8,'name':'台南古地圖 · 古典紙圖','metadata':{'design':'Original vintage-inspired palette and pencil textures; references MapTiler Vintage, Esri Modern Antique and Mapbox Pencil; no proprietary stylesheet or imagery copied','redistribution':'UNVERIFIED - LOCAL REVIEW ONLY','classification':'TYPE19 居住地 has distinct warm brown fill; other residential codes restored with shared pale background fill; unreviewed 999 excluded; Anping harbor reviewed as sea; sea and river same water color; no landuse outlines; primary roads use non-offset casing'},'sources':{'bomap':{'type':'vector','url':'pmtiles://./bomap.pmtiles','attribution':'中研院人社中心 GIS 專題中心｜作者保存的資料'}},'layers':layers}
(R/'demo/style.json').write_text(json.dumps(style,ensure_ascii=False,indent=2))
