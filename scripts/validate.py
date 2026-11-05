from pathlib import Path
import geopandas as gpd,numpy as np,pandas as pd,json,hashlib,subprocess,struct
R=Path(__file__).resolve().parents[1];results=[]
for p in sorted((R/'clean').glob('*.parquet')):
 a=gpd.read_parquet(p);b=gpd.read_file(p.with_suffix('.geojson'));assert len(a)==len(b);assert a.source_id.tolist()==b.source_id.tolist();assert a.is_valid.all() and b.is_valid.all();assert not a.geometry.is_empty.any();assert not a.geometry.isna().any()
 dist=float(a.geometry.hausdorff_distance(b.geometry).max());assert dist<1e-10
 for c in a.columns:
  if c=='geometry':continue
  for x,y in zip(a[c],b[c]):
   if pd.isna(x) and pd.isna(y):continue
   if isinstance(x,(int,float,np.number)):assert np.isclose(x,y,rtol=1e-12,atol=1e-10)
   else:assert x==y,(c,x,y)
 results.append({'layer':p.stem,'rows':len(a),'valid':True,'empty':0,'source_id_unique':bool(a.source_id.is_unique),'geojson_roundtrip_max_hausdorff_deg':dist,'attributes_equal':True})
assert sum(r['rows'] for r in results)==12494
v=subprocess.run(['pmtiles','verify',str(R/'demo/bomap.pmtiles')],capture_output=True,text=True);assert v.returncode==0
(R/'audit/pmtiles-verify.txt').write_text(v.stdout+v.stderr)
meta=subprocess.check_output(['pmtiles','show',str(R/'demo/bomap.pmtiles'),'--metadata'],text=True);(R/'audit/pmtiles-metadata.json').write_text(meta)
m=json.loads(meta);assert set(x['id'] for x in m['vector_layers'])==set(r['layer'] for r in results)
selection=json.loads((R/'audit/tile_selection.json').read_text())
land=next(l for l in m['tilestats']['layers'] if l['layer']=='landuse')
types=next(a for a in land['attributes'] if a['attribute']=='raw_type')['values']
assert {1,19,22,23,999}.issubset(set(types)),types
reviewed=gpd.read_parquet(R/'reviewed/landuse.parquet')
tiles=gpd.read_file(R/'tile-input/landuse.geojson')
assert tiles.loc[tiles.raw_type.eq(999),'source_id'].tolist()==['landuse:008844']
assert not tiles.display_type.eq(999).any()
original=gpd.read_parquet(R/'clean/landuse.parquet')
assert reviewed.raw_type.equals(original.raw_type)
assert reviewed.geometry.geom_equals_exact(original.geometry,0).all()
assert 19 in types and land['count']==8940
assert selection['residential_kept']==2113
classes=json.loads((R/'demo/classes.json').read_text())
assert all(c['type']!=999 for c in classes)
assert next(c['label'] for c in classes if c['type']==19)=='居住地'
(R/'audit/tile_filter_validation.json').write_text(json.dumps({'metadata_landuse_count':land['count'],'metadata_types':types,'only_reviewed_original_999_included':True, 'unreviewed_999_excluded':True,'residential_kept':2113,'ui_excludes_999':True},ensure_ascii=False,indent=2))

(R/'audit/validation.json').write_text(json.dumps({'clean_roundtrips':results,'pmtiles_verify':True,'pmtiles_source_layers_match':True,'browser_rendering_verified':False},indent=2))
print('PASS: 7 layer roundtrips, 12494 rows, geometries valid, PMTiles structure/layers verified')
# Supplement source profiles with record deletion flags, projected statistical outliers, key duplication and coordinate extents.
extra=[]
for p in sorted((R/'extracted/0605').rglob('*.shp')):
 b=p.with_suffix('.dbf').read_bytes();count=struct.unpack_from('<I',b,4)[0];head=struct.unpack_from('<H',b,8)[0];rec=struct.unpack_from('<H',b,10)[0];g=gpd.read_file(p,encoding='UTF-8');record={'file':str(p.relative_to(R)),'dbf_header_count':count,'deleted_records':sum(b[head+i*rec]==42 for i in range(count)),'shp_rows':len(g),'numeric_iqr_flags':{},'duplicate_nonnull_keys':{}}
 for c in g.columns:
  if c=='geometry':continue
  if pd.api.types.is_numeric_dtype(g[c]):
   s=g[c].dropna();q1,q3=s.quantile(.25),s.quantile(.75);iqr=q3-q1
   record['numeric_iqr_flags'][c]={'low':float(q1-1.5*iqr) if len(s) else None,'high':float(q3+1.5*iqr) if len(s) else None,'flagged_rows':g.index[(g[c]<q1-1.5*iqr)|(g[c]>q3+1.5*iqr)].tolist(),'interpretation':'statistical screening only; identifiers/categories and natural size variation are not errors'}
  if c.lower() in ['id','fid_']:record['duplicate_nonnull_keys'][c]=int(g[c].dropna().duplicated().sum())
 extra.append(record)
(R/'audit/additional-quality.json').write_text(json.dumps(extra,ensure_ascii=False,indent=2,allow_nan=False))

style=json.loads((R/'demo/style.json').read_text())
assert not any(l['type']=='line' and l.get('source-layer')=='landuse' for l in style['layers'])
assert next(c['types'] for c in classes if c['id']=='background')==[1,22,23]
assert next(c['types'] for c in classes if c['id']=='beach')==[25,26]
assert next(c['color'] for c in classes if c['id']=='sea')==next(c['color'] for c in classes if c['id']=='21')
primary=[l for l in style['layers'] if l.get('source-layer')=='road_primary']
assert len(primary)==2 and all(l['layout']['line-cap']=='round' for l in primary)
assert all(l['paint']['line-offset']==['interpolate',['linear'],['zoom'],8,0.0,12,0,16,0.0] for l in primary)

assert next(l['paint']['fill-color'] for l in style['layers'] if l['id']=='land-19') != next(l['paint']['fill-color'] for l in style['layers'] if l['id']=='land-background')
