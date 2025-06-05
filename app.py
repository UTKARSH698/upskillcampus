import streamlit as st
import requests
import datetime
import plotly.graph_objects as go
import numpy as np
import math # For math.isclose for floating point comparison

# --- Configuration ---
# Your API Key is directly placed here as requested.
# For production or public sharing, it's highly recommended to use Streamlit's secrets.toml
# or environment variables for security.
API_KEY = "3d836f0b3e18831deb85653baace302a"


OWM_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast" # 5-day / 3-hour forecast
OWM_ICON_URL = "http://openweathermap.org/img/wn/{icon_code}@2x.png"

# --- Crop Data (Expanded with Soil Info) ---
crops = {
    "rice": {"name": "Rice 🍚", "description": "A staple food, rice thrives in warm, humid climates with ample water and heavy clay or loamy soils.", "optimal_temp": (20, 35), "optimal_humidity": (60, 80), "water": "high", "planting_months": [5, 6, 7], "harvest_months": [10, 11, 12], "suitable_soils": ["clay", "loamy", "alluvial"]},
    "maize": {"name": "Maize 🌽", "description": "Versatile crop used for food and feed. Prefers moderate temperatures and well-drained, fertile loamy soils.", "optimal_temp": (18, 27), "optimal_humidity": (50, 80), "water": "medium", "planting_months": [3, 4, 5], "harvest_months": [8, 9, 10], "suitable_soils": ["loamy", "sandy loam"]},
    "jute": {"name": "Jute 🌱", "description": "A natural fiber crop requiring high humidity, warm weather, and sandy to clay loamy soils.", "optimal_temp": (24, 37), "optimal_humidity": (70, 90), "water": "high", "planting_months": [3, 4], "harvest_months": [7, 8], "suitable_soils": ["sandy loam", "clay loam", "alluvial"]},
    "cotton": {"name": "Cotton ☁️", "description": "Important fiber crop, needs a long frost-free period, moderate water, and deep, well-drained black or alluvial soils.", "optimal_temp": (21, 30), "optimal_humidity": (50, 70), "water": "medium", "planting_months": [4, 5], "harvest_months": [10, 11], "suitable_soils": ["black", "alluvial", "loamy"]},
    "coconut": {"name": "Coconut 🥥", "description": "Tropical palm needing consistent warmth, humidity, and sandy to loamy soils, often near coastal areas.", "optimal_temp": (20, 30), "optimal_humidity": (70, 90), "water": "high", "planting_months": [6, 7, 8], "harvest_months": [12, 1, 2], "suitable_soils": ["sandy", "loamy"]},
    "papaya": {"name": "Papaya 🥭", "description": "Sweet tropical fruit, sensitive to cold and waterlogging. Prefers well-drained sandy loam soils.", "optimal_temp": (21, 33), "optimal_humidity": (60, 85), "water": "medium", "planting_months": [2, 3, 4], "harvest_months": [7, 8, 9], "suitable_soils": ["sandy loam", "loamy"]},
    "orange": {"name": "Orange 🍊", "description": "Citrus fruit, requires warm climate but can tolerate some cold. Best in well-drained loamy or sandy loam soils.", "optimal_temp": (13, 37), "optimal_humidity": (50, 80), "water": "medium", "planting_months": [6, 7], "harvest_months": [11, 12], "suitable_soils": ["loamy", "sandy loam"]},
    "apple": {"name": "Apple 🍎", "description": "Temperate fruit, needs a cold dormant period for good fruiting. Thrives in deep, well-drained loamy soils.", "optimal_temp": (7, 24), "optimal_humidity": (60, 80), "water": "medium", "planting_months": [12, 1, 2], "harvest_months": [9, 10], "suitable_soils": ["loamy", "silty loam"]},
    "muskmelon": {"name": "Muskmelon 🍈", "description": "Summer fruit, needs warm, sunny weather and consistent moisture. Prefers well-drained sandy loam to loamy soils.", "optimal_temp": (18, 30), "optimal_humidity": (50, 70), "water": "medium", "planting_months": [2, 3, 4], "harvest_months": [6, 7], "suitable_soils": ["sandy loam", "loamy"]},
    "watermelon": {"name": "Watermelon 🍉", "description": "Another summer favorite, requires hot weather and plenty of water. Best in well-drained sandy loam soils.", "optimal_temp": (21, 35), "optimal_humidity": (50, 70), "water": "medium", "planting_months": [1, 2, 3], "harvest_months": [4, 5, 6], "suitable_soils": ["sandy loam", "sandy"]},
    "grapes": {"name": "Grapes 🍇", "description": "Versatile fruit, thrives in warm, dry summers and cool winters. Prefers well-drained loamy or sandy soils.", "optimal_temp": (15, 35), "optimal_humidity": (50, 70), "water": "medium", "planting_months": [12, 1], "harvest_months": [3, 4], "suitable_soils": ["loamy", "sandy", "clay loam"]},
    "mango": {"name": "Mango 🥭", "description": "The 'king of fruits', needs tropical or subtropical climate and well-drained loamy soils.", "optimal_temp": (24, 27), "optimal_humidity": (60, 85), "water": "medium", "planting_months": [6, 7], "harvest_months": [3, 4, 5], "suitable_soils": ["loamy", "sandy loam", "alluvial"]},
    "banana": {"name": "Banana 🍌", "description": "Tropical fruit, requires high temperatures, humidity, rainfall, and deep, fertile, well-drained loamy soils.", "optimal_temp": (26, 30), "optimal_humidity": (70, 90), "water": "high", "planting_months": [3, 4], "harvest_months": [10, 11], "suitable_soils": ["loamy", "silty loam", "clay loam"]},
    "pomegranate": {"name": "Pomegranate 🌰", "description": "Drought-tolerant fruit, prefers hot and dry climate. Adapts to various soils but prefers deep, well-drained loamy to sandy soils.", "optimal_temp": (25, 35), "optimal_humidity": (40, 60), "water": "low", "planting_months": [6, 7], "harvest_months": [11, 12], "suitable_soils": ["loamy", "sandy loam", "red"]},
    "lentil": {"name": "Lentil 🥣", "description": "A pulse crop, resilient and thrives in cool, dry conditions. Best in well-drained loamy soils.", "optimal_temp": (18, 24), "optimal_humidity": (40, 60), "water": "low", "planting_months": [10, 11], "harvest_months": [3, 4], "suitable_soils": ["loamy", "sandy loam"]},
    "blackgram": {"name": "Blackgram ⚫", "description": "A protein-rich pulse, thrives in warm and humid conditions. Prefers well-drained loamy to clay loamy soils.", "optimal_temp": (25, 35), "optimal_humidity": (60, 80), "water": "medium", "planting_months": [6, 7], "harvest_months": [10, 11], "suitable_soils": ["loamy", "clay loam"]},
    "mungbean": {"name": "Mungbean 🟢", "description": "Another popular pulse, adaptable to various climates. Best in well-drained sandy loam to loamy soils.", "optimal_temp": (25, 35), "optimal_humidity": (60, 80), "water": "medium", "planting_months": [6, 7], "harvest_months": [9, 10], "suitable_soils": ["sandy loam", "loamy"]},
    "mothbeans": {"name": "Mothbeans 🫘", "description": "Drought-resistant pulse, suitable for arid regions. Grows well in sandy to sandy loam soils.", "optimal_temp": (25, 35), "optimal_humidity": (50, 70), "water": "low", "planting_months": [6, 7], "harvest_months": [9, 10], "suitable_soils": ["sandy", "sandy loam"]},
    "pigeonpeas": {"name": "Pigeonpeas 🫘", "description": "Hardy pulse crop, tolerates dry conditions. Best in well-drained loamy soils.", "optimal_temp": (18, 30), "optimal_humidity": (50, 70), "water": "medium", "planting_months": [6, 7], "harvest_months": [12, 1], "suitable_soils": ["loamy", "sandy loam"]},
    "kidneybeans": {"name": "Kidneybeans 🫘", "description": "Popular bean, sensitive to frost and extreme heat. Prefers well-drained, fertile loamy soils.", "optimal_temp": (15, 25), "optimal_humidity": (50, 70), "water": "medium", "planting_months": [6, 7], "harvest_months": [10, 11], "suitable_soils": ["loamy", "silty loam"]},
    "chickpea": {"name": "Chickpea 🥜", "description": "Cool-season legume, thrives in dry, cool conditions. Best in well-drained loamy to sandy soils.", "optimal_temp": (15, 25), "optimal_humidity": (40, 60), "water": "low", "planting_months": [10, 11], "harvest_months": [3, 4], "suitable_soils": ["loamy", "sandy loam"]},
    "coffee": {"name": "Coffee ☕", "description": "A high-value crop, needs specific temperature and rainfall. Requires deep, well-drained, slightly acidic loamy soils.", "optimal_temp": (15, 25), "optimal_humidity": (60, 80), "water": "medium", "planting_months": [5, 6], "harvest_months": [11, 12], "suitable_soils": ["loamy", "volcanic"]}
}

