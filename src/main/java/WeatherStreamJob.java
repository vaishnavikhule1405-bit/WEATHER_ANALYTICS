import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.spark.api.java.function.VoidFunction2;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;
import org.apache.spark.sql.functions;
import org.apache.spark.sql.streaming.StreamingQuery;
import org.apache.spark.sql.streaming.Trigger;

public class WeatherStreamJob {

    private static KafkaProducer<String, String> kafkaProducer = null;
    private static String outputTopic = null;

    public static void main(String[] args) throws Exception {
        String bootstrapServers = setting("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092");
        String topic = setting("KAFKA_WEATHER_TOPIC", "weather.raw");
        outputTopic = setting("KAFKA_OUTPUT_TOPIC", "weather.analytics");
        Path outputPath = Paths.get(setting("WEATHER_STREAM_OUTPUT", "output/streaming/latest.csv"))
                .toAbsolutePath().normalize();
=======
        Path outputPath = Paths.get(setting("WEATHER_STREAM_OUTPUT", "output/streaming/latest.csv"))
                .toAbsolutePath().normalize();
>>>>>>> 494eb012c67aa314f543bac7c562cf03984b6b36
        Path checkpointDirectory = Paths.get(setting("WEATHER_STREAM_CHECKPOINT", "output/streaming/checkpoint"))
                .toAbsolutePath().normalize();

        boolean enableKafkaOutput = outputTopic != null && !outputTopic.trim().isEmpty() && !outputTopic.equalsIgnoreCase("none");
        if (enableKafkaOutput) {
            Properties props = new Properties();
            props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
            props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
            props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
            props.put(ProducerConfig.ACKS_CONFIG, "1");
            kafkaProducer = new KafkaProducer<>(props);
            System.out.println("Publishing streaming analytics to Kafka topic: " + outputTopic);
        }

        SparkSession spark = SparkSession.builder()
                .appName("Weather Kafka Streaming Analytics")
                .master("local[*]")
                .config("spark.driver.host", "127.0.0.1")
                .config("spark.driver.bindAddress", "127.0.0.1")
                .config("spark.ui.enabled", "false")
                .getOrCreate();
        spark.sparkContext().setLogLevel("WARN");

        StructType messageSchema = new StructType()
                .add("city_name", DataTypes.StringType)
                .add("datetime", DataTypes.StringType)
                .add("temperature_2m", DataTypes.DoubleType)
                .add("relative_humidity_2m", DataTypes.DoubleType)
                .add("precipitation", DataTypes.DoubleType)
                .add("wind_speed_10m", DataTypes.DoubleType);

        Dataset<Row> records = spark.readStream()
                .format("kafka")
                .option("kafka.bootstrap.servers", bootstrapServers)
                .option("subscribe", topic)
                .option("startingOffsets", "earliest")
                .load()
                .select(functions.from_json(functions.col("value").cast("string"), messageSchema)
                        .alias("weather"))
                .select("weather.*")
                .withColumn("event_time", functions.to_timestamp(
                        functions.col("datetime"), "yyyy-MM-dd HH:mm:ss"))
                .filter(functions.col("city_name").isNotNull())
                .filter(functions.col("event_time").isNotNull())
                .filter(functions.col("temperature_2m").isNotNull());

        Dataset<Row> metrics = records
                .withWatermark("event_time", "10 minutes")
                .groupBy(functions.window(functions.col("event_time"), "5 minutes"),
                        functions.col("city_name"))
                .agg(
                        functions.round(functions.avg("temperature_2m"), 2).alias("avg_temperature"),
                        functions.round(functions.max("temperature_2m"), 2).alias("max_temperature"),
                        functions.round(functions.min("temperature_2m"), 2).alias("min_temperature"),
                        functions.round(functions.avg("relative_humidity_2m"), 2).alias("avg_humidity"),
                        functions.round(functions.sum("precipitation"), 2).alias("total_precipitation"),
                        functions.round(functions.avg("wind_speed_10m"), 2).alias("avg_wind_speed"));

        StreamingQuery query = metrics.writeStream()
                .outputMode("append")
                .option("checkpointLocation", checkpointDirectory.toString())
                .trigger(Trigger.ProcessingTime(2000))
                .foreachBatch((VoidFunction2<Dataset<Row>, Long>)
                    (batch, batchId) -> publishLatestByCity(batch, outputPath, batchId))
                .start();

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try {
                if (kafkaProducer != null) {
                    kafkaProducer.flush();
                    kafkaProducer.close();
                }
                query.stop();
                spark.stop();
            } catch (Exception ignored) {
            }
        }));

        System.out.println("Consuming " + topic + " from " + bootstrapServers);
        System.out.println("Latest city-window snapshot CSV: " + outputPath);
        query.awaitTermination();
    }

    private static void publishLatestByCity(Dataset<Row> batch, Path outputFile, long batchId)
            throws Exception {
        List<Row> rows = batch.collectAsList();
        if (rows.isEmpty()) {
            return;
        }

        Map<String, Snapshot> latestByCity = readSnapshots(outputFile);
        for (Row row : rows) {
            String city = row.getAs("city_name");
            Row window = row.getAs("window");
            Timestamp windowStart = window.getAs("start");
            Timestamp windowEnd = window.getAs("end");
            String snapshot = toJson(row, city, windowStart, windowEnd);
            Snapshot existing = latestByCity.get(city);
            Instant end = windowEnd.toInstant();
            if (existing == null || end.compareTo(existing.windowEnd()) >= 0) {
                latestByCity.put(city, new Snapshot(end, toCsv(row, city, windowStart, windowEnd)));
            }
            if (kafkaProducer != null) {
                kafkaProducer.send(new ProducerRecord<>(outputTopic, city, snapshot));
            }
        }

        StringBuilder csv = new StringBuilder(CSV_HEADER).append('\n');
        for (Snapshot snapshot : latestByCity.values()) {
            csv.append(snapshot.csvRow()).append('\n');
        }
=======
            Snapshot existing = latestByCity.get(city);
            Instant end = windowEnd.toInstant();
            if (existing == null || end.compareTo(existing.windowEnd()) >= 0) {
                latestByCity.put(city, new Snapshot(end, toCsv(row, city, windowStart, windowEnd)));
            }
        }

        StringBuilder csv = new StringBuilder(CSV_HEADER).append('\n');
        for (Snapshot snapshot : latestByCity.values()) {
            csv.append(snapshot.csvRow()).append('\n');
        }
