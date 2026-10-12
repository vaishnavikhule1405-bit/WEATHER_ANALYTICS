import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

public class WeatherAnalytics {

    public static void main(String[] args) {

        // ==========================================
        // SPARK SESSION
        // ==========================================

        SparkSession spark = SparkSession.builder()
                .appName("Indian Cities Weather Analytics")
                .master("local[*]")
                .config("spark.driver.host", "127.0.0.1")
                .config("spark.driver.bindAddress", "127.0.0.1")
                .config("spark.hadoop.fs.file.impl",
                        "org.apache.hadoop.fs.RawLocalFileSystem")
                .config("spark.hadoop.fs.file.impl.disable.cache", "true")
                .config("spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version", "2")
                .config("spark.ui.enabled", "false")
                .getOrCreate();

        spark.sparkContext().setLogLevel("WARN");

        // ==========================================
        // FILE PATH
        // ==========================================

        Path projectRoot = Paths.get("").toAbsolutePath().normalize();
        Path inputFile = projectRoot.resolve("data").resolve("hourly_data.csv");
        Path outputDir = projectRoot.resolve("output");

        try {
            Files.createDirectories(outputDir);
        } catch (Exception e) {
            System.err.println("Unable to create output directory: " + outputDir);
            e.printStackTrace();
            return;
        }

        String filePath = inputFile.toString().replace('\\', '/');
        System.out.println("Reading CSV from: " + filePath);

        // ==========================================
        // 1. LOAD DATASET
        // ==========================================

        Dataset<Row> weather = spark.read()
                .option("header", "true")
                .option("inferSchema", "true")
                .csv(filePath);

        System.out.println();
        System.out.println("======================================");
        System.out.println("INDIAN CITIES WEATHER ANALYTICS");
        System.out.println("======================================");

        System.out.println("Number of rows: " + weather.count());
        System.out.println("Number of columns: " + weather.columns().length);

        // ==========================================
        // 2. SHOW SCHEMA
        // ==========================================

        System.out.println();
        System.out.println("======================================");
        System.out.println("DATASET SCHEMA");
        System.out.println("======================================");

        weather.printSchema();

        // ==========================================
        // 3. REMOVE INVALID RECORDS
        // ==========================================

        weather = weather
                .filter(weather.col("city_name").isNotNull())
                .filter(weather.col("datetime").isNotNull())
                .filter(weather.col("temperature_2m").isNotNull());

        System.out.println();
        System.out.println("Rows after cleaning: " + weather.count());

        // ==========================================
        // 4. CREATE SPARK SQL VIEW
        // ==========================================

        weather.createOrReplaceTempView("weather");

        // ==========================================
        // 5. CITY-WISE TEMPERATURE
        // ==========================================

        System.out.println();
        System.out.println("======================================");
        System.out.println("AVERAGE TEMPERATURE BY CITY");
        System.out.println("======================================");

        Dataset<Row> cityTemperature = spark.sql(
                "SELECT city_name, " +
                "ROUND(AVG(temperature_2m), 2) AS avg_temperature, " +
                "ROUND(MAX(temperature_2m), 2) AS max_temperature, " +
                "ROUND(MIN(temperature_2m), 2) AS min_temperature " +
                "FROM weather " +
                "GROUP BY city_name " +
                "ORDER BY avg_temperature DESC"
        );

        cityTemperature.show(50, false);

        // ==========================================
        // 6. CITY-WISE RAINFALL
        // ==========================================

        System.out.println();
        System.out.println("======================================");
        System.out.println("RAINFALL BY CITY");
        System.out.println("======================================");

        Dataset<Row> rainfall = spark.sql(
                "SELECT city_name, " +
                "ROUND(SUM(precipitation), 2) AS total_precipitation, " +
                "ROUND(AVG(precipitation), 2) AS avg_precipitation, " +
                "ROUND(MAX(precipitation), 2) AS max_precipitation " +
                "FROM weather " +
                "GROUP BY city_name " +
                "ORDER BY total_precipitation DESC"
        );

        rainfall.show(50, false);

        // ==========================================
        // 7. CITY-WISE HUMIDITY
        // ==========================================

        System.out.println();
        System.out.println("======================================");
        System.out.println("AVERAGE HUMIDITY BY CITY");
        System.out.println("======================================");

        Dataset<Row> humidity = spark.sql(
                "SELECT city_name, " +
                "ROUND(AVG(relative_humidity_2m), 2) AS avg_humidity, " +
                "ROUND(MAX(relative_humidity_2m), 2) AS max_humidity, " +
                "ROUND(MIN(relative_humidity_2m), 2) AS min_humidity " +
                "FROM weather " +
                "GROUP BY city_name " +
                "ORDER BY avg_humidity DESC"
        );

        humidity.show(50, false);

        // ==========================================
        // 8. WIND ANALYSIS
        // ==========================================

        System.out.println();
        System.out.println("======================================");
        System.out.println("WIND SPEED BY CITY");
        System.out.println("======================================");

        Dataset<Row> wind = spark.sql(
                "SELECT city_name, " +
                "ROUND(AVG(wind_speed_10m), 2) AS avg_wind_speed, " +
                "ROUND(MAX(wind_speed_10m), 2) AS max_wind_speed " +
                "FROM weather " +
                "GROUP BY city_name " +
                "ORDER BY avg_wind_speed DESC"
        );

        wind.show(50, false);

        // ==========================================
        // 9. MONTHLY TEMPERATURE
        // ==========================================

        System.out.println();
        System.out.println("======================================");
        System.out.println("MONTHLY TEMPERATURE ANALYSIS");
        System.out.println("======================================");

        Dataset<Row> monthlyTemperature = spark.sql(
                "SELECT " +
                "YEAR(datetime) AS year, " +
                "MONTH(datetime) AS month, " +
                "ROUND(AVG(temperature_2m), 2) AS avg_temperature, " +
                "ROUND(MAX(temperature_2m), 2) AS max_temperature, " +
                "ROUND(MIN(temperature_2m), 2) AS min_temperature " +
                "FROM weather " +
                "GROUP BY YEAR(datetime), MONTH(datetime) " +
                "ORDER BY year, month"
        );

        monthlyTemperature.show(100, false);

        // ==========================================
        // 10. CITY + MONTH ANALYSIS
        // ==========================================

        System.out.println();
        System.out.println("======================================");
        System.out.println("CITY-WISE MONTHLY TEMPERATURE");
        System.out.println("======================================");

        Dataset<Row> cityMonthly = spark.sql(
                "SELECT " +
                "city_name, " +
                "YEAR(datetime) AS year, " +
                "MONTH(datetime) AS month, " +
                "ROUND(AVG(temperature_2m), 2) AS avg_temperature, " +
                "ROUND(AVG(relative_humidity_2m), 2) AS avg_humidity, " +
                "ROUND(SUM(precipitation), 2) AS total_precipitation " +
                "FROM weather " +
                "GROUP BY city_name, YEAR(datetime), MONTH(datetime) " +
                "ORDER BY city_name, year, month"
        );

        cityMonthly.show(100, false);

        // ==========================================
        // 11. EXPORT RESULTS
        // ==========================================

        System.out.println();
        System.out.println("======================================");
        System.out.println("EXPORTING RESULTS");
        System.out.println("======================================");

        cityTemperature
                .coalesce(1)
                .write()
                .mode("overwrite")
                .option("header", "true")
                .csv(outputDir.resolve("city_temperature").toString());

        rainfall
                .coalesce(1)
                .write()
                .mode("overwrite")
                .option("header", "true")
                .csv(outputDir.resolve("city_rainfall").toString());

        humidity
                .coalesce(1)
                .write()
                .mode("overwrite")
                .option("header", "true")
                .csv(outputDir.resolve("city_humidity").toString());

        wind
                .coalesce(1)
                .write()
                .mode("overwrite")
                .option("header", "true")
                .csv(outputDir.resolve("city_wind").toString());

        monthlyTemperature
                .coalesce(1)
                .write()
                .mode("overwrite")
                .option("header", "true")
                .csv(outputDir.resolve("monthly_temperature").toString());

        cityMonthly
                .coalesce(1)
                .write()
                .mode("overwrite")
                .option("header", "true")
                .csv(outputDir.resolve("city_monthly").toString());

        // ==========================================
        // DONE
        // ==========================================

        System.out.println();
        System.out.println("======================================");
        System.out.println("ANALYSIS COMPLETED SUCCESSFULLY");
        System.out.println("Results saved in the output folder.");
        System.out.println("======================================");

        spark.stop();
    }
}