soil_types = [
    "Choose Soil Type", # Default/placeholder
    "sandy", "sandy loam", "loamy", "silty loam", "clay", "clay loam", "black", "red", "alluvial", "acidic"
]

# --- Helper Functions ---
def fetch_weather(city):
    """Fetches current weather data for a given city."""
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(OWM_CURRENT_URL, params=params)
    if response.status_code == 401:
        raise Exception("Invalid API Key. Please check your OpenWeatherMap API key.")
    elif response.status_code == 404:
        raise Exception("City not found. Please check the spelling.")
    elif response.status_code == 429:
        raise Exception("API rate limit exceeded. Please wait a few minutes and try again.")
    elif response.status_code != 200:
        raise Exception(f"Weather API error: {response.status_code} - {response.text}")

    data = response.json()

    # Get wind direction
    deg = data["wind"].get("deg", 0)
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    wind_direction_index = round(deg / (360. / len(directions))) % len(directions)
    wind_direction = directions[wind_direction_index]

    return {
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"].get("speed", 0.0),
        "wind_direction": wind_direction,
        "rainfall": data.get("rain", {}).get("1h", 0.0), # Rainfall in last 1 hour
        "condition": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    }

def fetch_forecast(city):
    """Fetches 5-day / 3-hour weather forecast data for a given city."""
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(OWM_FORECAST_URL, params=params)
    if response.status_code == 401:
        raise Exception("Invalid API Key. Please check your OpenWeatherMap API key.")
    elif response.status_code == 404:
        raise Exception("City not found. Please check the spelling for forecast.")
    elif response.status_code == 429:
        raise Exception("Forecast API rate limit exceeded. Please wait a few minutes and try again.")
    elif response.status_code != 200:
        raise Exception(f"Forecast API error: {response.status_code} - {response.text}")

    data = response.json()
    forecast_list = []
    today = datetime.date.today()

    # Aggregate forecast data by day
    daily_forecasts = {}
    for item in data["list"]:
        dt_object = datetime.datetime.fromtimestamp(item["dt"])
        date_str = dt_object.strftime("%Y-%m-%d")

        if date_str not in daily_forecasts:
            daily_forecasts[date_str] = {
                "temps": [], "humidities": [], "rainfalls": [], "conditions": [], "icons": []
            }
        daily_forecasts[date_str]["temps"].append(item["main"]["temp"])
        daily_forecasts[date_str]["humidities"].append(item["main"]["humidity"])
        daily_forecasts[date_str]["rainfalls"].append(item.get("rain", {}).get("3h", 0.0))
        daily_forecasts[date_str]["conditions"].append(item["weather"][0]["description"])
        daily_forecasts[date_str]["icons"].append(item["weather"][0]["icon"])

    # Process aggregated data for display
    for date_str, daily_data in daily_forecasts.items():
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_obj == today: # Skip today as it's covered by current weather
            continue

        avg_temp = sum(daily_data["temps"]) / len(daily_data["temps"])
        avg_humidity = sum(daily_data["humidities"]) / len(daily_data["humidities"])
        total_rainfall = sum(daily_data["rainfalls"]) # Sum 3-hour rainfalls for daily total

        # Find most common condition/icon for the day
        from collections import Counter
        most_common_condition = Counter(daily_data["conditions"]).most_common(1)[0][0]
        most_common_icon = Counter(daily_data["icons"]).most_common(1)[0][0]

        forecast_list.append({
            "date": date_obj,
            "min_temp": min(daily_data["temps"]),
            "max_temp": max(daily_data["temps"]),
            "avg_humidity": avg_humidity,
            "total_rainfall": total_rainfall,
            "condition": most_common_condition,
            "icon": most_common_icon
        })
    return forecast_list