>>>>>>> 494eb012c67aa314f543bac7c562cf03984b6b36
        writeAtomically(outputFile, csv.toString());
        System.out.println("Published latest windows for " + latestByCity.size()
                + " cities (batch " + batchId + ")");
    }

    private static String toJson(Row row, String city, Timestamp start, Timestamp end) {
        return "{\"city_name\":\"" + escapeJson(city) + "\","
                + "\"window_start\":\"" + start.toInstant() + "\","
                + "\"window_end\":\"" + end.toInstant() + "\","
                + "\"timestamp\":" + System.currentTimeMillis() + ","
                + "\"avg_temperature\":" + number(row, "avg_temperature") + ","
                + "\"max_temperature\":" + number(row, "max_temperature") + ","
                + "\"min_temperature\":" + number(row, "min_temperature") + ","
                + "\"avg_humidity\":" + number(row, "avg_humidity") + ","
                + "\"total_precipitation\":" + number(row, "total_precipitation") + ","
                + "\"avg_wind_speed\":" + number(row, "avg_wind_speed") + "}";
    }

    private record Snapshot(Instant windowEnd, String csvRow) {}

    private static final String CSV_HEADER =
    private record Snapshot(Instant windowEnd, String csvRow) {}

    private static final String CSV_HEADER =
            "city_name,window_start,window_end,avg_temperature,max_temperature,"
            + "min_temperature,avg_humidity,total_precipitation,avg_wind_speed";

    private static String toCsv(Row row, String city, Timestamp start, Timestamp end) {
        return escapeCsv(city) + ","
                + start.toInstant() + ","
                + end.toInstant() + ","
                + number(row, "avg_temperature") + ","
                + number(row, "max_temperature") + ","
                + number(row, "min_temperature") + ","
                + number(row, "avg_humidity") + ","
                + number(row, "total_precipitation") + ","
                + number(row, "avg_wind_speed");
    }

    private static Map<String, Snapshot> readSnapshots(Path outputFile) throws IOException {
        Map<String, Snapshot> snapshots = new TreeMap<>();
        if (!Files.exists(outputFile)) {
            return snapshots;
        }

        List<String> lines = Files.readAllLines(outputFile, StandardCharsets.UTF_8);
        if (lines.isEmpty() || !CSV_HEADER.equals(lines.get(0))) {
            throw new IOException("Unexpected streaming CSV header in " + outputFile);
        }
        for (int i = 1; i < lines.size(); i++) {
            List<String> fields = parseCsvLine(lines.get(i));
            if (fields.size() != 9) {
                throw new IOException("Malformed streaming CSV row " + (i + 1) + " in " + outputFile);
            }
            try {
                snapshots.put(fields.get(0),
                        new Snapshot(Instant.parse(fields.get(2)), lines.get(i)));
            } catch (DateTimeParseException exception) {
                throw new IOException("Invalid window_end in streaming CSV row " + (i + 1)
                        + " in " + outputFile, exception);
            }
        }
        return snapshots;
    }

    private static List<String> parseCsvLine(String line) throws IOException {
        List<String> fields = new ArrayList<>();
        StringBuilder field = new StringBuilder();
        boolean quoted = false;
        for (int i = 0; i < line.length(); i++) {
            char character = line.charAt(i);
            if (character == '"') {
                if (quoted && i + 1 < line.length() && line.charAt(i + 1) == '"') {
                    field.append('"');
                    i++;
                } else {
                    quoted = !quoted;
                }
            } else if (character == ',' && !quoted) {
                fields.add(field.toString());
                field.setLength(0);
            } else {
                field.append(character);
            }
        }
        if (quoted) {
            throw new IOException("Unclosed quoted field in streaming CSV");
        }
        fields.add(field.toString());
        return fields;
<<<<<<< HEAD
>>>>>>> 494eb012c67aa314f543bac7c562cf03984b6b36
=======
>>>>>>> 494eb012c67aa314f543bac7c562cf03984b6b36
    }

    private static String number(Row row, String field) {
        Number value = row.getAs(field);
        return value == null ? "" : String.format(Locale.ROOT, "%.2f", value.doubleValue());
    }

    private static void writeAtomically(Path target, String content) throws IOException {
        Files.createDirectories(target.toAbsolutePath().getParent());
        Path temporary = target.resolveSibling(target.getFileName() + ".tmp");
        Files.writeString(temporary, content, StandardCharsets.UTF_8);
        try {
            Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING,
                    StandardCopyOption.ATOMIC_MOVE);
        } catch (Exception exception) {
            try {
                Files.deleteIfExists(target);
                Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING);
            } catch (Exception fallback) {
                Files.writeString(target, content, StandardCharsets.UTF_8);
                try {
                    Files.deleteIfExists(temporary);
                } catch (Exception ignored) {
                }
            }
        }
    }

    private static String escapeCsv(String value) {
        if (value.contains(",") || value.contains("\"") || value.contains("\n") || value.contains("\r")) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }
        return value;
    }

    private static String setting(String name, String fallback) {
        return System.getenv().getOrDefault(name, fallback);
    }
}