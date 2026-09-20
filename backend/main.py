from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from database import engine, Base, SessionLocal
import models
from crop_data import CROP_DATA
from decision_engine import analyze_conditions
from weather import get_weather
from ai_service import ask_agriculture_ai


app = FastAPI()


# ================================
# CORS
# ================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================
# Database
# ================================

Base.metadata.create_all(bind=engine)


# ================================
# Sensor Data Model
# ================================

class SensorData(BaseModel):
    temperature: float
    humidity: float
    soil_moisture: float


# ================================
# Home
# ================================

@app.get("/")
def home():

    return {
        "message": "Smart Agriculture AI Backend is running!"
    }


# ================================
# Receive Sensor Data
# ================================

@app.post("/sensor-data")
def receive_sensor_data(data: SensorData):

    db = SessionLocal()

    new_reading = models.SensorReading(
        temperature=data.temperature,
        humidity=data.humidity,
        soil_moisture=data.soil_moisture,
        timestamp=datetime.utcnow()
    )

    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    db.close()

    return {
        "status": "success",
        "message": "Sensor data saved successfully!",
        "data": {
            "id": new_reading.id,
            "temperature": new_reading.temperature,
            "humidity": new_reading.humidity,
            "soil_moisture": new_reading.soil_moisture,
            "timestamp": new_reading.timestamp
        }
    }


# ================================
# Crop Analysis
# ================================

@app.get("/analysis")
def crop_analysis(crop: str = "Wheat"):

    # Check crop name
    if crop not in CROP_DATA:

        return {
            "status": "error",
            "message": "Crop not found",
            "available_crops": list(CROP_DATA.keys())
        }


    crop_info = CROP_DATA[crop]


    # ================================
    # Get Latest Sensor Reading
    # ================================

    db = SessionLocal()

    latest_reading = (
        db.query(models.SensorReading)
        .order_by(models.SensorReading.id.desc())
        .first()
    )

    db.close()


    if latest_reading is None:

        return {
            "status": "error",
            "message": "No sensor data available"
        }


    temperature = latest_reading.temperature
    humidity = latest_reading.humidity
    soil_moisture = latest_reading.soil_moisture


    # ================================
    # Run Decision Engine
    # ================================

    decision = analyze_conditions(
        crop_info=crop_info,
        temperature=temperature,
        humidity=humidity,
        soil_moisture=soil_moisture
    )


    # ================================
    # Get Weather Forecast
    # ================================

    weather_data = get_weather()

    precipitation_probability = 0

    try:

        probabilities = weather_data["hourly"]["precipitation_probability"]

        # Look at the next 6 hours
        next_hours = probabilities[:6]

        if next_hours:
            precipitation_probability = max(next_hours)

    except (KeyError, TypeError, IndexError):

        precipitation_probability = 0


    # ================================
    # Weather-Aware Irrigation
    # ================================

    irrigation_status = decision["irrigation"]

    irrigation_level = decision["priority"].lower()

    recommendation = decision["recommendation"]

    warnings = list(decision["warnings"])


    # If soil needs water but significant rain is expected,
    # delay irrigation.

    if (
        soil_moisture < crop_info["soil_moisture_min"]
        and precipitation_probability >= 60
    ):

        irrigation_status = "Delay irrigation - rain expected"

        irrigation_level = "low"

        recommendation = (
            "Soil moisture is low, but significant rainfall "
            "is expected in the next few hours. Delay irrigation "
            "and monitor soil moisture."
        )

        warnings.append(
            f"Rain probability is {precipitation_probability}% "
            "in the next few hours."
        )


    # ================================
    # Return Complete Analysis
    # ================================

    return {

        "status": "success",

        "analysis": {

            "crop": crop,

            "temperature": temperature,

            "humidity": humidity,

            "soil_moisture": soil_moisture,

            "timestamp": latest_reading.timestamp,

            "irrigation_status": irrigation_status,

            "irrigation_level": irrigation_level,

            "rain_probability": precipitation_probability,

            "temperature_status": (

                "Temperature is below ideal range"

                if temperature < crop_info["temperature_min"]

                else

                "Temperature is above ideal range"

                if temperature > crop_info["temperature_max"]

                else

                "Temperature is within ideal range"
            ),

            "humidity_status": (

                "Humidity is below ideal range"

                if humidity < crop_info["humidity_min"]

                else

                "Humidity is above ideal range"

                if humidity > crop_info["humidity_max"]

                else

                "Humidity is within ideal range"
            ),

            "overall_status": decision["overall_status"],

            "health_score": decision["health_score"],

            "recommendation": recommendation,

            "issues": decision["issues"],

            "warnings": warnings,

            "crop_requirements": {

                "soil_moisture_min":
                    crop_info["soil_moisture_min"],

                "soil_moisture_max":
                    crop_info["soil_moisture_max"],

                "temperature_min":
                    crop_info["temperature_min"],

                "temperature_max":
                    crop_info["temperature_max"],

                "humidity_min":
                    crop_info["humidity_min"],

                "humidity_max":
                    crop_info["humidity_max"],

                "ph_min":
                    crop_info["ph_min"],

                "ph_max":
                    crop_info["ph_max"],

                "water_requirement":
                    crop_info["water_requirement"]
            }
        }
    }


# ================================
# Get All Sensor Data
# ================================

@app.get("/sensor-data")
def get_sensor_data():

    db = SessionLocal()

    readings = db.query(models.SensorReading).all()

    db.close()

    return readings


# ================================
# Weather
# ================================

@app.get("/weather")
def weather():

    return get_weather()

# ================================
# AI Agricultural Advice
# ================================

@app.get("/ai-advice")
def ai_advice(
    crop: str = "Rice",
    question: str = ""
):

    # Get latest sensor reading

    db = SessionLocal()

    latest_reading = (
        db.query(models.SensorReading)
        .order_by(models.SensorReading.id.desc())
        .first()
    )

    db.close()


    if latest_reading is None:

        return {
            "status": "error",
            "message": "No sensor data available"
        }


    # Get crop analysis

    analysis_response = crop_analysis(crop)

    if analysis_response.get("status") != "success":

        return analysis_response


    analysis = analysis_response["analysis"]


    # Ask Gemini

    advice = ask_agriculture_ai(
        crop=crop,
        temperature=latest_reading.temperature,
        humidity=latest_reading.humidity,
        soil_moisture=latest_reading.soil_moisture,
        irrigation_status=analysis["irrigation_status"],
        health_score=analysis["health_score"],
        recommendation=analysis["recommendation"],
        rain_probability=analysis["rain_probability"],
        question=question
    )


    return {
        "status": "success",
        "crop": crop,
        "ai_advice": advice
    }