import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

st.set_page_config(layout="wide")

# ---- Weather Fetcher (Open-Meteo) ----
def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
    )
    data = requests.get(url).json()

    if "current" not in data:
        return None
    
    return {
        "temp": data["current"]["temperature_2m"],
        "humidity": data["current"]["relative_humidity_2m"],
        "wind": data["current"]["wind_speed_10m"],
        "code": data["current"]["weather_code"]
    }

# Weather code decoder
WEATHER_DESC = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Depositing rime fog ❄️🌫️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌧️",
    55: "Dense drizzle 🌧️",
    61: "Light rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️🌧️",
    71: "Light snow 🌨️",
    73: "Moderate snow 🌨️❄️",
    75: "Heavy snow ❄️❄️🌨️",
    95: "Thunderstorm ⛈️",
}

st.title("Interactive Weather Map (Open-Meteo) 🌍")
st.write("Click anywhere to get instant weather — no API key needed.")

# ---- Map ----
m = folium.Map(location=[35, 135], zoom_start=4)
map_data = st_folium(m, key="map", height=500, width=900)

# ---- Auto Update on Click ----
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    weather = get_weather(lat, lon)

    st.success(f"Coordinates: {lat:.4f}, {lon:.4f}")

    if weather:
        desc = WEATHER_DESC.get(weather["code"], "Unknown weather")
        st.subheader(f"{desc}")
        st.write(f"**Temperature:** {weather['temp']} °C")
        st.write(f"**Humidity:** {weather['humidity']} %")
        st.write(f"**Wind Speed:** {weather['wind']} m/s")
    else:
        st.error("No weather data returned for this location.")
else:
    st.info("Click a point on the map to view weather.")
