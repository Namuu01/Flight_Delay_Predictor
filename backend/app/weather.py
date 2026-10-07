# ================================================================
# WEATHER API CONFIGURATION
# ================================================================

import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Locate and load .env file from backend directory or project root
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


# ================================================================
# LIVE WEATHER FETCH FUNCTION
# ================================================================

def get_live_weather(city):

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:

        response = requests.get(
            OPENWEATHER_URL,
            params=params,
            timeout=10
        )

        if response.status_code != 200:

            print(
                f"⚠️ OpenWeather API Warning "
                f"{response.status_code}: {response.text}"
            )

            print("Using default fallback weather parameters.")

            return {
                "Temperature_C": 28.0,
                "Visibility_km": 10.0,
                "Wind_Speed_kmh": 12.0,
                "Precipitation_mm": 0.0
            }

        data = response.json()

        temperature_c = data["main"]["temp"]

        visibility_km = (
            data.get("visibility", 10000) / 1000
        )

        wind_speed_kmh = (
            data.get("wind", {}).get("speed", 0) * 3.6
        )

        precipitation_mm = (
            data.get("rain", {}).get("1h", 0)
        )

        return {
            "Temperature_C": temperature_c,
            "Visibility_km": visibility_km,
            "Wind_Speed_kmh": wind_speed_kmh,
            "Precipitation_mm": precipitation_mm
        }

    except Exception as exc:

        print(
            f"⚠️ Could not fetch live weather "
            f"({exc}). Using defaults."
        )

        return {
            "Temperature_C": 28.0,
            "Visibility_km": 10.0,
            "Wind_Speed_kmh": 12.0,
            "Precipitation_mm": 0.0
        }


# ================================================================
# SOURCE HUB → OPENWEATHER CITY MAPPING
# ================================================================

weather_city_map = {

    "0": "Bengaluru",
    "1": "Chennai",
    "2": "Delhi",
    "3": "Kolkata",
    "4": "Mumbai",

    "Bangalore": "Bengaluru",
    "Bengaluru": "Bengaluru",
    "Chennai": "Chennai",
    "Delhi": "Delhi",
    "Kolkata": "Kolkata",
    "Mumbai": "Mumbai",
}


# ================================================================
# FETCH LIVE WEATHER
# ================================================================

def fetch_live_weather(source):

    city = weather_city_map.get(
        str(source),
        str(source)
    )

    weather = get_live_weather(city)

    return (
        f"🌦️ {city} Live Weather\n"
        f"Temperature: {weather['Temperature_C']:.1f} °C\n"
        f"Visibility: {weather['Visibility_km']:.1f} km\n"
        f"Wind Speed: {weather['Wind_Speed_kmh']:.1f} km/h\n"
        f"Precipitation: {weather['Precipitation_mm']:.1f} mm"
    )


# ================================================================
# GET WEATHER VALUES FOR PREDICTION
# ================================================================

def get_weather_values(source):

    city = weather_city_map.get(
        str(source),
        str(source)
    )

    weather = get_live_weather(city)

    return (
        weather["Visibility_km"],
        weather["Wind_Speed_kmh"],
        weather["Precipitation_mm"],
        weather["Temperature_C"],
    )
