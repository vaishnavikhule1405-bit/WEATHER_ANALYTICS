## 7. EXACT VISUAL-BY-VISUAL CONFIGURATION FOR PAGE 2: City Comparison

### 7.1 City Slicer (Selection Bar)
- **Visual Type**: Slicer
- **Field**: Dim_City[city_name]
- **Slicer type**: Dropdown (or List) - Multi-select enabled
- **Selection**: Ctrl+Click to select multiple; default sensible selection (e.g. Mumbai, Delhi, Bangalore)
- **Search**: Enabled
- **Select All**: Enabled
- **Title**: Select Cities

### 7.2 Monthly Temperature Trajectory (Line Chart)
- **Visual Type**: Line Chart
- **X-Axis**: Dim_Date[MonthShort]
- **Y-Axis**: _Measures[Average Temperature]
- **Legend**: Dim_City[city_name]
- **Tooltips**: Dim_Date[MonthShort], Dim_Date[Year], _Measures[Average Temperature], Dim_City[city_name]
- **Sorting**: X-Axis sorted by Dim_Date[MonthNo] (ensure Sort by Column applied)
- **Markers**: Show markers on data points (recommended)
- **Title**: Monthly Average Temperature (°C)
- **Formatting**: Smooth lines, data labels off by default (on hover)

### 7.3 Extreme Temperature Range (Clustered Column Chart)
- **Visual Type**: Clustered Column Chart
- **X-Axis**: Dim_City[city_name]
- **Values (Y-Axis)**: City_Temperature[max_temperature], City_Temperature[min_temperature]
- **Legend**: On (Max vs Min)
- **Tooltips**: City_Temperature[max_temperature], City_Temperature[min_temperature], Dim_City[city_name]
- **Title**: Temperature Range (Max vs Min °C)
- **Colors**: Max #D7191C, Min #2B83BA

### 7.4 Rainfall vs Humidity Dynamics (Line and Clustered Column Chart)
- **Visual Type**: Line and Clustered Column Chart
- **X-Axis**: Dim_Date[MonthShort]
- **Column Values**: _Measures[Total Rainfall]
- **Line Values**: _Measures[Average Humidity]
- **Legend**: On
- **Tooltips**: Dim_Date[MonthShort], _Measures[Total Rainfall], _Measures[Average Humidity]
- **Sorting**: X-Axis by Dim_Date[MonthNo]
- **Title**: Rainfall vs Humidity by Month
- **Line style**: Dashed or solid; secondary Y-axis used for humidity

### 7.5 Wind Speed vs Humidity Dispersion (Scatter Chart)
- **Visual Type**: Scatter Chart
- **X-Axis**: City_Wind[avg_wind_speed]
- **Y-Axis**: City_Humidity[avg_humidity]
- **Details**: Dim_City[city_name]
- **Size**: Dim_City[population]
- **Legend**: Dim_City[city_name] (or as appropriate)
- **Tooltips**: Dim_City[city_name], City_Wind[avg_wind_speed], City_Humidity[avg_humidity], Dim_City[population]
- **Title**: Wind Speed vs Humidity (Size = Population)

---
- [ ] **Page names exact**: India Climate Overview, City Comparison, Seasonality & Trends (3 pages total)
- [ ] **Data unchanged**: No modifications to Spark outputs (output/) or source CSVs
- [ ] **Save**: File > Save as C:\Projects\Weather-analytics-Bda-\Indian_Weather_Analytics.pbix
- [ ] **Final review**: All visuals render, formatting consistent, interactions working
