from pathlib import Path
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
R=Path(__file__).resolve().parents[1]
fpath=R/'demo/fonts/I.Ming-8.10.ttf'
font=FontProperties(fname=str(fpath))
plt.rcParams['svg.fonttype']='none';plt.rcParams['font.family']=font.get_name();plt.rcParams['hatch.linewidth']=0.25
colors={'farm':'#e4d2a9','residential':'#e8dec7','forest':'#9cae92','wood':'#b4bda1','heath':'#d9cfb4','cemetery':'#c3b9a6','grassland':'#d1d3b3','beach':'#e6d4ac','river':'#9fb9b6','sea':'#9fb9b6'}
fig=plt.figure(figsize=(16,10),facecolor='#f1e6cc');ax=fig.add_axes([.245,.065,.73,.875]);ax.set_facecolor('#f1e6cc')
x0,x1,y0,y1=120.12,120.41,22.95,23.13
land=gpd.read_parquet(R/'reviewed/landuse.parquet');land=land.cx[x0:x1,y0:y1];land=land[~land.display_type.isin([999])];land.loc[land.display_type.eq(2),'class_tag']='sea'
land.loc[land.raw_landuse.eq('residential') & land.raw_type.eq(19),'class_tag']='residential_19'
colors['residential_19']='#b28c72'
for c,col in colors.items():
 d=land[land.class_tag==c]
 if len(d):d.plot(ax=ax,facecolor=col,edgecolor='none',linewidth=0,hatch={'wood':'o','forest':'//','cemetery':'+','heath':'..','farm':'-','grassland':'.'}.get(c,None))
# Parallel offsets are measured in metres in EPSG:3826, then drawn in geographic view.
for layer,parts in [('road_footpath',[(0,':',.65)]),('road_unknown',[(-12,'--',.65),(12,'--',.65)]),('road_minor',[(-12,'-',.65),(12,'--',.65)]),('road_primary',[(0,'-',2.2),(0,'-',1.3)]),('railway',[(-13,'-',.65),(13,'-',.65),(0,'--',1.6)])]:
 d=gpd.read_parquet(R/'clean'/f'{layer}.parquet').cx[x0:x1,y0:y1]
 if len(d):
  projected=d.to_crs(3826)
  for offset,ls,w in parts:
   line=projected.geometry.offset_curve(offset) if offset else projected.geometry
   line.to_crs(4326).plot(ax=ax,color='#f1e6cc' if layer=='road_primary' and w==1.3 else '#5b503e',linewidth=w,linestyle=ls,capstyle='round',joinstyle='round')
names=gpd.read_parquet(R/'clean/names.parquet').cx[x0:x1,y0:y1];occupied=[]
for _,r in names.iterrows():
 x,y=r.geometry.x,r.geometry.y;n=r.name_historical
 if not n or r.name_review!='as_transcribed':continue
 if any(abs(x-a)<.011+len(n)*.0014 and abs(y-b)<.008 for a,b in occupied):continue
 occupied.append((x,y));ax.plot(x,y,'.',color='#4d3d2b',markersize=2);ax.text(x,y+.001,n,fontproperties=font,fontsize=8,color='#443728',ha='center',va='bottom',clip_on=True,bbox=dict(facecolor='#f1e6cc',alpha=.65,edgecolor='none',pad=.3))
ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_aspect(1/0.921);ax.tick_params(labelsize=8,colors='#8d7c60');ax.ticklabel_format(useOffset=False,style='plain');ax.grid(alpha=.15,color='#9c8e72',linewidth=.5)
for spine in ax.spines.values():spine.set_color('#a79879')
fig.text(.04,.92,'GEOMNI  /  DAY 06',fontsize=12,color='#76654b');fig.text(.04,.85,'台南古地圖',fontproperties=font,fontsize=32,color='#4c3e2d');fig.text(.04,.78,'循著舊地名\n讀一片田地與聚落的風景',fontproperties=font,fontsize=15,linespacing=1.8,color='#65543d');fig.text(.04,.66,'VINTAGE  /  2026',fontsize=11,color='#8c7655')
labels=[('farm','田地'),('residential_19','居住地'),('residential','背景'),('forest','竹林'),('wood','樹林'),('heath','荒地'),('cemetery','墓地'),('river','河川'),('sea','海域')]
for i,(k,n) in enumerate(labels):
 yy=.60-i*.037;fig.patches.append(Rectangle((.042,yy),.012,.014,transform=fig.transFigure,facecolor=colors[k],edgecolor='#978568',linewidth=.5));fig.text(.063,yy,n,fontproperties=font,fontsize=11,color='#66553f')
fig.text(.04,.22,'本地審閱版本\n臺南區域節錄，非全臺資料\n受原始堡圖設計啟發\n海域與河川同色',fontproperties=font,fontsize=11,linespacing=1.7,color='#8b563c')
fig.text(.04,.075,'來源：中研院人社中心 GIS 專題中心\n作者保存的資料 · 北緯 22.95° 以北\n靜態資料預覽，非互動頁面截圖',fontproperties=font,fontsize=9,linespacing=1.7,color='#827055')
fig.text(.94,.88,'N\n↑',fontsize=18,color='#53432e',ha='center');fig.text(.25,.965,'臺灣堡圖 / 日治時期的土地樣貌',fontproperties=font,fontsize=14,color='#776349');fig.text(.97,.02,'06 NOVEMBER  •  REVIEW EDITION',ha='right',fontsize=9,color='#8b7b63')
fig.savefig(R/'preview.png',dpi=140,facecolor=fig.get_facecolor());fig.savefig(R/'preview.svg',facecolor=fig.get_facecolor());print(R/'preview.png')
