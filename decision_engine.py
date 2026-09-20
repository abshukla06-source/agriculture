def analyze_conditions(
    crop_info,
    temperature,
    humidity,
    soil_moisture
):

    issues = []
    warnings = []
    score = 100


    # ================================
    # Soil Moisture
    # ================================

    if soil_moisture < crop_info["soil_moisture_min"]:

        issues.append("Soil moisture is too low")
        score -= 35

    elif soil_moisture > crop_info["soil_moisture_max"]:

        warnings.append("Soil moisture is too high")
        score -= 15


    # ================================
    # Temperature
    # ================================

    if temperature < crop_info["temperature_min"]:

        issues.append("Temperature is below the ideal range")
        score -= 20

    elif temperature > crop_info["temperature_max"]:

        issues.append("Temperature is above the ideal range")
        score -= 20


    # ================================
    # Humidity
    # ================================

    if humidity < crop_info["humidity_min"]:

        warnings.append("Humidity is below the ideal range")
        score -= 10

    elif humidity > crop_info["humidity_max"]:

        warnings.append("Humidity is above the ideal range")
        score -= 10


    # ================================
    # Overall Status
    # ================================

    if score >= 80:

        overall_status = "Healthy"

    elif score >= 60:

        overall_status = "Needs Attention"

    else:

        overall_status = "Critical"


    # ================================
    # Irrigation Recommendation
    # ================================

    if soil_moisture < crop_info["soil_moisture_min"]:

        irrigation = "Irrigation recommended"

    elif soil_moisture > crop_info["soil_moisture_max"]:

        irrigation = "Do not irrigate"

    else:

        irrigation = "No irrigation needed"


    # ================================
    # Priority
    # ================================

    if soil_moisture < crop_info["soil_moisture_min"]:

        priority = "HIGH"

    elif issues:

        priority = "MEDIUM"

    else:

        priority = "LOW"


    # ================================
    # Final Recommendation
    # ================================

    if overall_status == "Healthy":

        recommendation = (
            "Current conditions are suitable for the selected crop."
        )

    elif overall_status == "Needs Attention":

        recommendation = (
            "Some environmental conditions need attention."
        )

    else:

        recommendation = (
            "Immediate action is recommended to protect the crop."
        )


    return {

        "overall_status": overall_status,

        "health_score": max(score, 0),

        "irrigation": irrigation,

        "priority": priority,

        "recommendation": recommendation,

        "issues": issues,

        "warnings": warnings

    }