def calculate_suitability_score(crop_key, weather, soil_type):
    """Calculates a suitability score (0-100) for a crop based on weather and soil."""
    crop = crops[crop_key]
    score = 0
    temp_score = 0
    humidity_score = 0
    rainfall_score = 0
    soil_score = 0
    month_score = 0

    # Temperature Score
    temp = weather["temperature"]
    tmin, tmax = crop["optimal_temp"]
    if tmin <= temp <= tmax:
        temp_score = 30 # Optimal
    elif tmin - 5 <= temp <= tmax + 5:
        temp_score = 20 # Within tolerance
    else:
        temp_score = 5 # Far off

    # Humidity Score
    humidity = weather["humidity"]
    hmin, hmax = crop["optimal_humidity"]
    if hmin <= humidity <= hmax:
        humidity_score = 30 # Optimal
    elif hmin - 10 <= humidity <= hmax + 10:
        humidity_score = 20 # Within tolerance
    else:
        humidity_score = 5 # Far off

    # Rainfall Score (simplified)
    # This needs more nuance for 'low', 'medium', 'high' water crops
    rainfall = weather["rainfall"] # 1-hour rainfall
    if crop["water"] == "high":
        if rainfall >= 1.0: rainfall_score = 15
        elif rainfall >= 0.1: rainfall_score = 10
        else: rainfall_score = 5
    elif crop["water"] == "medium":
        if 0.1 <= rainfall <= 5.0: rainfall_score = 15
        else: rainfall_score = 10
    else: # low water
        if rainfall < 1.0: rainfall_score = 15
        else: rainfall_score = 5 # Too much rain might be bad

    # Soil Score
    if soil_type.lower() in crop["suitable_soils"]:
        soil_score = 15
    else:
        soil_score = 0

    # Month Score (planting/harvest ideal time)
    current_month = datetime.datetime.now().month
    if current_month in crop["planting_months"] or current_month in crop["harvest_months"]:
        month_score = 10
    else:
        month_score = 5 # Not ideal but not disastrous

    score = temp_score + humidity_score + rainfall_score + soil_score + month_score
    return int(score) # Return as integer percentage

