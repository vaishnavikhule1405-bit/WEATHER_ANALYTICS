import json
import time
import sys
from datetime import datetime, timezone, timedelta
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = ['localhost:9092']
TOPIC_RAW        = 'weather.raw'
TOPIC_ANALYTICS  = 'weather.analytics'

# ── Timing ──────────────────────────────────────────────────────────────────
# Each record gets a simulated event-timestamp 30 seconds ahead of the
# previous one.  This spreads data points evenly across the Grafana X-axis
# (30-min window = 60 distinct buckets @ 30s each).
#
# Real-world send rate: one record every 2 real seconds so the chart
# fills quickly while remaining stable (no flicker).
EVENT_STEP_SEC  = 30   # simulated time gap between consecutive records
SEND_DELAY_SEC  = 2    # real wall-clock seconds between sends

def main():
    print("=" * 65)
    print("  KAFKA TIME-SERIES WEATHER STREAM  (30-s event cadence)")
    print("  Real send rate : 1 record / 2 seconds")
    print("  Simulated step : 30 seconds per record")
    print("  Topics         : " + TOPIC_RAW + "  |  " + TOPIC_ANALYTICS)
    print("  Grafana        : http://localhost:3000")
    print("=" * 65)

    # ── Connect ──────────────────────────────────────────────────────────────
    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Connected to Kafka on " + str(BOOTSTRAP_SERVERS))
    except Exception as e:
        print("ERROR: Could not connect to Kafka:", e)
        sys.exit(1)

    # ── Load dataset ─────────────────────────────────────────────────────────
    with open("data/stream_feed_7days.json", "r", encoding="utf-8") as f:
        records = json.load(f)
    total_records = len(records)
    print(f"Loaded {total_records} chronological weather records.\n")
    print("Streaming live to Kafka... (Press Ctrl+C to stop)\n")

    # ── State ─────────────────────────────────────────────────────────────────
    city_windows = {}      # sliding window of last 10 obs per city
    sent_count   = 0
    idx          = 0

    # Simulated event time starts 10 minutes ago so the chart fills immediately
    sim_time = datetime.now(tz=timezone.utc) - timedelta(minutes=10)

    try:
        while True:
            event = records[idx]
            idx   = (idx + 1) % total_records
            sent_count += 1

            city   = event["city_name"]
            temp   = float(event["temperature_2m"])
            hum    = float(event["relative_humidity_2m"])
            precip = float(event["precipitation"])
            wind   = float(event["wind_speed_10m"])

            # ── Simulated event timestamp (30s per step) ──────────────────────
            evt_ms = int(sim_time.timestamp() * 1000)
            sim_time += timedelta(seconds=EVENT_STEP_SEC)

            # ── Raw observation → weather.raw ─────────────────────────────────
            raw_payload = {
                "city_name"            : city,
                "datetime"             : sim_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "timestamp"            : evt_ms,
                "temperature_2m"       : temp,
                "relative_humidity_2m" : hum,
                "precipitation"        : precip,
                "wind_speed_10m"       : wind
            }
            producer.send(TOPIC_RAW, key=city.encode('utf-8'), value=raw_payload)

            # ── Sliding window analytics (last 10 obs per city) ───────────────
            if city not in city_windows:
                city_windows[city] = []
            c_hist = city_windows[city]
            c_hist.append({"t": temp, "h": hum, "p": precip, "w": wind})
            if len(c_hist) > 10:
                c_hist.pop(0)

            avg_t = round(sum(x["t"] for x in c_hist) / len(c_hist), 2)
            max_t = round(max(x["t"] for x in c_hist), 2)
            min_t = round(min(x["t"] for x in c_hist), 2)
            avg_h = round(sum(x["h"] for x in c_hist) / len(c_hist), 2)
            tot_p = round(sum(x["p"] for x in c_hist), 2)
            avg_w = round(sum(x["w"] for x in c_hist) / len(c_hist), 2)

            # ── Analytics payload → weather.analytics ─────────────────────────
            analytics_payload = {
                "city_name"           : city,
                "window_start"        : (sim_time - timedelta(minutes=5)).isoformat(),
                "window_end"          : sim_time.isoformat(),
                "timestamp"           : evt_ms,
                "avg_temperature"     : avg_t,
                "max_temperature"     : max_t,
                "min_temperature"     : min_t,
                "avg_humidity"        : avg_h,
                "total_precipitation" : tot_p,
                "avg_wind_speed"      : avg_w
            }
            producer.send(TOPIC_ANALYTICS, key=city.encode('utf-8'), value=analytics_payload)
            producer.flush()

            # ── Console status ────────────────────────────────────────────────
            city_disp = city.encode('ascii', 'ignore').decode('ascii')
            evt_label = sim_time.strftime("%H:%M:%S")
            print(
                f"[#{sent_count:05d}] {evt_label} | {city_disp:<15s} | "
                f"Temp: {temp:5.1f}C | Hum: {hum:2.0f}% | "
                f"AvgT: {avg_t:5.1f}C | MinT: {min_t:5.1f}C | MaxT: {max_t:5.1f}C",
                flush=True
            )

            # ── Wait 10 real seconds before the next record ───────────────────
            time.sleep(SEND_DELAY_SEC)

    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")
    finally:
        producer.flush()
        producer.close()
        print("Kafka producer closed cleanly.")

if __name__ == "__main__":
    main()
