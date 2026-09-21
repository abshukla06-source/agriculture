import os
import time

import streamlit as st
from google import genai
from google.genai import errors as genai_errors


_client = None

# Set GEMINI_MODEL in Streamlit secrets/env to override.
DEFAULT_MODEL = "gemini-3.6-flash"

# Tried in order if the primary model is unavailable.
FALLBACK_MODELS = ["gemini-2.0-flash"]

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2  # doubles each retry (2s, 4s, 8s)


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


def _generate_with_retry(client, model, prompt):
    delay = RETRY_DELAY_SECONDS
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            return client.models.generate_content(model=model, contents=prompt)
        except genai_errors.ServerError as e:
            # 503 / high-demand — worth retrying
            last_error = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(delay)
                delay *= 2
        except genai_errors.ClientError:
            # 4xx (bad key, bad request, etc.) — retrying won't help
            raise

    raise last_error


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
    models_to_try = [os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)] + FALLBACK_MODELS

    last_error = None
    for model in models_to_try:
        try:
            response = _generate_with_retry(client, model, prompt)
            return response.text
        except genai_errors.ServerError as e:
            last_error = e
            continue  # try the next model in the fallback list

    raise RuntimeError(
        f"All models are currently unavailable (Gemini servers busy). Last error: {last_error}"
    )