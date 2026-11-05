"""Apply explicit reviewed classification separately from source-preserving clean data."""
from pathlib import Path
import geopandas as gpd,json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'tile-input';D.mkdir(exist_ok=True)
g=gpd.read_parquet(R/'clean/landuse.parquet')
g['display_type']=g.raw_type.copy();g['classification_review']='source';g['correction_id']=''
corrections=json.loads((R/'audit/manual_classification_corrections.json').read_text())
for c in corrections:
 mask=g.source_id.eq(c['source_id']);assert mask.sum()==1
 assert int(g.loc[mask,'raw_type'].iloc[0])==c['original_type']
 g.loc[mask,'display_type']=c['display_type'];g.loc[mask,'class_historical']=c['label'];g.loc[mask,'class_tag']='sea';g.loc[mask,'render_fill']=True
 g.loc[mask,'classification_review']='user_confirmed_interpretation';g.loc[mask,'correction_id']=c['correction_id']
reviewed=R/'reviewed';reviewed.mkdir(exist_ok=True)
g.to_parquet(reviewed/'landuse.parquet',index=False);g.to_file(reviewed/'landuse.geojson',driver='GeoJSON')
excluded_unknown=g.display_type.eq(999);out=g.loc[~excluded_unknown].copy()
out.loc[out.raw_landuse.eq('residential') & out.raw_type.eq(19),'class_historical']='居住地'
out.to_file(D/'landuse.geojson',driver='GeoJSON')
excluded=g.loc[excluded_unknown,['source_id','raw_type']].copy();excluded['reason']='unreviewed_999';excluded.to_csv(R/'audit/tile_exclusions.csv',index=False,encoding='utf-8-sig')
record={'source_records':len(g),'tile_records':len(out),'residential_total':int(out.raw_landuse.eq('residential').sum()),'residential_kept':int((out.raw_landuse.eq('residential') & out.raw_type.eq(19)).sum()),'excluded_999':int(excluded_unknown.sum()),'corrected_original_999':out.loc[out.raw_type.eq(999),'source_id'].tolist(),'rule':'exclude unreviewed display_type 999; include explicitly reviewed Anping water polygon; preserve raw_type','source_clean_data_preserved':True,'tile_input_sha256':hashlib.sha256((D/'landuse.geojson').read_bytes()).hexdigest()}
(R/'audit/tile_selection.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
assert len(out)==8940 and record['residential_kept']==2113
print(record)
