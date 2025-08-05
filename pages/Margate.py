import math
import streamlit as st
import sys
import os
import pandas as pd
import joblib
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
import holidays
from sklearn.preprocessing import LabelEncoder

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

now = datetime.now(ZoneInfo("America/New_York"))
today = now.date()
left_co, cent_co = st.columns([1, 4])

with left_co:
    st.image("rising_tide_vertical.png", width=100)

with cent_co:
    st.markdown(
        f"""
        <div style='display: flex; align-items: center; height: 100%;'>
            <div style='padding-left: 50px;'>
                <h1 style='margin: 0;'>Margate Predictions</h1>
                <div style='margin-top: 6px; font-size: 1.95rem; opacity: 0.8;'>
                    {now.strftime("%A, %B %d, %Y")}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown("---")


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
model_path = os.path.join(os.path.dirname(__file__), '..', 'xgb_MARGATE_model.pkl')
model_path = os.path.abspath(model_path) # get absolute path

margate_model = joblib.load(model_path)

from weather_utils import get_weather_data

location = "Margate"

# datetime features
year = 2025 # most current year from model data
month = today.month
dayofweek = today.weekday()
weekofyear = today.isocalendar()[1]
is_weekend = 1 if dayofweek >= 5 else 0
us_holidays = holidays.US(years=2025)
is_holiday = 1 if today in us_holidays else 0
uv_index = 10

weather = get_weather_data(location)

# === Sidebar: Weather Snapshot ===
with st.sidebar:
    st.header("🌦️ Weather Snapshot")
    if weather:
        st.markdown(f"""
        - **Temperature:** {weather['temp']} °F  
        - **Condition:** {weather['conditions']}  
        - **Humidity:** {weather['humidity']}%  
        - **Cloud Cover:** {weather['cloudcover']}%  
        - **Rain (last 5h):** {weather['precip']} mm  
        - **High Temp:** {weather['tempmax']} °F  
        - **Low Temp:** {weather['tempmin']} °F  
        - **Rain Chance:** {weather['precipcover']:.0f}%   
        - **Air Quality Index (categorical):** {weather['aqi_numeric']} 
        """)
    else:
        st.warning("⚠️ Could not retrieve weather data.")

# === Main Input Area ===
st.subheader("📝 Enter Yesterday's Observations")

prev_car_count = st.number_input("🚗 Car Wash Count (Yesterday)", min_value=0, max_value=3000, step=1)

# Encode conditions using LabelEncoder
le = LabelEncoder()
le.fit(['Clear', "Partially Cloudy", "Rain, Partially Cloudy", "Rain, Overcast", "Overcast", "Clouds"])
conditions_encoded = le.transform([weather['conditions']])[0]

# prev day rain
prev_day_rain = weather['precip']
rolling_rain_2 = weather['precip']

def custom_aqi_score(aqi):
    mapping = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4}
    return mapping.get(aqi, 1)

weather["aqi_category"] = custom_aqi_score(weather["aqi_numeric"])

import time

# === For Future Prediction Button ===
if st.button("🔮 Predict"):
    if weather:
        with st.spinner("Crunching the numbers…"):
            # feature vector
            features = np.array([[
                weather["tempmax"],
                weather["tempmin"],
                weather["temp"],
                weather["humidity"],
                weather["precip"],
                weather["precipcover"],
                weather["cloudcover"],
                uv_index,
                conditions_encoded,
                year,
                month,
                dayofweek,
                weekofyear,
                is_weekend,
                prev_day_rain,
                prev_car_count,
                rolling_rain_2,
                is_holiday,
                weather["aqi_category"]
            ]])

            # simulate 3s work
            time.sleep(3)

            prediction = margate_model.predict(features)[0]

        st.subheader(f"Predicted Total Car Count (Retail & Members): **{int(prediction)} cars**")

        if dayofweek <=4:
             multiplier = 0.00
        else:
             multiplier = 0.05
                    
        # calculations
        members = prediction * (0.25 + multiplier)
        conversion = members * 0.10
        # FS calculations
        # Calculate FS count from car count prediction (Weekends usually busier)
        if dayofweek < 4:  # Monday–Friday (0–4)
            FSmultiplier = 0.075
        else:  # Saturday–Sunday (5,6)
            FSmultiplier = 0.10

        st.subheader(f":blue_car: Predicted Potential Members: {members:.0f} cars :blue_car:")
        st.subheader(f":zap: Conversion Goal: {conversion:.0f} new members :zap:")
        st.markdown("---")
        st.subheader(f":star: Greeters should aim for {(conversion / 10):.0f} new members per hour :star:")
        st.markdown("---")
        st.subheader(f"Predicted Full Service washes: {int(prediction) * FSmultiplier :.0f} cars")
        st.markdown("---")

        # greeter split
        st.subheader("Recommended Shift Split for Greeters")
        greeter = math.ceil(conversion // 2)
        leftover = conversion % 2
        st.write(f"Opening Greeter team: **{greeter} new members**")
        st.write(f"Closing Greeter team: **{greeter} new members**")
        st.write(f"Sales Supervisor/Manager: **{math.ceil(leftover)} new members**")




    else:
        st.error("❌ Weather data is missing — prediction cannot proceed.")
