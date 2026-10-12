# Power BI Setup Instructions (Ordered)

Follow these steps in order. Refer to powerbi_checklist.md for a click-by-click breakdown.

## 1. Import

1. Launch Power BI Desktop
2. Save the file as Indian_Weather_Analytics.pbix in C:\Projects\Weather-analytics-Bda-\
3. Import all 6 CSV files from powerbi_ready/: Dim_City.csv, City_Monthly.csv, City_Temperature.csv, City_Rainfall.csv, City_Wind.csv, City_Humidity.csv (via Get Data > Text/CSV)
4. Open Power Query Editor (Transform Data) to review imported tables

---

## 2. Data Categories

1. Go to Table View (left navigation)
2. Select Dim_City table
3. Set latitude → Data Category: Latitude
4. Set longitude → Data Category: Longitude
5. Set city_name → Data Category: City

---

## 3. Sort Columns

1. Ensure Dim_Date exists (import from powerbi_ready/Dim_Date.csv or create via DAX)
2. In Table View, select Dim_Date table
3. Select MonthName → Column Tools > Sort by column → MonthNo
4. Select MonthShort → Column Tools > Sort by column → MonthNo
5. Select Season → Column Tools > Sort by column → SeasonOrder
6. Add calculated column to City_Monthly: DateKey = DATE(City_Monthly[year], City_Monthly[month], 1)

---

## 4. Relationships

Switch to Model View. Create all relationships with Single cross-filter direction:
1. Dim_City[city_name] (1) → City_Monthly[city_name] (*) 
2. Dim_Date[DateKey] (1) → City_Monthly[DateKey] (*)
3. Dim_City[city_name] (1) → City_Temperature[city_name] (1)
4. Dim_City[city_name] (1) → City_Rainfall[city_name] (1)
5. Dim_City[city_name] (1) → City_Wind[city_name] (1)
6. Dim_City[city_name] (1) → City_Humidity[city_name] (1)

---

## 5. Measures

1. Home > Enter Data → Table name: _Measures → Load
2. Delete default Column1 from _Measures
3. For each measure in dax_measures.dax, add as New Measure in _Measures

---

## 6. Theme

1. View ribbon > Themes
2. Import powerbi_automation/weather_theme.json

---

## 7. Page 1: India Climate Overview

1. Rename Page 1 to India Climate Overview
2. Add title: Indian Cities Weather and Climate Analytics (Apache Spark Pipeline)
3. Add 6 KPI cards for the required measures
4. Add Map visual with lat/lon, sized by Total Rainfall, colored by Average Temperature gradient
5. Add Top 10 Hottest Cities clustered bar (Top N by Maximum Temperature)
6. Add Top 10 Rainiest Cities clustered bar (Top N by Total Rainfall)
7. Add slicers: Year (tile), Season (dropdown), City (dropdown searchable)

---

## 8. Page 2: City Comparison

1. Add new page → rename to City Comparison
2. Add multi-select City slicer
3. Add Line chart: Average Temperature by MonthShort, legend by City
4. Add Clustered column chart: Max and Min temperature by City
5. Add Line and clustered column chart: Total Rainfall (columns) vs Average Humidity (line) by MonthShort
6. Add Scatter chart: avg_wind_speed vs avg_humidity, size by population, details/color by City

---

## 9. Page 3: Seasonality & Trends

1. Add new page → rename to Seasonality & Trends
2. Add Area chart: Total Rainfall by MonthShort
3. Add Matrix heatmap: Cities × Months showing Average Temperature with 3-color gradient
4. Add Donut chart: Total Rainfall by Season
5. Add Line chart: Average Temperature by Year

---

## 10. Validation

1. Test cross-filtering from map
2. Test Year slicer (e.g., 2023)
3. Test Season slicer (Monsoon)
4. Test multi-select on City Comparison
5. Verify all relationships have Single cross-filter direction
6. Save as Indian_Weather_Analytics.pbix
7. Confirm exact page names: India Climate Overview, City Comparison, Seasonality & Trends