def get_recommendations(crop_key, weather, soil_type):
    """Generates AI-powered recommendations for a given crop based on weather and soil."""
    crop = crops[crop_key]
    current_month = datetime.datetime.now().month
    recs = []

    # --- Soil Compatibility ---
    if soil_type.lower() == "choose soil type":
        recs.append({"type": "info", "text": "❓ **Soil Type Not Selected:** Please select your soil type to get more accurate recommendations."})
    elif soil_type.lower() not in crop["suitable_soils"]:
        recs.append({"type": "warning", "text": f"⚠️ **Soil Mismatch!** Your selected soil ({soil_type.title()}) is generally not ideal for {crop['name']}. This might impact growth and yield. Consider soil amendments or choosing a more suitable crop."})
    else:
        recs.append({"type": "success", "text": f"✅ **Soil Compatibility:** {crop['name']} is well-suited for {soil_type.title()} soil."})

    # --- Temperature Analysis ---
    temp = weather["temperature"]
    tmin, tmax = crop["optimal_temp"]
    if temp < tmin - 5:
        recs.append({"type": "warning", "text": f"🥶 **Extreme Cold ({temp}°C)!** Significantly below optimal ({tmin}-{tmax}°C). Severe impact likely. Strong frost protection or delaying planting is critical."})
    elif temp < tmin:
        recs.append({"type": "warning", "text": f"⬇️ Temperature {temp}°C is low for {crop['name']} (optimal: {tmin}-{tmax}°C). Growth might be stunted. Use crop covers or choose a warmer planting time."})
    elif temp > tmax + 5:
        recs.append({"type": "warning", "text": f"🥵 **Extreme Heat ({temp}°C)!** Far above optimal ({tmin}-{tmax}°C). Risk of wilting, sun-scald, and yield loss. Increase irrigation significantly and consider shade nets during peak sun."})
    elif temp > tmax:
        recs.append({"type": "warning", "text": f"⬆️ Temperature {temp}°C is high for {crop['name']} (optimal: {tmin}-{tmax}°C). Ensure adequate watering to prevent heat stress and monitor for signs of scorching."})
    else:
        recs.append({"type": "success", "text": f"☀️ **Optimal Temperature!** The current temperature of {temp}°C is perfect for {crop['name']}."})

    # --- Humidity Analysis ---
    humidity = weather["humidity"]
    hmin, hmax = crop["optimal_humidity"]
    if humidity < hmin - 10:
        recs.append({"type": "warning", "text": f"🏜️ **Very Low Humidity ({humidity}%):** Significantly below optimal ({hmin}-{hmax}%). This can lead to rapid moisture loss and stress. Increase irrigation frequency and consider misting systems."})
    elif humidity < hmin:
        recs.append({"type": "warning", "text": f"💧 Humidity {humidity}% is low for {crop['name']} (optimal: {hmin}-{hmax}%). Ensure consistent watering to compensate for increased evaporation."})
    elif humidity > hmax + 10:
        recs.append({"type": "warning", "text": f"💦 **Very High Humidity ({humidity}%):** Well above optimal ({hmin}-{hmax}%). This significantly increases the risk of fungal diseases, rot, and pest issues. Ensure good air circulation and consider preventative fungicides."})
    elif humidity > hmax:
        recs.append({"type": "warning", "text": f"⬆️ Humidity {humidity}% is high for {crop['name']} (optimal: {hmin}-{hmax}%). Monitor for signs of fungal infections and ensure adequate ventilation."})
    else:
        recs.append({"type": "success", "text": f"✅ **Optimal Humidity!** The current humidity of {humidity}% is ideal for {crop['name']}."})

    # --- Rainfall Analysis ---
    rainfall = weather["rainfall"] # 1-hour rainfall
    if rainfall > 15: # Heavy rain
        recs.append({"type": "warning", "text": f"🌧️ **Heavy Rainfall ({rainfall}mm)!** Expect potential waterlogging. Ensure excellent drainage to prevent root rot and soil erosion. Protect vulnerable plants."})
    elif rainfall > 5: # Moderate rain
        recs.append({"type": "info", "text": f"☔ **Moderate Rainfall ({rainfall}mm).** Provides good natural watering. Monitor soil moisture; additional irrigation might be minimal."})
    elif rainfall > 0 and rainfall <= 5: # Light rain
         recs.append({"type": "info", "text": f"💧 **Light Rainfall ({rainfall}mm).** Beneficial light moisture. Check soil regularly as supplemental irrigation may still be needed, especially for high water crops."})
    elif math.isclose(rainfall, 0.0, abs_tol=0.1) and crop["water"] == "high": # Using math.isclose for float comparison
        recs.append({"type": "warning", "text": f"☀️ **No Significant Rainfall.** {crop['name']} needs high water. Provide consistent and ample irrigation to prevent drought stress."})
    elif math.isclose(rainfall, 0.0, abs_tol=0.1) and crop["water"] == "medium":
        recs.append({"type": "info", "text": f"☀️ **No Significant Rainfall.** {crop['name']} needs medium water. Check soil moisture daily and irrigate as needed to maintain adequate moisture."})
    else:
        recs.append({"type": "success", "text": f"💧 Current rainfall ({rainfall}mm) is manageable and should not pose an immediate threat or major benefit for {crop['name']}."})

    # --- Wind Speed Analysis ---
    wind_speed = weather["wind_speed"]
    if wind_speed > 15: # Very strong winds
        recs.append({"type": "warning", "text": f"💨 **Very Strong Winds ({wind_speed} m/s)!** High risk of physical damage, lodging, and rapid moisture loss. Provide strong staking, windbreaks, or protection."})
    elif wind_speed > 8: # Strong winds
        recs.append({"type": "warning", "text": f"🌬️ **Strong Winds ({wind_speed} m/s)!** Can cause physical damage, stress, and increased water loss for {crop['name']}. Consider windbreaks or staking for taller crops."})
    elif wind_speed > 3: # Moderate winds
        recs.append({"type": "info", "text": f"🍃 **Moderate Winds ({wind_speed} m/s).** Good for air circulation, which can help prevent fungal issues. Monitor moisture levels as evaporation will be higher."})
    else:
        recs.append({"type": "success", "text": f"✅ Wind speed ({wind_speed} m/s) is calm and favorable for {crop['name']}."})


    # --- Monthly Activity Recommendations ---
    if current_month in crop["planting_months"]:
        recs.append({"type": "info", "text": f"🪴 **Optimal Planting Window!** This is an ideal month to plant {crop['name']}. Ensure all preparations are complete."})
    else:
        # Check if planting month is upcoming or past
        upcoming_planting_months = [m for m in crop["planting_months"] if m > current_month]
        if upcoming_planting_months:
            recs.append({"type": "info", "text": f"🗓️ The best planting months for {crop['name']} are: {', '.join(datetime.date(1900, m, 1).strftime('%B') for m in crop['planting_months'])}. Your next window is in {datetime.date(1900, min(upcoming_planting_months), 1).strftime('%B')}."})
        else:
            recs.append({"type": "info", "text": f"🗓️ The best planting months for {crop['name']} are: {', '.join(datetime.date(1900, m, 1).strftime('%B') for m in crop['planting_months'])}. Consider planning for next year or using appropriate off-season cultivation methods (e.g., greenhouses)."})

    if current_month in crop["harvest_months"]:
        recs.append({"type": "info", "text": f"🌾 **Harvest Season!** This is a good time to harvest {crop['name']}. Monitor maturity closely."})
    else:
        # Check if harvest month is upcoming or past
        upcoming_harvest_months = [m for m in crop["harvest_months"] if m > current_month]
        if upcoming_harvest_months:
            recs.append({"type": "info", "text": f"📅 The main harvest months for {crop['name']} are: {', '.join(datetime.date(1900, m, 1).strftime('%B') for m in crop['harvest_months'])}. Your next harvest period is in {datetime.date(1900, min(upcoming_harvest_months), 1).strftime('%B')}."})
        else:
            recs.append({"type": "info", "text": f"📅 The main harvest months for {crop['name']} are: {', '.join(datetime.date(1900, m, 1).strftime('%B') for m in crop['harvest_months'])}. Focus on post-harvest activities or preparing for the next growing cycle."})

    # --- Disease/Pest Risk Assessment ---
    if humidity > 85 and temp > 28:
        recs.append({"type": "warning", "text": f"🦠 **Very High Disease Risk!** With {humidity}% humidity and {temp}°C, conditions are highly favorable for aggressive fungal and bacterial diseases. Implement strong preventative measures and monitor daily."})
    elif humidity > 75 and temp > 22:
        recs.append({"type": "info", "text": f"🐞 **Elevated Disease Risk.** High humidity and warm temperatures create favorable conditions for many diseases and pests. Monitor your crops closely for early signs and maintain good sanitation."})
    else:
        recs.append({"type": "success", "text": f"✨ **Low Disease Risk.** Current conditions are less conducive for widespread disease outbreaks. Maintain good plant health."})

    # --- Overall Assessment (Added to the top for immediate visibility) ---
    suitability_score = calculate_suitability_score(crop_key, weather, soil_type)
    if suitability_score >= 80:
        recs.insert(0, {"type": "success", "text": f"🌟 **Excellent Overall Suitability!** Conditions are highly favorable for {crop['name']}. You have a great chance for a bountiful yield!"})
    elif suitability_score >= 60:
        recs.insert(0, {"type": "info", "text": f"👍 **Good Overall Suitability!** Conditions are generally favorable for {crop['name']}. Minor adjustments might be beneficial. Pay attention to specific advisories."})
    elif suitability_score >= 40:
        recs.insert(0, {"type": "warning", "text": f"⚠️ **Moderate Overall Suitability.** Some challenging factors are present. Review detailed recommendations and consider management strategies."})
    else:
        recs.insert(0, {"type": "error", "text": f"🚫 **Low Overall Suitability!** Significant challenges detected for {crop['name']} under current conditions. Carefully review warnings and consider if this is the right crop for now."})

    return recs

