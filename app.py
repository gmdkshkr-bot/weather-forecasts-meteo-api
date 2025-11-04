import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
import datetime

st.set_page_config(layout="wide")

# Default coordinates (Seoul)
DEFAULT_LAT = 37.5665
DEFAULT_LON = 126.9780

# --- Session State Setup ---
if "lat" not in st.session_state:
    st.session_state.lat = DEFAULT_LAT
if "lon" not in st.session_state:
    st.session_state.lon = DEFAULT_LON

st.title("Interactive Weather Map (7-Day Forecast)")

# --- Build map centered on last clicked position ---
m = folium.Map(location=[st.session_state.lat, st.session_state.lon],
               zoom_start=8)

# Add marker
folium.Marker(
    location=[st.session_state.lat, st.session_state.lon],
    popup="Selected Location",
    tooltip="Selected"
).add_to(m)

# --- Render map ---
map_data = st_folium(m, height=500, width=800)

# --- If user clicks map, update session state ---
if map_data and map_data.get("last_clicked"):
    st.session_state.lat = map_data["last_clicked"]["lat"]
    st.session_state.lon = map_data["last_clicked"]["lng"]

# --- Call Open-Meteo API ---
weather_url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={st.session_state.lat}&longitude={st.session_state.lon}"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
    "&current_weather=true&timezone=auto"
)

response = requests.get(weather_url).json()

st.subheader("Current Weather")
current = response.get("current_weather", {})
st.write(current)

# --- 7-Day Forecast ---
st.subheader("7-Day Forecast")

daily = response.get("daily", {})
dates = daily.get("time", [])
t_max = daily.get("temperature_2m_max", [])
t_min = daily.get("temperature_2m_min", [])
rain = daily.get("precipitation_probability_max", [])

for i in range(len(dates)):
    st.write(
        f"📅 {dates[i]} — 🌡️ Max: {t_max[i]}°C | 🌡️ Min: {t_min[i]}°C | 🌧️ Rain: {rain[i]}%"
)
