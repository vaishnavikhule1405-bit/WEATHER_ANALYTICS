# Grafana Real-Time Kafka Visualization Guide
## Indian Cities Weather & Climate Streaming Analytics

This guide describes how to visualize the continuous streaming output produced by Apache Kafka and Apache Spark in Grafana using the direct Kafka data source plugin.

---

## 1. Architecture Overview

```
┌────────────────────────┐
│  data/hourly_data.csv  │
└───────────┬────────────┘
            │
            ▼ (Chronological Event-Time Replay)
┌────────────────────────┐
│   WeatherCsvProducer   │
└───────────┬────────────┘
            │ (Continuous Stream)
            ▼
┌────────────────────────────────────────────────────────┐
│                  Apache Kafka (KRaft)                  │
│                                                        │
│  Topic: weather.raw          Topic: weather.analytics  │
│  (Raw City Observations)     (Spark Windowed Metrics)  │
└───────────┬────────────────────────────▲───────────────┘
            │                            │
            │ (Consume)                  │ (Publish aggregations)
            ▼                            │
┌────────────────────────────────────────┴───────────────┐
│        WeatherStreamJob (Spark Structured Streaming)   │
│        - 5-minute tumbling/sliding event-time windows  │
│        - Min/Avg/Max Temp, Avg Humidity, Wind, Rain    │
└────────────────────────────────────────────────────────┘
            │
            ▼ (Continuous Direct Consumer)
┌────────────────────────────────────────────────────────┐
│                  Grafana Dashboard                     │
│  - hamedkarbasi93-kafka-datasource Plugin              │
│  - Port 3000 (http://localhost:3000)                   │
│  - Auto-provisioned Datasource & Dashboard             │
└────────────────────────────────────────────────────────┘
```

### Components

1. **Kafka Broker (`apache/kafka:4.0.0`)**: Runs in Docker with dual listeners:
   - `localhost:9092`: Exposed to Windows host for Spark and producer jobs.
   - `kafka:29092`: Internal Docker network listener for Grafana.
2. **Grafana (`grafana/grafana:10.4.0`)**: Runs in Docker with pre-installed `hamedkarbasi93-kafka-datasource` plugin.
3. **Kafka Topics**:
   - `weather.raw`: Continuous raw observation feed published by `WeatherCsvProducer`.
   - `weather.analytics`: Continuous 5-minute aggregated metrics published by `WeatherStreamJob`.

---

## 2. Quick Start

### Step 1: Start Docker Services (Kafka + Grafana)

Make sure Docker Desktop is running, then run in PowerShell:

```powershell
docker compose up -d
```

Verify both containers are healthy:

```powershell
docker compose ps
```

You should see:
- `kafka` on port `9092`
- `weather_grafana` on port `3000`

### Step 2: Open Grafana

Open your browser and navigate to:
```
http://localhost:3000
```

- **Username**: `admin`
- **Password**: `admin`

The data source and dashboard are automatically provisioned. Navigate to:
**Dashboards** > **Weather Analytics** > **Indian Cities Weather - Real-Time Kafka Stream**.

---

## 3. Streaming Data into Kafka

### Terminal 1: Start Spark Streaming Consumer

Open PowerShell in the project root:

```powershell
$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot"
$env:HADOOP_HOME = "C:\hadoop"
$env:PATH = "$env:JAVA_HOME\bin;$env:HADOOP_HOME\bin;$env:PATH"
$env:WEATHER_STREAM_CHECKPOINT = "output/streaming/checkpoint-replay"

mvn -DskipTests compile exec:java "-Dexec.mainClass=WeatherStreamJob"
```

*Note: Update `JAVA_HOME` and `HADOOP_HOME` if installed in different directories on your machine.*

### Terminal 2: Start Continuous CSV Replay Producer

Open a second PowerShell window:

```powershell
$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot"
$env:HADOOP_HOME = "C:\hadoop"
$env:PATH = "$env:JAVA_HOME\bin;$env:HADOOP_HOME\bin;$env:PATH"

# Replay up to 20,000 records with 100ms pacing for continuous streaming:
$env:WEATHER_REPLAY_LIMIT = "20000"
$env:WEATHER_REPLAY_DELAY_MS = "100"

mvn -DskipTests compile exec:java "-Dexec.mainClass=WeatherCsvProducer"
```

