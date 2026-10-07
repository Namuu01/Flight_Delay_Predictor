import sys
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.weather import fetch_live_weather, get_weather_values, get_live_weather
from app.prediction import (
    predict_flight_delay,
    raw_airlines,
    raw_sources,
    raw_destinations,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

app = FastAPI(
    title="Flight Delay Prediction API",
    description="Operational Flight Delay Forecasting Engine with Live Weather Integration",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FlightPredictionRequest(BaseModel):
    airline: str = Field(default="IndiGo", description="Operating airline")
    source: str = Field(default="Delhi", description="Departure airport city")
    destination: str = Field(default="Mumbai", description="Arrival airport city")
    total_stops: int = Field(default=0, ge=0, le=4, description="Number of layovers")
    journey_year: int = Field(default=2026, description="Flight departure year")
    journey_month: int = Field(default=8, ge=1, le=12, description="Flight departure month")
    journey_day: int = Field(default=15, ge=1, le=31, description="Flight departure day")
    dep_hour: int = Field(default=18, ge=0, le=23, description="Departure hour (24h format)")
    vis_km: Optional[float] = Field(default=None, description="Visibility in km (auto-fetched if omitted)")
    wind_kmh: Optional[float] = Field(default=None, description="Wind speed in km/h (auto-fetched if omitted)")
    rain_mm: Optional[float] = Field(default=None, description="Precipitation in mm (auto-fetched if omitted)")
    temp_c: Optional[float] = Field(default=None, description="Temperature in °C (auto-fetched if omitted)")


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Flight Delay Prediction Engine",
        "endpoints": {
            "/options": "GET valid airlines, sources, and destinations",
            "/weather/{city}": "GET live METAR weather for an airport city",
            "/predict": "POST flight details for delay prediction",
            "/health": "GET health status",
        },
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/options")
def get_options():
    return {
        "airlines": raw_airlines,
        "sources": raw_sources,
        "destinations": raw_destinations,
    }


@app.get("/weather/{city}")
def get_city_weather(city: str):
    weather_data = get_live_weather(city)
    summary_text = fetch_live_weather(city)
    return {
        "city": city,
        "weather": weather_data,
        "summary": summary_text,
    }


@app.post("/predict")
def predict_delay(req: FlightPredictionRequest):
    # Fetch live weather if not explicitly supplied
    vis_km = req.vis_km
    wind_kmh = req.wind_kmh
    rain_mm = req.rain_mm
    temp_c = req.temp_c

    if any(v is None for v in [vis_km, wind_kmh, rain_mm, temp_c]):
        live_vis, live_wind, live_rain, live_temp = get_weather_values(req.source)
        vis_km = live_vis if vis_km is None else vis_km
        wind_kmh = live_wind if wind_kmh is None else wind_kmh
        rain_mm = live_rain if rain_mm is None else rain_mm
        temp_c = live_temp if temp_c is None else temp_c

    forecast_text = predict_flight_delay(
        airline=req.airline,
        source=req.source,
        destination=req.destination,
        total_stops=req.total_stops,
        journey_year=req.journey_year,
        journey_month=req.journey_month,
        journey_day=req.journey_day,
        dep_hour=req.dep_hour,
        vis_km=vis_km,
        wind_kmh=wind_kmh,
        rain_mm=rain_mm,
        temp_c=temp_c,
    )

    return {
        "forecast": forecast_text,
        "weather_used": {
            "visibility_km": vis_km,
            "wind_speed_kmh": wind_kmh,
            "precipitation_mm": rain_mm,
            "temperature_c": temp_c,
        },
    }
