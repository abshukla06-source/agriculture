import random
from datetime import datetime

import pandas as pd
import streamlit as st

from database import engine, Base, SessionLocal
import models
from crop_data import CROP_DATA
from decision_engine import analyze_conditions
from weather import get_weather
from ai_service import ask_agriculture_ai

st.set_page_config(page_title="Smart Agriculture AI", page_icon="🌾", layout="wide")

Base.metadata.create_all(bind=engine)


# ================================
# Helpers
# ================================

@st.cache_data(ttl=600)
def fetch_weather(lat, lon):
    return get_weather(latitude=lat, longitude=lon)


def save_reading(temperature, humidity, soil_moisture):
    db = SessionLocal()
    reading = models.SensorReading(
        temperature=temperature,
        humidity=humidity,
        soil_moisture=soil_moisture,
        timestamp=datetime.utcnow(),
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    db.close()
    return reading


def get_latest_reading():
    db = SessionLocal()
    reading = (
        db.query(models.SensorReading)
        .order_by(models.SensorReading.id.desc())
        .first()
    )
    db.close()
    return reading


def get_all_readings():
    db = SessionLocal()
    readings = (
        db.query(models.SensorReading)
        .order_by(models.SensorReading.id.asc())
        .all()
    )
    db.close()
    return readings


# ================================
# Sidebar — sensor input & controls
# ================================

st.sidebar.header("Controls")
crop = st.sidebar.selectbox("Select crop", list(CROP_DATA.keys()))

st.sidebar.subheader("Sensor input")
mode = st.sidebar.radio("Reading source", ["Simulate random reading", "Enter manually"])

if mode == "Simulate random reading":
    if st.sidebar.button("Generate new reading"):
        reading = save_reading(
            temperature=round(random.uniform(15, 40), 1),
            humidity=round(random.uniform(30, 90), 1),
            soil_moisture=round(random.uniform(20, 90), 1),
        )
        st.sidebar.success(f"Saved reading #{reading.id}")
else:
    with st.sidebar.form("manual_reading_form"):
        temperature = st.slider("Temperature (°C)", 0.0, 50.0, 27.0)
        humidity = st.slider("Humidity (%)", 0.0, 100.0, 60.0)
        soil_moisture = st.slider("Soil moisture (%)", 0.0, 100.0, 50.0)
        submitted = st.form_submit_button("Save reading")
        if submitted:
            reading = save_reading(temperature, humidity, soil_moisture)
            st.sidebar.success(f"Saved reading #{reading.id}")

st.sidebar.divider()
st.sidebar.subheader("Location (for weather)")
lat = st.sidebar.number_input("Latitude", value=26.9124, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=75.7873, format="%.4f")


# ================================
# Main
# ================================

st.title("🌾 Smart Agriculture AI")
st.caption("Real-time crop condition monitoring and AI-assisted irrigation advice")

latest = get_latest_reading()

if latest is None:
    st.info("No sensor readings yet. Use the sidebar to generate or enter one.")
    st.stop()

crop_info = CROP_DATA[crop]
decision = analyze_conditions(
    crop_info, latest.temperature, latest.humidity, latest.soil_moisture
)

try:
    weather_data = fetch_weather(lat, lon)
    probs = weather_data["hourly"]["precipitation_probability"][:6]
    rain_probability = max(probs) if probs else 0
except Exception:
    weather_data = None
    rain_probability = 0

irrigation_status = decision["irrigation"]
recommendation = decision["recommendation"]
warnings = list(decision["warnings"])

if (
    latest.soil_moisture < crop_info["soil_moisture_min"]
    and rain_probability >= 60
):
    irrigation_status = "Delay irrigation - rain expected"
    recommendation = (
        "Soil moisture is low, but significant rainfall is expected in the "
        "next few hours. Delay irrigation and monitor soil moisture."
    )
    warnings.append(f"Rain probability is {rain_probability}% in the next few hours.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Temperature", f"{latest.temperature} °C")
col2.metric("Humidity", f"{latest.humidity} %")
col3.metric("Soil moisture", f"{latest.soil_moisture} %")
col4.metric("Health score", f"{decision['health_score']}/100")

status_box = {
    "Healthy": st.success,
    "Needs Attention": st.warning,
    "Critical": st.error,
}[decision["overall_status"]]
status_box(f"**{decision['overall_status']}** — {recommendation}")

st.write(
    f"**Irrigation:** {irrigation_status}  |  "
    f"**Priority:** {decision['priority']}  |  "
    f"**Rain probability (6h):** {rain_probability}%"
)

for issue in decision["issues"]:
    st.error(issue)
for w in warnings:
    st.warning(w)

st.divider()

st.subheader("Sensor history")
readings = get_all_readings()
df = pd.DataFrame(
    [
        {
            "timestamp": r.timestamp,
            "Temperature": r.temperature,
            "Humidity": r.humidity,
            "Soil moisture": r.soil_moisture,
        }
        for r in readings
    ]
).set_index("timestamp")
st.line_chart(df)

st.divider()

st.subheader("Ask the AI agronomist")
question = st.text_input("Your question", placeholder="Should I irrigate today?")
if st.button("Get AI advice"):
    try:
        advice = ask_agriculture_ai(
            crop=crop,
            temperature=latest.temperature,
            humidity=latest.humidity,
            soil_moisture=latest.soil_moisture,
            irrigation_status=irrigation_status,
            health_score=decision["health_score"],
            recommendation=recommendation,
            rain_probability=rain_probability,
            question=question,
        )
        st.write(advice)
    except RuntimeError as e:
        st.error(f"{e} — add it in the app's Secrets settings on Streamlit Cloud.")
    except Exception as e:
        st.error(f"AI request failed: {e}")
