# Power BI Desktop Click-by-Click Checklist
## Indian Weather Analytics - Final Report Build

Use this checklist to track every required action. Check off items as you complete them.

---

## 1. Import

- [ ] **Open Power BI Desktop** → Launch application
- [ ] **Save file** → File > Save As → Indian_Weather_Analytics.pbix in C:\Projects\Weather-analytics-Bda-\
- [ ] **Get Data - Dim_City** → Get Data > Text/CSV → Select powerbi_ready/Dim_City.csv → Load
- [ ] **Get Data - City_Monthly** → Get Data > Text/CSV → Select powerbi_ready/City_Monthly.csv → Load
- [ ] **Get Data - City_Temperature** → Get Data > Text/CSV → Select powerbi_ready/City_Temperature.csv → Load
- [ ] **Get Data - City_Rainfall** → Get Data > Text/CSV → Select powerbi_ready/City_Rainfall.csv → Load
- [ ] **Get Data - City_Wind** → Get Data > Text/CSV → Select powerbi_ready/City_Wind.csv → Load
- [ ] **Get Data - City_Humidity** → Get Data > Text/CSV → Select powerbi_ready/City_Humidity.csv → Load
- [ ] **Verify import** → All 6 tables appear in Fields pane

---

## 2. Data Categories

- [ ] **Switch to Table View** → Left nav → Table view
- [ ] **Dim_City.latitude** → Select column → Column Tools > Data Category > Latitude
- [ ] **Dim_City.longitude** → Select column → Column Tools > Data Category > Longitude
- [ ] **Dim_City.city_name** → Select column → Column Tools > Data Category > City

---

## 3. Sort Columns

- [ ] **Create Dim_Date if not present** → Modeling > New Table (or import from CSV). If using DAX, paste Dim_Date formula from dax_measures.dax/POWER_BI_GUIDE
- [ ] **Switch to Dim_Date table** → Table View or Data View → Select Dim_Date
- [ ] **Sort MonthName by MonthNo** → Select MonthName → Column Tools > Sort by column > MonthNo
- [ ] **Sort MonthShort by MonthNo** → Select MonthShort → Column Tools > Sort by column > MonthNo
- [ ] **Sort Season by SeasonOrder** → Select Season → Column Tools > Sort by column > SeasonOrder
- [ ] **Add DateKey to City_Monthly** → Select City_Monthly table → Modeling > New Column → DateKey = DATE(City_Monthly[year], City_Monthly[month], 1)

---

## 4. Relationships

- [ ] **Switch to Model View** → Left nav → Model view
- [ ] **Dim_City[city_name] → City_Monthly[city_name]** → Drag drop → Cardinality: One to Many (1:*) → Cross filter direction: Single
- [ ] **Dim_Date[DateKey] → City_Monthly[DateKey]** → Drag drop → Cardinality: One to Many (1:*) → Cross filter direction: Single
- [ ] **Dim_City[city_name] → City_Temperature[city_name]** → Drag drop → Cardinality: One to One (1:1) → Cross filter direction: Single
- [ ] **Dim_City[city_name] → City_Rainfall[city_name]** → Drag drop → Cardinality: One to One (1:1) → Cross filter direction: Single
- [ ] **Dim_City[city_name] → City_Wind[city_name]** → Drag drop → Cardinality: One to One (1:1) → Cross filter direction: Single
- [ ] **Dim_City[city_name] → City_Humidity[city_name]** → Drag drop → Cardinality: One to One (1:1) → Cross filter direction: Single
- [ ] **Verify all relationships** → All use Single cross-filter direction as specified

---

## 5. Measures

- [ ] **Create _Measures table** → Home > Enter Data → Table name: _Measures → Load
- [ ] **Delete Column1** → Right-click Column1 in _Measures → Delete
- [ ] **Add Average Temperature** → New Measure in _Measures: Average Temperature = AVERAGE(City_Monthly[avg_temperature])
- [ ] **Add Maximum Temperature** → Maximum Temperature = MAX(City_Temperature[max_temperature])
- [ ] **Add Minimum Temperature** → Minimum Temperature = MIN(City_Temperature[min_temperature])
- [ ] **Add Temperature Range** → Temperature Range = [Maximum Temperature] - [Minimum Temperature]
- [ ] **Add Total Rainfall** → Total Rainfall = SUM(City_Monthly[total_precipitation])
- [ ] **Add Average Monthly Rainfall** → Average Monthly Rainfall = AVERAGE(City_Monthly[total_precipitation])
- [ ] **Add Average Humidity** → Average Humidity = AVERAGE(City_Monthly[avg_humidity])
- [ ] **Add Average Wind Speed** → Average Wind Speed = AVERAGE(City_Wind[avg_wind_speed])
- [ ] **Add Hottest City** → Use CONCATENATEX/TOPN formula per guide
- [ ] **Add Wettest City** → Use CONCATENATEX/TOPN formula per guide
- [ ] **Add Highest Humidity City** → Use CONCATENATEX/TOPN formula per guide

- [ ] **Test cross-filtering** → Click city on Map (Page 1) → Verify KPIs and charts update
- [ ] **Test Year slicer** → Change Year to 2023 → Verify data updates correctly
- [ ] **Test Season slicer** → Select Monsoon → Verify rainfall patterns
- [ ] **Test City Comparison** → Multi-select cities → Verify all visuals respond
- [ ] **Verify relationships** → Check no ambiguous paths or circular dependencies
- [ ] **Save report** → File > Save as Indian_Weather_Analytics.pbix
- [ ] **Final verification** → All 3 pages named exactly as specified: India Climate Overview, City Comparison, Seasonality & Trends
