# Power BI Automation Guide

This directory contains automation assets to minimize manual work in Power BI Desktop.

## Purpose

The Spark processing is complete and the powerbi_ready/ directory contains cleaned CSV datasets, DAX measures, Power Query M scripts, theme, and validation artifacts. This powerbi_automation/ folder packages everything needed to build the final Indian_Weather_Analytics.pbix report with the exact page structure and data model required.

## Files

- **PowerQuery_AllTables.m** - Power Query M script to import all 7 tables (Dim_City, Dim_Date, City_Monthly, City_Temperature, City_Rainfall, City_Wind, City_Humidity). Contains proper column types and paths.
- **dax_measures.dax** - Complete DAX measures including corrected TOPN/CONCATENATEX formulas for text KPIs (Hottest City, Wettest City, Highest Humidity City).
- **weather_theme.json** - Custom Power BI theme for consistent styling.
- **validation_report.md** - Data quality validation report (row counts, referential integrity, schemas).
- **powerbi_checklist.md** - Click-by-click checklist covering every required action.
- **setup_instructions.md** - Step-by-step ordered instructions (Import → Data categories → Sort columns → Relationships → Measures → Theme → Page 1 → Page 2 → Page 3 → Validation).

## What Must Be Done in Power BI Desktop

Power BI Desktop (GUI) is required for:
1. **Data import & Power Query execution** - Loading CSVs and applying M transformations
2. **Data modeling** - Creating relationships in Model View (1:* and 1:1 with Single cross-filter direction)
3. **Data categorization** - Setting geographic data categories (Latitude/Longitude/City) for mapping
4. **Calculated columns** - Adding DateKey to City_Monthly if not imported via Dim_Date
5. **Creating measures table** - Building _Measures table and all DAX measures
6. **Report page layout** - Creating and positioning all visuals on the 3 required pages
7. **Visual configuration** - Setting conditional formatting, filters (Top N), slicer types, chart axes, etc.
8. **Theme application** - Applying the custom theme
9. **Validation** - Testing cross-filtering and slicers interactively

While Power Query M and DAX can be copied/pasted, the visual construction and model relationship setup must be performed in Power BI Desktop's GUI.

## Quick Start

1. Open Power BI Desktop
2. Save as C:\Projects\Weather-analytics-Bda-\Indian_Weather_Analytics.pbix
3. Follow **setup_instructions.md** step by step
4. Use **powerbi_checklist.md** to track completion
5. Validate against requirements (3 pages with exact names, specified data model)

## Source of Truth

These files are derived from powerbi_ready/POWER_BI_GUIDE.md. The Spark outputs remain unmodified.
