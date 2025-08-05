# weather_utils.py
import requests
import streamlit as st
from datetime import datetime, timedelta
import datetime as dt
import os

def get_weather_data(location):
    location = location.strip().title()  # normalize input
    API_KEY = st.secrets["API_KEY"]
    if not API_KEY:
        st.error("API key invalid/missing")

    locations = {
        "Coral Springs": {"lat": 26.2712, "lon": -80.2706},
        "Margate": {"lat": 26.2445, "lon": -80.2064},
        "Parkland": {"lat": 26.3108, "lon": -80.2232},
    }

    coords = locations.get(location)
    if not coords:
        st.error(f"Error with location: `{location}`")
        return None

    lat, lon = coords["lat"], coords["lon"]
    weather_data = {}

    # --- 1. Current Weather ---
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "imperial"}
        response = requests.get(url, params=params)
        data = response.json()

        weather_data["temp"] = data["main"]["temp"]
        weather_data["humidity"] = data["main"]["humidity"]
        weather_data["cloudcover"] = data["clouds"]["all"]
        weather_data["conditions"] = data["weather"][0]["main"]

        if "rain" in data:
            weather_data["precip"] = data["rain"].get("3h", data["rain"].get("1h", 0.0))
        else:
            weather_data["precip"] = 0.0

    except Exception as e:
        st.warning(f"Failed to fetch current weather: {e}")
        return None

    # --- 2. Forecast (for max/min and chance of rain) ---
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "imperial"}
        response = requests.get(url, params=params)
        data = response.json()

        temps = [entry["main"]["temp"] for entry in data["list"][:8]]
        pops = [entry.get("pop", 0) for entry in data["list"][:8]]

        weather_data["tempmax"] = max(temps)
        weather_data["tempmin"] = min(temps)
        weather_data["precipcover"] = max(pops) * 100  # % chance of rain
        weather_data["avg_temp"] = sum(temps) / len(temps)

    except Exception as e:
        st.warning(f"Failed to fetch forecast data: {e}")
        return None

    # --- 3. AQI (numerical) ---
    try:
        # Calculate Unix timestamps for yesterday
        yesterday = datetime.utcnow() - timedelta(days=1)
        start_ts = int(datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0).timestamp())
        end_ts = start_ts + 86400  # 24 hours later

        url = "https://api.openweathermap.org/data/2.5/air_pollution/history"
        params = {
            "lat": lat,
            "lon": lon,
            "start": start_ts,
            "end": end_ts,
            "appid": API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()

        # Extract max AQI from the hourly values
        if "list" in data and data["list"]:
            aqi_values = [entry["main"]["aqi"] for entry in data["list"]]
            aqi_max = max(aqi_values)
        else:
            aqi_max = None

        weather_data["aqi_numeric"] = aqi_max  # 1–5 scale

    except Exception as e:
        st.warning(f"Failed to fetch historical AQI data: {e}")
        weather_data["aqi_numeric"] = None

    return weather_data
