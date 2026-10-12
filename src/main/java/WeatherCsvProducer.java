import java.util.Iterator;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Properties;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.functions;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;

public class WeatherCsvProducer {

    public static void main(String[] args) throws Exception {
        Path csvPath = args.length > 0
                ? Paths.get(args[0])
                : Paths.get("data", "hourly_data.csv");
        String bootstrapServers = setting("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092");
        String topic = setting("KAFKA_WEATHER_TOPIC", "weather.raw");
        long delayMs = Long.parseLong(setting("WEATHER_REPLAY_DELAY_MS", "0"));
        long recordLimit = Long.parseLong(setting("WEATHER_REPLAY_LIMIT", "0"));

        SparkSession spark = SparkSession.builder()
            .appName("Weather CSV Kafka Producer")
            .master("local[*]")
            .config("spark.driver.host", "127.0.0.1")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem")
            .config("spark.ui.enabled", "false")
            .getOrCreate();
        spark.sparkContext().setLogLevel("WARN");

        Dataset<Row> orderedWeather = spark.read()
            .option("header", "true")
            .schema(weatherSchema())
            .csv(csvPath.toString())
            .withColumn("event_time", functions.to_timestamp(
                functions.col("datetime"), "yyyy-MM-dd HH:mm:ss"))
            .filter(functions.col("city_name").isNotNull())
            .filter(functions.col("event_time").isNotNull())
            .filter(functions.col("temperature_2m").isNotNull())
            .orderBy(functions.col("event_time"), functions.col("city_name"))
            .drop("event_time");
        if (recordLimit > 0) {
            orderedWeather = orderedWeather.limit((int) Math.min(recordLimit, Integer.MAX_VALUE));
        }

        Properties properties = new Properties();
        properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        properties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        properties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        properties.put(ProducerConfig.ACKS_CONFIG, "all");
        properties.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");

        try (KafkaProducer<String, String> producer = new KafkaProducer<>(properties)) {
            Iterator<Row> rows = orderedWeather.toLocalIterator();
            long sent = 0;
            while (rows.hasNext()) {
                Row row = rows.next();
                String city = row.getAs("city_name");
                producer.send(new ProducerRecord<>(topic, city, toJson(row)));
                sent++;
                if (sent % 1000 == 0) {
                    producer.flush();
                    System.out.println("Published " + sent + " chronologically ordered weather records");
                }
                if (delayMs > 0) {
                    Thread.sleep(delayMs);
                }
            }
            producer.flush();
            System.out.println("Published " + sent + " chronologically ordered records to " + topic
                    + " at " + bootstrapServers);
        } finally {
            spark.stop();
        }
    }

    private static StructType weatherSchema() {
        return new StructType()
                .add("city_name", DataTypes.StringType)
                .add("datetime", DataTypes.StringType)
                .add("temperature_2m", DataTypes.DoubleType)
                .add("relative_humidity_2m", DataTypes.DoubleType)
                .add("precipitation", DataTypes.DoubleType)
                .add("wind_speed_10m", DataTypes.DoubleType);
    }

    private static String toJson(Row row) {
        return "{\"city_name\":\"" + escapeJson(row.getAs("city_name")) + "\","
                + "\"datetime\":\"" + row.getAs("datetime") + "\","
                + "\"timestamp\":" + System.currentTimeMillis() + ","
                + "\"temperature_2m\":" + number(row, "temperature_2m") + ","
                + "\"relative_humidity_2m\":" + number(row, "relative_humidity_2m") + ","
                + "\"precipitation\":" + number(row, "precipitation") + ","
                + "\"wind_speed_10m\":" + number(row, "wind_speed_10m") + "}";
    }

    private static String number(Row row, String field) {
        Double value = row.getAs(field);
        return value == null ? "null" : Double.toString(value);
    }

    private static String escapeJson(String value) {
        return value.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r");
    }

    private static String setting(String name, String fallback) {
        return System.getenv().getOrDefault(name, fallback);
    }
}