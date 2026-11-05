# 台南古地圖 · Tainan Vintage Map

Geomni · #30DayMapChallenge 2026 · Day 06 — Vintage

以作者保存的臺灣堡圖資料，重新呈現日治時期台南的土地利用、聚落、道路與地名。

## 技術

Shapefile → GeoPandas / Shapely 整理中文編碼、分類與幾何 → Tippecanoe 製作 PMTiles 向量圖磚 → MapLibre GL JS 互動呈現。可搜尋歷史地名、切換土地與五種交通設施圖層。原始欄位保留，人工判讀另存；安平內港的未知分類經判讀補為水域。

## 樣式設計

符號受原始堡圖設計啟發，參照截自原圖的圖例簡化重繪。以暖紙色、低飽和藍綠水域、暖褐居住地與灰綠植被搭配細紙紋、鉛筆感紋樣及宋體地名。一等道路使用連續外框與內線，土地不加邊界線；居住地與背景分色，河川與海域同色。

視覺方向參考 MapTiler Vintage、Esri Modern Antique 與 Mapbox Pencil，樣式與紙紋自行實作，未直接套用其 stylesheet。靜態圖範圍限北緯 22.95 度以北。

## 預覽

執行 `python3 scripts/serve.py`，開啟 http://127.0.0.1:8766/REVIEW.html 。互動頁位於 demo/standalone.html，程式庫、Worker、圖磚與地名均內嵌。一般版本為 demo/index.html。

## 來源與授權

資料來源：[中央研究院人社中心地理資訊科學研究專題中心](https://gis.rchss.sinica.edu.tw/)，使用作者保存的資料。

依作者提供，適用授權暫列 [CC BY-NC-SA 3.0 台灣](https://creativecommons.org/licenses/by-nc-sa/3.0/tw/legalcode)，此保存版本仍待核實。此儲存庫先以私有方式保存，未啟用 Pages。第三方程式庫授權見 demo/vendor/。

## 研究紀錄

完整資料盤點、原始資料、清理成果與研究紀錄保留本地，未納入這份展示儲存庫。scripts/ 保留處理程式；完整重建需搭配本地 source/、clean/ 與 audit/ 等研究檔案。此處的既有地圖可直接預覽；package_standalone.py 可用隨附資產重新打包。

中英社群稿見 social-draft.md，尚未發佈。
