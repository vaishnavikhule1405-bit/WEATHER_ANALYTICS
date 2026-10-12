# Dataset Consolidation & Validation Report

This report documents the verification, cleaning, and consolidation of Spark-generated analytical outputs and dimension files into `powerbi_ready/`.

---

## 1. Summary of Consolidation

| Dataset Name | Source Path | Raw File Count | Total Raw Lines (inc. header) | Data Rows (Before) | Rows (After Consolidation) | Header Row Count | Empty Rows Removed |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dim_City** | `data/cities.csv` | 1 | 51 | 50 | **50** | 1 | 0 |
| **City_Monthly** | `output/city_monthly/` | 1 | 3,201 | 3,200 | **3,200** | 1 | 0 |
| **City_Temperature** | `output/city_temperature/` | 1 | 51 | 50 | **50** | 1 | 0 |
| **City_Rainfall** | `output/city_rainfall/` | 1 | 51 | 50 | **50** | 1 | 0 |
| **City_Wind** | `output/city_wind/` | 1 | 51 | 50 | **50** | 1 | 0 |
| **City_Humidity** | `output/city_humidity/` | 1 | 51 | 50 | **50** | 1 | 0 |

---

## 2. Column Schemas, Data Types, & Null Counts

### 1. `Dim_City.csv`
- **Rows**: 50
- **Primary Key**: `city_name` (Verified 100% Unique)
- **Columns & Data Types**:
  - `rank` (Whole Number): 0 missing (0%)
  - `city_name` (Text, UTF-8): 0 missing (0%)
  - `latitude` (Decimal Number): 0 missing (0%) — Min: 8.5241, Max: 34.0837
  - `longitude` (Decimal Number): 0 missing (0%) — Min: 70.0577, Max: 91.7362
  - `population` (Whole Number): 0 missing (0%)
- **Duplicate Rows**: 0

### 2. `City_Monthly.csv`
- **Rows**: 3,200 (50 cities × 64 continuous months)
- **Granularity**: `city_name` + `year` + `month` (Unique composite key)
- **Time Horizon**: January 2020 to April 2025 (Years: 2020, 2021, 2022, 2023, 2024, 2025)
- **Columns & Data Types**:
  - `city_name` (Text, UTF-8): 0 missing (0%)
  - `year` (Whole Number): 0 missing (0%)
  - `month` (Whole Number): 0 missing (0%)
  - `avg_temperature` (Decimal Number): 0 missing (0%)
  - `avg_humidity` (Decimal Number): 0 missing (0%)
  - `total_precipitation` (Decimal Number): 0 missing (0%)
- **Duplicate Rows**: 0

### 3. `City_Temperature.csv`
- **Rows**: 50
- **Key**: `city_name` (Verified 100% Unique)
- **Columns & Data Types**:
  - `city_name` (Text, UTF-8): 0 missing (0%)
  - `avg_temperature` (Decimal Number): 0 missing (0%)
  - `max_temperature` (Decimal Number): 0 missing (0%)
  - `min_temperature` (Decimal Number): 0 missing (0%)
- **Duplicate Rows**: 0

### 4. `City_Rainfall.csv`
- **Rows**: 50
- **Key**: `city_name` (Verified 100% Unique)
- **Columns & Data Types**:
  - `city_name` (Text, UTF-8): 0 missing (0%)
  - `total_precipitation` (Decimal Number): 0 missing (0%)
  - `avg_precipitation` (Decimal Number): 0 missing (0%)
  - `max_precipitation` (Decimal Number): 0 missing (0%)
- **Duplicate Rows**: 0

### 5. `City_Wind.csv`
- **Rows**: 50
- **Key**: `city_name` (Verified 100% Unique)
- **Columns & Data Types**:
  - `city_name` (Text, UTF-8): 0 missing (0%)
  - `avg_wind_speed` (Decimal Number): 0 missing (0%)
  - `max_wind_speed` (Decimal Number): 0 missing (0%)
- **Duplicate Rows**: 0

### 6. `City_Humidity.csv`
- **Rows**: 50
- **Key**: `city_name` (Verified 100% Unique)
- **Columns & Data Types**:
  - `city_name` (Text, UTF-8): 0 missing (0%)
  - `avg_humidity` (Decimal Number): 0 missing (0%)
  - `max_humidity` (Decimal Number): 0 missing (0%)
  - `min_humidity` (Decimal Number): 0 missing (0%)
- **Duplicate Rows**: 0

---

## 3. Referential Integrity Verification

A strict referential integrity audit was conducted comparing `Dim_City[city_name]` with the city names in all analytical fact tables:
- **Total Unique Cities in Dim_City**: 50
- **Total Unique Cities in Spark Analytical Outputs**: 50
- **Cities in Dim_City missing from Spark outputs**: **0** (None)
- **Cities in Spark outputs missing from Dim_City**: **0** (None)
- **Diacritics & UTF-8 Encoding**: Special characters (e.g. `Kolkāta`, `Hyderābād`, `Sūrat`) are preserved intact with standard UTF-8-BOM encoding to prevent character corruption in Power BI and Microsoft Excel.

---

## 4. Column Content Inspection of `City_Monthly.csv`

The original Spark SQL aggregation query was inspected directly from `src/main/java/WeatherAnalytics.java` lines 211–222:
- **`avg_temperature`**: Included in `City_Monthly`
- **`max_temperature`**: Not present in `City_Monthly` (available in `City_Temperature`)
- **`min_temperature`**: Not present in `City_Monthly` (available in `City_Temperature`)
- **`avg_humidity`**: Included in `City_Monthly`
- **`total_precipitation`**: Included in `City_Monthly`
- **`avg_wind_speed`**: Not present in `City_Monthly` (available in `City_Wind`)

All decimal values preserve Spark's exact calculations without truncation or modification.
