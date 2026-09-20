import requests


# Default coordinates (Jaipur) — overridden via get_weather() args
JAIPUR_LATITUDE = 26.9124
JAIPUR_LONGITUDE = 75.7873


def get_weather(latitude=JAIPUR_LATITUDE, longitude=JAIPUR_LONGITUDE):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "hourly": "precipitation_probability,precipitation",
        "forecast_days": 1,
        "timezone": "Asia/Kolkata"
    }

    response = requests.get(url, params=params, timeout=10)

    response.raise_for_status()

    data = response.json()

    return data
