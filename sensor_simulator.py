import requests
import random
import time


BACKEND_URL = "http://127.0.0.1:8000/sensor-data"


while True:

    temperature = round(random.uniform(25, 35), 1)
    humidity = round(random.uniform(50, 80), 1)
    soil_moisture = round(random.uniform(25, 70), 1)

    sensor_data = {
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_moisture
    }

    try:

        response = requests.post(
            BACKEND_URL,
            json=sensor_data
        )

        print(
            "Sent:",
            sensor_data,
            "| Status:",
            response.status_code
        )

    except Exception as error:

        print("Could not connect to backend:", error)

    time.sleep(5)