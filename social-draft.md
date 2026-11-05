# 中文草稿

#30DayMapChallenge Day 06 — Vintage｜台南古地圖

一張古地圖，不只是換成泛黃的底色。

這次以作者保存的臺灣堡圖資料，重繪日治時期台南的土地利用、聚落、道路與地名。技術上，先用 GeoPandas／Shapely 整理 Shapefile 的中文編碼、分類與幾何，再透過 Tippecanoe 轉成 PMTiles 向量圖磚，以 MapLibre GL JS 製作可搜尋地名、切換圖層的互動地圖。

樣式受原始堡圖設計啟發，參照原圖符號簡化重繪；搭配暖紙色、藍綠水域、暖褐聚落、細緻紙紋與鉛筆感紋樣，讓古典視覺與互動閱讀並存。居住地與背景分色，土地不加邊線，讓道路與歷史地名更清楚。

製圖也需要判讀：安平內港在保存資料中被列為未知分類，對照地名與空間位置後，補回應有的水色，並留下校正紀錄。

資料來源：中央研究院人社中心地理資訊科學研究專題中心；使用作者保存的資料。

#Geomni #Vintage #臺灣堡圖 #台南古地圖 #MapLibre #PMTiles #歷史地圖

# English draft

#30DayMapChallenge Day 06 — Vintage | Tainan Vintage Map

A vintage map takes more than a parchment-colored background.

Using a dataset preserved by the author, this map revisits land use, settlements, roads, and place names recorded in the Taiwan Fort Map during the Japanese colonial period. The workflow combines GeoPandas and Shapely for Shapefile encoding, classification, and geometry cleanup; Tippecanoe for PMTiles vector tiles; and MapLibre GL JS for interactive layers and historical place-name search.

The visual design draws on symbols from the original Fort Map, simplified and redrawn with warm paper tones, muted blue-green water, brown settlements, subtle paper grain, and pencil-like patterns. Distinct settlement and background colors, together with fills without land-use outlines, keep roads and historical names legible.

Interpretation matters, too: a polygon covering Anping’s inner harbor was classified as unknown in the preserved dataset. Reading it alongside historical place names and its spatial context helped restore its water classification, with the correction documented separately.

Data source: Center for GIS, Research Center for Humanities and Social Sciences, Academia Sinica; dataset preserved by the author.

#Geomni #Vintage #TaiwanFortMap #Tainan #MapLibre #PMTiles #HistoricalMaps

---

審稿備註（不納入貼文）：授權依作者提供暫列 CC BY-NC-SA 3.0 TW，保存版本適用性待核實；目前沒有公開地圖網址。未發佈社群。
