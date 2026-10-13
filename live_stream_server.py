import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Weather Analytics Real-Time Streaming Server")

# Check if kafka-python is available
try:
    from kafka import KafkaProducer
    kafka_producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("Connected to Kafka on localhost:9092")
except Exception as e:
    kafka_producer = None
    print("Running without Kafka connection:", e)

# Load the chronological stream sample
with open("data/stream_sample_600.json", "r", encoding="utf-8") as f:
    STREAM_RECORDS = json.load(f)

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    with open("live_weather_stream_dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/events")
async def get_all_events():
    return STREAM_RECORDS

@app.post("/api/publish_event")
async def publish_event(event: dict):
    """Optionally forwards an event to Kafka in real time"""
    if kafka_producer:
        try:
            kafka_producer.send("weather.raw", event)
        except Exception:
            pass
    return {"status": "ok"}

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  WEATHER REAL-TIME STREAMING & VISUALIZATION SERVER")
    print("  Dashboard URL: http://localhost:8080")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