As soon as the producer publishes messages, switch to Grafana at `http://localhost:3000` to watch the live streaming visualizations!

---

## 4. Provisioned Dashboard Panels

The dashboard (`weather-kafka-live`) contains:

| Section | Panel Name | Type | Topic | Description |
| :--- | :--- | :--- | :--- | :--- |
| **KPIs** | Kafka Broker Status | Stat | `weather.raw` | Displays active connection to the Kafka stream |
| **KPIs** | Latest Active City | Stat | `weather.raw` | Current city record being ingested |
| **KPIs** | Live Temperature | Stat | `weather.raw` | Current temperature (°C) with color alerts |
| **KPIs** | Live Humidity | Stat | `weather.raw` | Current relative humidity (%) |
| **KPIs** | Live Wind Speed | Stat | `weather.raw` | Current wind velocity (km/h) |
| **KPIs** | Live Precipitation | Stat | `weather.raw` | Current rainfall (mm) |
| **Raw Stream** | Live Temperature Stream | Time Series | `weather.raw` | Real-time smooth trend line of incoming temperatures |
| **Raw Stream** | Humidity & Wind Dynamics | Time Series | `weather.raw` | Dual series tracking atmospheric humidity and wind |
| **Analytics** | Windowed Temperature Analytics | Time Series | `weather.analytics` | Min, Avg, and Max temperatures calculated by Spark |
| **Analytics** | Rain & Wind Gauges | Gauge | `weather.analytics` | Visual gauges for wind speed and rainfall intensity |
| **Live Feeds** | Live Observation Feed | Table | `weather.raw` | Tabular stream of raw events with heat-map color cells |
| **Live Feeds** | Aggregated Analytics Feed | Table | `weather.analytics` | Tabular stream of 5-min window summaries across cities |

---

## 5. Configuration Reference

### Docker Compose (`docker-compose.yml`)

The Kafka service configures dual listeners to ensure both host processes and Docker containers communicate with Kafka without conflicts:

```yaml
environment:
  KAFKA_LISTENERS: PLAINTEXT://:9092,PLAINTEXT_INTERNAL://:29092,CONTROLLER://:9093
  KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092,PLAINTEXT_INTERNAL://kafka:29092
  KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_INTERNAL:PLAINTEXT
```

Grafana installs the Kafka datasource plugin automatically:

```yaml
environment:
  - GF_SECURITY_ADMIN_USER=admin
  - GF_SECURITY_ADMIN_PASSWORD=admin
  - GF_INSTALL_PLUGINS=hamedkarbasi93-kafka-datasource
  - GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=hamedkarbasi93-kafka-datasource
```

### Datasource Provisioning (`grafana/provisioning/datasources/datasources.yaml`)

```yaml
apiVersion: 1
datasources:
  - name: Kafka
    type: hamedkarbasi93-kafka-datasource
    uid: kafka-datasource
    access: proxy
    isDefault: true
    editable: true
    jsonData:
      bootstrapServers: "kafka:29092"
```

### Creating Custom Panels in Grafana

If you want to build custom panels in Grafana:
1. Click **Add panel** > **Add a new panel**.
2. Select data source **Kafka**.
3. In query editor:
   - **Topic**: `weather.raw` or `weather.analytics`
   - **Partition**: `all`
   - **Message Format**: `json`
   - **Offset Reset**: `latest`
   - **Timestamp Mode**: `now` (or `message`)
4. In panel settings, choose visualization (Time series, Stat, Gauge, Bar chart, Table).
5. Apply field units (e.g., `Temperature > Celsius`, `Velocity > km/h`, `Humidity > %`).

---

## 6. Maintenance & Reset

### Stopping Services
```powershell
docker compose stop
```

### Discarding Streaming Progress & Resetting Kafka Data
```powershell
Remove-Item -Recurse -Force output/streaming
docker compose down -v
```
