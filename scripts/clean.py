"""Rebuild from preserved ZIP; no source files overwritten. Run from any directory."""
from pathlib import Path
import json,zipfile,hashlib,struct,platform,subprocess
import geopandas as gpd, pandas as pd, numpy as np, shapely, pyproj
from shapely.validation import explain_validity
from shapely.geometry import MultiPolygon
R=Path(__file__).resolve().parents[1]
def save(p,x):
 (R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf8')
def scalar(x):
 if pd.isna(x): return None
 return x.item() if hasattr(x,'item') else x
zpath=R/'source/BoMapData.zip'
manifest=[]
with zipfile.ZipFile(zpath) as z:
 for i in z.infolist():
  n=i.filename
  try: n=n.encode('cp437').decode('utf8')
  except (UnicodeError): pass
  assert not Path(n).is_absolute() and '..' not in Path(n).parts
  entry=dict(zip_name=i.filename,decoded_name=n,size=i.file_size,crc=i.CRC,metadata_only=n.startswith('__MACOSX') or n.endswith('.DS_Store'))
  if not i.is_dir():
   b=z.read(i);entry['sha256']=hashlib.sha256(b).hexdigest(); p=R/'extracted'/n
   p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists(): assert p.read_bytes()==b
   else: p.write_bytes(b)
  manifest.append(entry)
save('audit/zip_inventory.json',manifest)
profiles=[]; changes=[]; mappings=[]; issues=[]; outputs={}; repairs=[]
roadids={'一等':'road_primary','不明路':'road_unknown','小徑':'road_footpath','小路':'road_minor','鐵路.doc':'railway'}
semantics={'farm':'田地','forest':'竹林','wood':'樹林','heath':'荒地','cemetery':'墓地','grassland':'草地','beach':'沙灘（子類待核）','residential':'residential','river':'河川（來源標籤）'}
for p in sorted((R/'extracted/0605').rglob('*.shp')):
 layer='names' if '1904name' in p.name else 'landuse' if p.stem=='merge' else roadids[p.stem]
 db=p.with_suffix('.dbf').read_bytes(); hlen=struct.unpack_from('<H',db,8)[0]
 fields=[]
 for off in range(32,hlen-1,32):
  desc=db[off:off+32]
  if desc[0]==13:break
  fields.append({'name':desc[:11].split(b'\0')[0].decode('ascii'),'dbf_type':chr(desc[11]),'width':desc[16],'decimal_places':desc[17]})
 g=gpd.read_file(p,encoding='UTF-8'); n=len(g); attrs=g.drop(columns='geometry')
 profile={'layer':layer,'source':str(p.relative_to(R)),'count':n,'dbf_fields':fields,'dbf_language_driver':db[29], 'cpg':p.with_suffix('.cpg').read_text() if p.with_suffix('.cpg').exists() else None,'encoding_used':'UTF-8 (strict raw DBF validation below)','crs_declared':str(g.crs),'bounds':g.total_bounds.tolist(),'geometry_types':g.geom_type.value_counts().to_dict(),'invalid':int((~g.is_valid).sum()),'empty':int(g.is_empty.sum()),'missing_geometry':int(g.geometry.isna().sum()),'non_simple':int((~g.is_simple).sum()),'fields':{}}
 # Validate every character field raw bytes; never silently replace undecodable characters.
 reclen=struct.unpack_from('<H',db,10)[0]; failures=[]
 for row in range(n):
  pos=hlen+row*reclen+1
  for f in fields:
   b=db[pos:pos+f['width']];pos+=f['width']
   if f['dbf_type']=='C':
    try:b.rstrip(b' \0').decode('utf8',errors='strict')
    except UnicodeError:failures.append({'row':row,'field':f['name'],'hex':b.hex()})
 profile['utf8_decode_failures']=failures
 assert not failures
 for c in attrs:
  s=attrs[c]; vc=s.value_counts(dropna=False)
  profile['fields'][c]={'dtype':str(s.dtype),'null':int(s.isna().sum()),'blank':int(s.map(lambda v:isinstance(v,str) and not v.strip()).sum()),'distinct_nonnull':int(s.nunique()),'values':[{ 'value':scalar(k),'count':int(v)} for k,v in vc.items()] if s.nunique()<100 else None}
  if pd.api.types.is_numeric_dtype(s):
   profile['fields'][c]['quantiles']=s.quantile([0,.01,.25,.5,.75,.99,1]).to_dict()
   profile['fields'][c]['nonfinite_nonnull']=int((s.notna() & ~np.isfinite(s)).sum())
  new='raw_'+c.lower()
  mappings.append({'layer':layer,'source_field':c,'source_type':str(s.dtype),'clean_field':new,'operation':'preserve value; explicit UTF-8 decoding','meaning': 'legacy measurement: units/projection not documented' if c in ['AREA','PERIMETER'] else 'source attribute; not a guaranteed identifier' if c.lower() in ['fid_','id'] else 'historical label/classification, not present-day observation'})
 geomkey=g.geometry.map(lambda x:shapely.normalize(x).wkb_hex)
 profile['duplicate_geometry_extra_rows']=int(geomkey.duplicated().sum())
 profile['duplicate_attributes_extra_rows']=int(attrs.duplicated().sum())
 full=attrs.copy();full['_geometry']=geomkey
 profile['duplicate_feature_extra_rows']=int(full.duplicated().sum())
 for idx in full.index[full.duplicated(keep=False)]: issues.append({'layer':layer,'row':int(idx),'issue':'exact_duplicate_preserved'})
 out=g.rename(columns={c:'raw_'+c.lower() for c in attrs}).copy()
 out['source_id']=[f'{layer}:{i:06d}' for i in range(n)];out['source_layer']=layer
 if g.crs is None:
  assert layer=='names' and g.total_bounds[0]>119 and g.total_bounds[2]<122
  profile['coordinate_field_max_difference_deg']=float(max(abs(g.geometry.x-g.POINT_X).max(),abs(g.geometry.y-g.POINT_Y).max()))
  out=out.set_crs(4326);out['crs_status']='assumed_WGS84_missing_prj'
  changes.append({'layer':layer,'action':'assign EPSG:4326 for preview only','evidence':'degree-like coordinates and spatial overlap; POINT_X/Y mismatch in some records; datum not independently proven'})
 else:out=out.to_crs(4326);out['crs_status']='declared_WGS84'
 out['geometry_repaired']=False
 for idx in g.index[~g.is_valid]:
  old=g.geometry[idx];fixed=shapely.make_valid(old);discard=[]
  if fixed.geom_type=='GeometryCollection':
   parts=[]
   for part in fixed.geoms:
    if part.geom_type=='Polygon':parts.append(part)
    elif part.geom_type=='MultiPolygon':parts.extend(part.geoms)
    else:discard.append(part.wkt)
   fixed=MultiPolygon(parts)
  assert fixed.is_valid and not fixed.is_empty
  out.at[idx,'geometry']=fixed;out.at[idx,'geometry_repaired']=True
  repairs.append({'source_id':out.at[idx,'source_id'],'reason':explain_validity(old),'before_type':old.geom_type,'after_type':fixed.geom_type,'before_wkt':old.wkt,'after_wkt':fixed.wkt,'collapsed_components_not_tiled':discard,'area_delta_deg2':fixed.area-old.area})
 if layer=='names':
  dx=g.geometry.x-g.POINT_X;dy=g.geometry.y-g.POINT_Y
  profile['coordinate_mismatch_over_1e_6_deg']=int(((abs(dx)>1e-6)|(abs(dy)>1e-6)).sum())
  for i in g.index[(abs(dx)>1e-6)|(abs(dy)>1e-6)]:issues.append({'layer':layer,'row':int(i),'issue':'coordinate_fields_disagree_with_geometry','dx_deg':float(dx[i]),'dy_deg':float(dy[i])})
  out['name_historical']=out.raw_name.map(lambda x:x.strip() if isinstance(x,str) else x)
  out['name_review']=out.name_historical.map(lambda x: 'missing' if x is None else 'uncertain_source_text' if any(k in x for k in ['缺','?','？','□','�']) else 'private_use_character' if any(0xE000<=ord(k)<=0xF8FF for k in x) else 'as_transcribed')
  for i in out.index[out.name_review!='as_transcribed']:issues.append({'layer':layer,'row':int(i),'issue':out.at[i,'name_review'],'value':out.at[i,'name_historical']})
 elif layer=='landuse':
  out['class_tag']=out.raw_landuse.fillna(out.raw_natural).fillna(out.raw_waterway).fillna('unknown')
  out['class_historical']=out.class_tag.map(semantics).fillna('')
  out.loc[out.raw_type==2,'class_historical']='海域'
  out.loc[out.raw_type==999,'class_historical']=''
  out.loc[out.raw_type.eq(19) & out.raw_landuse.eq('residential'),'class_historical']='居住地'
  out['render_fill']=~out.raw_type.isin([999])
  profile['type_tag_crosswalk']=g.groupby(['TYPE','landuse','natural','waterway'],dropna=False).size().reset_index(name='count').to_dict('records')
  # Positive-area overlap: do not dissolve legitimate historical boundaries.
  projected=out.to_crs(3826); geoms=projected.geometry; tree=geoms.sindex; overlaps=[]
  for i,geo in enumerate(geoms):
   for j in tree.query(geo,predicate='intersects'):
    if j<=i:continue
    area=geo.intersection(geoms.iloc[j]).area
    if area>1: overlaps.append({'a':out.source_id.iloc[i],'b':out.source_id.iloc[j],'overlap_m2':area})
  save('audit/landuse_overlaps_over_1m2.json',overlaps);profile['overlap_pairs_over_1m2']=len(overlaps)
  out['area_m2']=projected.area;out['perimeter_m']=projected.length
  profile['legacy_area_ratio_quantiles']=(out.raw_area/out.area_m2).quantile([0,.5,1]).to_dict()
 else:out['class_historical']=p.stem.replace('.doc','');out['class_tag']=layer
 if layer!='landuse':out['length_m']=out.to_crs(3826).length
 out['source_row']=range(n)
 assert len(out)==n and out.is_valid.all()
 out.to_parquet(R/'clean'/f'{layer}.parquet',index=False)
 out.to_file(R/'clean'/f'{layer}.geojson',driver='GeoJSON')
 profiles.append(profile);outputs[layer]=n
 for c in out.columns:
  if c=='geometry' or c.startswith('raw_'):continue
  mappings.append({'layer':layer,'source_field':'derived','clean_field':c,'source_type':None,'operation':'see clean.py','meaning':{'source_id':'layer + zero-based source row; stable within ZIP hash','source_row':'zero-based DBF record index','name_historical':'UTF-8 decoded original name, edge whitespace trimmed; no modernisation','class_historical':'PDF tag correspondence or original road filename; TYPE codes not inferred','class_tag':'original tag precedence landuse/natural/waterway; unknown retained','area_m2':'recomputed EPSG:3826 planar area','length_m':'recomputed EPSG:3826 planar length','perimeter_m':'recomputed EPSG:3826 planar boundary length'}.get(c,c)})
 save('audit/profiles.json',profiles)
save('audit/field_mapping.json',mappings);pd.DataFrame(mappings).to_csv(R/'audit/field_mapping.csv',index=False,encoding='utf-8-sig')
save('audit/geometry_repairs.json',repairs);save('audit/review_issues.json',issues)
changes += [{'action':'Decode ZIP filenames CP437 bytes as UTF-8; retain original names and hashes in inventory'}, {'action':'Read all DBF character bytes as strict UTF-8; never convert historical spelling to modern names'}, {'action':'Retain duplicate records, nulls, constant FID_, legacy numeric values; add stable source IDs'}, {'action':'Repair only 23 invalid polygons with make_valid; preserve any collapsed remnants in repair log'}, {'action':'Do not apply shift.txt; it refers to imagery and prior application cannot be determined'}, {'action':'Do not map TYPE integers to PDF row numbers: independent coding systems; use existing tag correspondence only'}]
save('audit/cleaning_log.json',changes)
save('audit/run.json',{'source_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'counts':outputs,'versions':{'python':platform.python_version(),'geopandas':gpd.__version__,'shapely':shapely.__version__,'pyproj':pyproj.__version__},'publication_allowed':False,'reason':'ZIP contains no explicit dataset redistribution license; depositar metadata not verified'})
print(json.dumps({'counts':outputs,'repairs':len(repairs),'review_issues':len(issues)},ensure_ascii=False))
