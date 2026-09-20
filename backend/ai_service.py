import os
from google import genai


client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


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


    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text