# --- Streamlit App ---
st.set_page_config(
    page_title="AgroSense AI: Smart Crop Advisor",
    page_icon="🌱",
    layout="wide", # Use wide layout for better visual analytics
    initial_sidebar_state="auto"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Ensure the entire app background is black */
    .stApp {
        background-color: #000000; /* Pure black */
        color: #f0f2f6; /* Light text for readability */
    }
    body {
        background-color: #000000; /* Fallback for body */
        color: #f0f2f6;
    }

    /* Main content container */
    .main .block-container {
        background-color: #1a1a1a; /* Dark grey for content blocks */
        border-radius: 1rem;
        padding: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5); /* Stronger shadow for depth */
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* Main title */
    h1 {
        color: #81c784; /* Lighter green for title */
        text-align: center;
        font-size: 3.2em;
        margin-bottom: 0.5em;
        font-weight: 700;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5); /* Darker shadow for light text */
    }

    /* Subheaders (h2) */
    h2 {
        color: #a5d6a7; /* Lighter green */
        border-bottom: 2px solid #66bb6a; /* Medium green border */
        padding-bottom: 0.6em;
        margin-top: 2em;
        font-weight: 600;
        font-size: 2em;
    }

    /* Smaller headers (h3) */
    h3 {
        color: #c8e6c9; /* Even lighter green */
        margin-top: 1.5em;
        font-weight: 500;
        font-size: 1.6em;
    }

    /* Even smaller headers (h5 for charts) */
    h5 {
        color: #bbb; /* Light grey for chart titles */
        font-size: 1.1em;
        text-align: center;
        margin-bottom: 0.8em;
    }

    /* Buttons */
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        font-weight: bold;
        border-radius: 0.75rem; /* More rounded */
        border: none;
        padding: 0.8rem 1.8rem;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.25); /* Stronger shadow */
        transition: all 0.3s ease-in-out;
        cursor: pointer;
        font-size: 1.1em;
    }
    .stButton>button:hover {
        background-color: #388e3c; /* Darker green on hover */
        transform: translateY(-3px); /* Lift effect */
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
    }

    /* Metrics (for current weather display) */
    .stMetric {
        background-color: #333333; /* Dark grey for metrics */
        color: #f0f2f6; /* Light text for contrast */
        border-left: 6px solid #4CAF50; /* Green border */
        padding: 1.2rem;
        border-radius: 0.75rem;
        box-shadow: 2px 2px 7px rgba(0,0,0,0.2); /* Soft shadow */
        margin-bottom: 1rem;
        text-align: center; /* Center content */
    }
    .stMetric label {
        font-weight: 600;
        color: #a5d6a7; /* Lighter green for label */
        font-size: 1.05em;
    }
    .stMetric div[data-testid="stMetricValue"] {
        font-size: 1.8em;
        color: #f0f2f6; /* Light value text */
        font-weight: bold;
    }
    .stMetric div[data-testid="stMetricDelta"] {
        font-size: 0.9em;
        color: #b3e5fc; /* Light blue for delta */
    }

    /* Alert boxes (success, warning, info, error) */
    .stAlert {
        border-radius: 0.75rem;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.2);
        font-size: 1.05em;
    }
    .stSuccess {
        background-color: #2e7d32; /* Darker green for success */
        color: white; /* White text */
        border-left: 6px solid #4caf50;
    }
    .stWarning {
        background-color: #ff8f00; /* Darker orange for warning */
        color: white; /* White text */
        border-left: 6px solid #ffa000;
    }
    .stInfo {
        background-color: #0277bd; /* Darker blue for info */
        color: white; /* White text */
        border-left: 6px solid #039be5;
    }
    .stError {
        background-color: #c62828; /* Darker red for error */
        color: white; /* White text */
        border-left: 6px solid #d32f2f;
    }

    /* Sidebar specific styling */
    .sidebar .sidebar-content {
        background-color: #262626; /* Slightly lighter dark grey for sidebar */
        padding: 1.5rem;
        border-right: 2px solid #444;
    }
    .css-1d391kg { /* Target for sidebar selectbox/text input labels */
        font-weight: 600;
        color: #a5d6a7; /* Lighter green for sidebar labels */
        margin-bottom: 0.5rem;
    }
    .stTextInput>div>div>input {
        background-color: #333333; /* Darker input background */
        color: #f0f2f6; /* Light text in input */
        border-radius: 0.5rem;
        border: 1px solid #555;
        padding: 0.6rem;
    }
    .stSelectbox>div>div>div {
        background-color: #333333; /* Darker selectbox background */
        color: #f0f2f6; /* Light text in selectbox */
        border-radius: 0.5rem;
        border: 1px solid #555;
        padding: 0.4rem;
    }
    .stSelectbox>div>div>div:focus {
        border-color: #4CAF50; /* Green highlight on focus */
    }
    /* Styles for the dropdown options list of the selectbox */
    div[data-baseweb="select"] > div:last-child {
        background-color: #262626; /* Darker background for dropdown list */
        color: #f0f2f6; /* Text color for dropdown options */
        border: 1px solid #4CAF50;
        border-radius: 0.5rem;
    }
    div[data-baseweb="select"] li { /* Individual options */
        color: #f0f2f6 !important;
    }
    div[data-baseweb="select"] li:hover { /* Hover on options */
        background-color: #4CAF50 !important;
        color: white !important;
    }


    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #4CAF50; /* Green progress bar */
    }
    .stProgress {
        margin-bottom: 1.5rem;
    }

    /* Small font for disclaimer/info */
    .stMarkdown small {
        color: #999;
    }

    /* Forecast cards */
    .forecast-card {
        background-color: #333333; /* Dark grey for forecast cards */
        color: #f0f2f6; /* Light text */
        border-radius: 0.75rem;
        padding: 1rem;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.3);
        text-align: center;
        margin-bottom: 1rem;
        height: 100%; /* Ensure cards are same height */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 1px solid #4CAF50; /* Green border for cards */
    }
    .forecast-card strong {
        color: #a5d6a7; /* Lighter green for strong text */
    }
    .forecast-card .stMetric {
        background-color: transparent; /* No background for metrics inside cards */
        border-left: none; /* No border for metrics inside cards */
        padding: 0.5rem 0;
        box-shadow: none;
        margin-bottom: 0.2rem;
    }
    .forecast-card .stMetric label {
        font-size: 0.9em;
        font-weight: normal;
        color: #c8e6c9; /* Light green label */
    }
    .forecast-card .stMetric div[data-testid="stMetricValue"] {
        font-size: 1.2em;
        font-weight: 600;
        color: #f0f2f6; /* Light value text */
    }
    .forecast-card .stMetric div[data-testid="stMetricDelta"] {
        display: none; /* Hide delta in forecast metrics */
    }
    /* Plotly chart adjustments for dark theme */
    .modebar-container {
        background-color: transparent !important;
    }
    .js-plotly-plot .plotly .cursor-pointer { /* Fix for plotly hover text color */
        fill: #f0f2f6 !important;
    }
    .js-plotly-plot .plotly .annotation-text { /* Fix for plotly annotation text color */
        fill: #f0f2f6 !important;
    }
    .js-plotly-plot .plotly .xaxislayer-above .xtick .ticktext { /* Fix for plotly x-axis tick text color */
        fill: #f0f2f6 !important;
    }
    .js-plotly-plot .plotly .yaxislayer-above .ytick .ticktext { /* Fix for plotly y-axis tick text color */
        fill: #f0f2f6 !important;
    }
    .js-plotly-plot .plotly .g-gtitle .gtitle { /* Fix for plotly title color */
        fill: #f0f2f6 !important;
    }
    .js-plotly-plot .plotly .traces .scatterlayer .fills { /* plotly fill color */
        fill: rgba(102,187,106,0.2) !important;
    }
    .js-plotly-plot .plotly .traces .scatterlayer .lines { /* plotly line color */
        stroke: rgba(102,187,106,0.5) !important;
    }

