import os

import streamlit as st
from google import genai


_client = None

# Set GEMINI_MODEL in Streamlit secrets/env to override. Verify this model
# name is still valid for your API key before deploying.
DEFAULT_MODEL = "gemini-3.6-flash"


def _get_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY")


def _get_client():
    global _client
    if _client is None:
        api_key = _get_api_key()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        _client = genai.Client(api_key=api_key)
    return _client


def ask_agriculture_ai(
    crop,
    temperature,
    humidity,
    soil_moisture,
    irrigation_status,
    health_score,
    recommendation,
    rain_probability,
    question=""
):

    prompt = f"""
You are an AI agricultural assistant.

Analyze the following farm conditions:

Crop: {crop}

Temperature: {temperature} °C
Humidity: {humidity} %
Soil Moisture: {soil_moisture} %
Rain Probability: {rain_probability} %

Current Irrigation Decision:
{irrigation_status}

Crop Health Score:
{health_score}/100

Existing Recommendation:
{recommendation}

Give a short, practical explanation for the farmer.

Explain:
1. Current crop condition
2. Whether irrigation is needed
3. Whether rain affects the decision
4. What the farmer should do next

Do not invent sensor values or facts that are not provided.

The farmer's question is:

{question}

Answer the farmer's question directly and practically.
"""

    client = _get_client()
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text
