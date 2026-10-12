// =============================================================================
// POWER QUERY (M) AUTOMATED IMPORT — ALL 7 TABLES
// =============================================================================
// In Power BI Desktop: Home > Get Data > Blank Query > Advanced Editor
// Paste each query block below into a separate Blank Query.
// Rename each query to the table name shown in the comment header.
//
// IMPORTANT: After pasting all 7 queries, click Close & Apply.
// =============================================================================

// =====================================================================
// TABLE 1: Dim_City  (50 rows — Dimension table with coordinates)
// =====================================================================
// Query Name: Dim_City
let
    Source = Csv.Document(
        File.Contents("C:\Projects\Weather-analytics-Bda-\powerbi_ready\Dim_City.csv"),
        [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"rank", Int64.Type},
        {"city_name", type text},
        {"latitude", type number},
        {"longitude", type number},
        {"population", Int64.Type}
    })
in
    #"Changed Type"


// =====================================================================
// TABLE 2: Dim_Date  (64 rows — Unique monthly dates, NOT daily)
// =====================================================================
// Query Name: Dim_Date
let
    Source = Csv.Document(
        File.Contents("C:\Projects\Weather-analytics-Bda-\powerbi_ready\Dim_Date.csv"),
        [Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"DateKey", type date},
        {"Year", Int64.Type},
        {"MonthNo", Int64.Type},
        {"MonthName", type text},
        {"MonthShort", type text},
        {"Quarter", type text},
        {"YearMonth", type text},
        {"Season", type text},
        {"SeasonOrder", Int64.Type}
    })
in
    #"Changed Type"


// =====================================================================
// TABLE 3: City_Monthly  (3200 rows — Primary fact table with DateKey)
// =====================================================================
// Query Name: City_Monthly
let
    Source = Csv.Document(
        File.Contents("C:\Projects\Weather-analytics-Bda-\powerbi_ready\City_Monthly.csv"),
        [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"city_name", type text},
        {"year", Int64.Type},
        {"month", Int64.Type},
        {"avg_temperature", type number},
        {"avg_humidity", type number},
        {"total_precipitation", type number},
        {"DateKey", type date}
    })
in
    #"Changed Type"


// =====================================================================
// TABLE 4: City_Temperature  (50 rows — Overall temp metrics per city)
// =====================================================================
// Query Name: City_Temperature
let
    Source = Csv.Document(
        File.Contents("C:\Projects\Weather-analytics-Bda-\powerbi_ready\City_Temperature.csv"),
        [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"city_name", type text},
        {"avg_temperature", type number},
        {"max_temperature", type number},
        {"min_temperature", type number}
    })
in
    #"Changed Type"


// =====================================================================
// TABLE 5: City_Rainfall  (50 rows — Precipitation metrics per city)
// =====================================================================
// Query Name: City_Rainfall
let
    Source = Csv.Document(
        File.Contents("C:\Projects\Weather-analytics-Bda-\powerbi_ready\City_Rainfall.csv"),
        [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"city_name", type text},
        {"total_precipitation", type number},
        {"avg_precipitation", type number},
        {"max_precipitation", type number}
    })
in
    #"Changed Type"


// =====================================================================
// TABLE 6: City_Wind  (50 rows — Wind speed metrics per city)
// =====================================================================
// Query Name: City_Wind
let
    Source = Csv.Document(
        File.Contents("C:\Projects\Weather-analytics-Bda-\powerbi_ready\City_Wind.csv"),
        [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"city_name", type text},
        {"avg_wind_speed", type number},
        {"max_wind_speed", type number}
    })
in
    #"Changed Type"


// =====================================================================
// TABLE 7: City_Humidity  (50 rows — Humidity metrics per city)
// =====================================================================
// Query Name: City_Humidity
let
    Source = Csv.Document(
        File.Contents("C:\Projects\Weather-analytics-Bda-\powerbi_ready\City_Humidity.csv"),
        [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"city_name", type text},
        {"avg_humidity", type number},
        {"max_humidity", type number},
        {"min_humidity", type number}
    })
in
    #"Changed Type"
