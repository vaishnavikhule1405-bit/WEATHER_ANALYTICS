# Weather Analytics Big Data Project

Apache Spark and Java process hourly weather data for Indian cities. The project includes a historical batch pipeline and a Kafka-based streaming pipeline that uses a local CSV dataset as its source. Real-time streaming analytics can be visualized directly in **Grafana**, and batch datasets are modeled for **Power BI**.

For full Grafana streaming setup and dashboard details, see [GRAFANA_GUIDE.md](file:///c:/Projects/Weather-analytics-Bda-/GRAFANA_GUIDE.md). For Power BI star schema and modeling details, see [powerbi_ready/POWER_BI_GUIDE.md](file:///c:/Projects/Weather-analytics-Bda-/powerbi_ready/POWER_BI_GUIDE.md).

## Batch Analytics (no Kafka required)

The large input file `data/hourly_data.csv` is excluded from this repository because it exceeds GitHub's file size limit. Obtain the dataset separately and place it at that path before running the batch or streaming pipelines.

Open PowerShell in the repository root (the directory containing `pom.xml`). Set Java 17 and Hadoop for that terminal, then verify Maven is using Java 17:

```powershell
$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot"
$env:HADOOP_HOME = "C:\hadoop"
$env:PATH = "$env:JAVA_HOME\bin;$env:HADOOP_HOME\bin;$env:PATH"
mvn -version
```

If Java 17 or Hadoop is installed elsewhere, change `JAVA_HOME` or `HADOOP_HOME` to its installation directory. `HADOOP_HOME` points to the Hadoop root; its `bin` directory is added to `PATH`.

Run the batch analysis:

```powershell
mvn clean compile exec:java "-Dexec.mainClass=WeatherAnalytics"
```

This reads `data/hourly_data.csv`, prints summary tables, and overwrites the six analytical CSV output folders under `output/`: `city_temperature`, `city_rainfall`, `city_humidity`, `city_wind`, `monthly_temperature`, and `city_monthly`. The monthly datasets keep separate `year` and `month` columns. Kafka and Docker are not needed for this batch run.

## Kafka Streaming & Real-Time Grafana Visualization

The demo replays CSV rows to Kafka, calculates five-minute event-time windows in Spark Structured Streaming, publishes aggregated metrics back to Kafka topic `weather.analytics`, and maintains a single readable CSV snapshot at `output/streaming/latest.csv`. The file has a header and one row per city, sorted by city name; each row contains that city's latest finalized window. Spark checkpoints Kafka progress separately in `output/streaming/checkpoint/`.

If you previously ran a version that wrote one file per city, those old snapshots may still be in `output/streaming/latest/`. They are no longer used; remove that legacy folder after stopping the old streaming job if you want to clear them.

Set `WEATHER_STREAM_OUTPUT` to change the snapshot CSV file path. Set `WEATHER_STREAM_CHECKPOINT` to change the checkpoint directory.

Start Kafka and Grafana (Docker Desktop must be running):

```powershell
docker compose up -d
```

- **Grafana URL**: [http://localhost:3000](http://localhost:3000)
- **Login**: `admin` / `admin`
- **Dashboard**: Pre-provisioned under *Dashboards* > *Weather Analytics* > *Indian Cities Weather - Real-Time Kafka Stream*.

In terminal 1, start Spark:

```powershell
$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot"
$env:HADOOP_HOME = "C:\hadoop"
$env:PATH = "$env:JAVA_HOME\bin;$env:HADOOP_HOME\bin;$env:PATH"
$env:WEATHER_STREAM_CHECKPOINT = "output/streaming/checkpoint-replay"
mvn -version
mvn -DskipTests compile exec:java "-Dexec.mainClass=WeatherStreamJob"
```

In terminal 2, replay up to 20,000 rows at a gentle pace:

```powershell
$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot"
$env:HADOOP_HOME = "C:\hadoop"
$env:PATH = "$env:JAVA_HOME\bin;$env:HADOOP_HOME\bin;$env:PATH"
mvn -version
$env:WEATHER_REPLAY_LIMIT = "20000"
$env:WEATHER_REPLAY_DELAY_MS = "5"
mvn -DskipTests compile exec:java "-Dexec.mainClass=WeatherCsvProducer"
```

Change `JAVA_HOME` or `HADOOP_HOME` in each terminal if your installations are in different directories. Confirm `mvn -version` reports Java 17 in both terminals. `HADOOP_HOME` is the Hadoop installation root (for example, `C:\hadoop`); add its `bin` directory to `PATH` so the Hadoop native libraries can be loaded. The checkpoint path above preserves the offsets and state from this run; use the same path when restarting this consumer.

The producer uses Spark to sort records globally by event time before publishing them. This matters because the CSV is grouped by city; replaying it in file order would make later cities' older observations look late to Spark's watermark. Spark's sort uses disk as needed rather than loading the entire file into Java memory.

Leave `WEATHER_REPLAY_LIMIT` unset or set it to `0` to replay the full CSV. Set `WEATHER_REPLAY_DELAY_MS` to `0` for an unthrottled replay. The producer defaults to Kafka at `localhost:9092` and topic `weather.raw`; configure `KAFKA_BOOTSTRAP_SERVERS` or `KAFKA_WEATHER_TOPIC` to change these. If Hadoop is installed somewhere other than `C:\hadoop`, set `HADOOP_HOME` to its local installation directory.

When the producer finishes, stop the streaming consumer with `Ctrl+C`, then stop Kafka while keeping its stored data:

```powershell
docker compose stop kafka
```

Only if you intentionally want to discard all streaming progress and Kafka data and replay from scratch, reset them:

```powershell
Remove-Item -Recurse -Force output/streaming
docker compose down -v
```

The existing CSV is the source for both batch and streaming analytics; no external weather API is required.