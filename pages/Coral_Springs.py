import streamlit as st
import sys
import os
import math
import pandas as pd
import joblib
import numpy as np
from dateutil.utils import today
import datetime
import holidays
from sklearn.preprocessing import LabelEncoder

left_co, cent_co = st.columns([1, 4])

with left_co:
    st.image("rising_tide_vertical.png", use_container_width=True)

with cent_co:
    st.markdown(
        """
        <div style='display: flex; align-items: center; height: 100%;'>
            <h1 style='margin: 0; padding-left: 50px;'>Coral Springs Predictions</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown("---")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
model_path = os.path.join(os.path.dirname(__file__), '..', 'xgb_CORALSPRINGS_model.pkl')
model_path = os.path.abspath(model_path) # get absolute path

CS_model = joblib.load(model_path)

from weather_utils import get_weather_data

location = "Coral Springs"

# datetime features
today = datetime.date.today()
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
        - **Rain (last 1h):** {weather['precip']} mm  
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

def custom_aqi_score(aqi):
    mapping = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4}
    return mapping.get(aqi, 1)

weather["aqi_category"] = custom_aqi_score(weather["aqi_numeric"])

# Encode conditions using LabelEncoder
le = LabelEncoder()
le.fit(['Clear', "Partially Cloudy", "Rain, Partially Cloudy", "Rain, Overcast", "Overcast", "Clouds"])
conditions_encoded = le.transform([weather['conditions']])[0]

# prev day rain
prev_day_rain = weather['precip']
rolling_rain_2 = weather['precip']

# === For Future Prediction Button ===
if st.button("🔮 Predict"):
    if weather:
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

        prediction = CS_model.predict(features)[0]
        st.subheader(f"Predicted Car Count: **{int(prediction)} cars**")

        # calculations
        members = prediction * 0.70
        conversion = members * 0.10

        st.subheader(f":blue_car: Predicted Potential Members: {members:.0f} cars :blue_car:")
        st.subheader(f":zap: Conversion Goal: {conversion:.0f} new members :zap:")
        st.markdown("---")
        st.subheader(f":star: Greeters should aim for {(conversion / 10):.0f} new members per hour :star:")
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