</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.title("🌾 AgroSense AI: Smart Crop Advisor")
st.markdown("### Your personal guide to smarter farming decisions! 🧑‍🌾")
st.write("Enter your location and crop details to get tailored advice based on current and forecasted weather conditions, and soil compatibility.")

# --- Sidebar for Inputs ---
st.sidebar.header("📍 Your Farm Details")
city = st.sidebar.text_input("Enter your city/town:", placeholder="e.g., Delhi, New York", key="city_input")
selected_crop_key = st.sidebar.selectbox(
    "Choose your crop:",
    list(crops.keys()),
    format_func=lambda c: crops[c]["name"],
    help="Select the crop you are interested in growing or currently cultivating.",
    key="crop_select"
)
selected_soil_type = st.sidebar.selectbox(
    "Select your soil type:",
    soil_types,
    help="Choosing the correct soil type helps in precise recommendations.",
    key="soil_select"
)

st.sidebar.markdown("---")
st.sidebar.info("Powered by OpenWeatherMap API and AI-driven agricultural knowledge.")

# --- Action Button ---
if st.sidebar.button("Get My Crop Advice 🌱", key="get_advice_button"):
    if not city:
        st.error("Please enter a city name to get weather data and recommendations.")
        st.stop()
    if selected_soil_type == "Choose Soil Type":
        st.warning("Please select your soil type for more accurate recommendations.")
        # Don't stop, but highlight importance

    with st.spinner(f"Fetching weather for {city} and generating recommendations..."):
        try:
            current_weather_data = fetch_weather(city)
            forecast_data = fetch_forecast(city) # Fetch forecast as well

            st.session_state["current_weather_data"] = current_weather_data
            st.session_state["forecast_data"] = forecast_data
            st.session_state["selected_crop_key"] = selected_crop_key
            st.session_state["selected_soil_type"] = selected_soil_type
            st.session_state["city"] = city
            st.success("Weather data fetched and recommendations generated!")

        except Exception as e:
            st.error(f"**Oops!** Encountered an issue: {e}")
            st.error("Please ensure your city name is correct, your API key is valid, and check your internet connection.")
            st.session_state["current_weather_data"] = None # Clear data on error
            st.session_state["forecast_data"] = None


# --- Display Results ---
if "current_weather_data" in st.session_state and st.session_state["current_weather_data"]:
    city_display = st.session_state["city"].title()
    selected_crop = crops[st.session_state["selected_crop_key"]]
    current_weather = st.session_state["current_weather_data"]
    forecast = st.session_state["forecast_data"]
    selected_soil = st.session_state["selected_soil_type"]

    st.markdown("---")

    # --- Crop Suitability Score ---
    score = calculate_suitability_score(st.session_state["selected_crop_key"], current_weather, selected_soil)
    st.subheader(f"✨ Crop Suitability Score for {selected_crop['name']}")
    st.progress(score / 100.0, text=f"Overall Suitability: **{score}%**")
    if score >= 80:
        st.success("Conditions are highly favorable! This is a great match for your crop.")
    elif score >= 60:
        st.info("Conditions are generally good. Pay attention to specific recommendations.")
    elif score >= 40:
        st.warning("Conditions are moderate. You might face some challenges; review advisories carefully.")
    else:
        st.error("Conditions are challenging. Significant adjustments or alternative crop consideration might be needed.")

    st.markdown("---")

    # --- Current Weather Dashboard ---
    st.subheader(f"🌐 Current Weather in {city_display}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Temperature", value=f"{current_weather['temperature']:.1f}C", delta=f"Feels like {current_weather['feels_like']:.1f}C")
        st.image(OWM_ICON_URL.format(icon_code=current_weather['icon']), caption=current_weather['condition'].title(), width=70)
    with col2:
        st.metric(label="Humidity", value=f"{current_weather['humidity']}%")
    with col3:
        st.metric(label="Wind", value=f"{current_weather['wind_speed']:.1f} m/s", delta=f"{current_weather['wind_direction']}")
    with col4:
        st.metric(label="Rainfall (last 1h)", value=f"{current_weather['rainfall']:.1f} mm")
        st.metric(label="Current Month", value=datetime.datetime.now().strftime("%B"))

    st.markdown("---")

    # --- Visual Analytics Dashboard (Current Weather vs. Optimal) ---
    st.subheader(f"📊 {selected_crop['name']} - Environmental Snapshot")
    temp_optimal_range = list(selected_crop["optimal_temp"])
    humidity_optimal_range = list(selected_crop["optimal_humidity"])

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("##### Temperature vs. Optimal Range")
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=['Current', 'Optimal Min', 'Optimal Max'],
            y=[current_weather['temperature'], temp_optimal_range[0], temp_optimal_range[1]],
            mode='markers',
            marker=dict(size=[20, 10, 10], color=['#ef5350', '#66bb6a', '#66bb6a']), # Red for current, green for optimal
            name='Temperature'
        ))
        fig_temp.add_shape(type="rect",
            x0=-0.5, y0=temp_optimal_range[0], x1=2.5, y1=temp_optimal_range[1],
            line=dict(color="rgba(102,187,106,0.5)", width=2),
            fillcolor="rgba(102,187,106,0.2)", # Green shaded area
            layer="below"
        )
        fig_temp.update_layout(
            yaxis_title="Temperature (°C)",
            showlegend=False,
            height=300,
            margin=dict(l=40, r=40, t=40, b=40),
            plot_bgcolor='rgba(0,0,0,0)', # Transparent plot background
            paper_bgcolor='rgba(0,0,0,0)', # Transparent paper background
            font=dict(color="#f0f2f6") # Chart text color
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_chart2:
        st.markdown("##### Humidity vs. Optimal Range")
        fig_hum = go.Figure()
        fig_hum.add_trace(go.Scatter(
            x=['Current', 'Optimal Min', 'Optimal Max'],
            y=[current_weather['humidity'], humidity_optimal_range[0], humidity_optimal_range[1]],
            mode='markers',
            marker=dict(size=[20, 10, 10], color=['#29b6f6', '#66bb6a', '#66bb6a']), # Blue for current, green for optimal
            name='Humidity'
        ))
        fig_hum.add_shape(type="rect",
            x0=-0.5, y0=humidity_optimal_range[0], x1=2.5, y1=humidity_optimal_range[1],
            line=dict(color="rgba(102,187,106,0.5)", width=2),
            fillcolor="rgba(102,187,106,0.2)", # Green shaded area
            layer="below"
        )
        fig_hum.update_layout(
            yaxis_title="Humidity (%)",
            showlegend=False,
            height=300,
            margin=dict(l=40, r=40, t=40, b=40),
            plot_bgcolor='rgba(0,0,0,0)', # Transparent plot background
            paper_bgcolor='rgba(0,0,0,0)', # Transparent paper background
            font=dict(color="#f0f2f6") # Chart text color
        )
        st.plotly_chart(fig_hum, use_container_width=True)


    st.markdown("---")

    st.subheader(f"🌱 {selected_crop['name']} - Crop Insights")
    st.info(f"**About {selected_crop['name']}:** {selected_crop['description']}")

    st.markdown("### 🤖 Personalized Recommendations")
    recommendations = get_recommendations(st.session_state["selected_crop_key"], current_weather, selected_soil)

    for i, rec in enumerate(recommendations):
        if rec["type"] == "success":
            st.success(rec["text"])
        elif rec["type"] == "warning":
            st.warning(rec["text"])
        elif rec["type"] == "info":
            st.info(rec["text"])
        elif rec["type"] == "error":
            st.error(rec["text"])
        else:
            st.write(rec["text"])


    st.markdown("---")

    # --- 5-Day Weather Forecast Panel ---
    if forecast:
        st.subheader("🗓️ 5-Day Weather Forecast")
        # Adjust column count based on number of forecast days, up to 5
        num_forecast_days = min(len(forecast), 5)
        forecast_cols = st.columns(num_forecast_days)
        for i, daily_forecast in enumerate(forecast[:num_forecast_days]):
            with forecast_cols[i]:
                st.markdown(f"<div class='forecast-card'>", unsafe_allow_html=True)
                st.markdown(f"**{daily_forecast['date'].strftime('%a, %b %d')}**")
                st.image(OWM_ICON_URL.format(icon_code=daily_forecast['icon']), width=60)
                st.caption(daily_forecast['condition'].title())
                st.metric(label="Temp Range", value=f"{daily_forecast['min_temp']:.1f}°C - {daily_forecast['max_temp']:.1f}°C")
                st.metric(label="Avg. Humidity", value=f"{daily_forecast['avg_humidity']:.0f}%")
                st.metric(label="Total Rain", value=f"{daily_forecast['total_rainfall']:.1f} mm")
                st.markdown(f"</div>", unsafe_allow_html=True)
    else:
        st.info("No 5-day forecast available. (This might be due to API limitations or an error during fetch.)")

    st.markdown("---")
    st.subheader("💡 Sustainable Farming Tip")
    st.write(f"**Did you know?** Implementing **cover crops** during off-seasons can significantly improve soil health, reduce erosion, and suppress weeds, benefiting crops like {selected_crop['name']} in the long run! 🌱")

    st.markdown("---")
    st.caption("Disclaimer: This tool provides AI-generated recommendations based on general agricultural guidelines and OpenWeatherMap data. Always consult with local agricultural experts for precise advice tailored to your specific farm conditions and local regulations.")