import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

# ---- Weather Fetcher ----
def get_weather(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    data = requests.get(url).json()
    
    if "main" not in data:
        return None
    
    return {
        "location": data["name"],
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "desc": data["weather"][0]["description"]
    }

# ---- Streamlit UI ----
st.title("Interactive Weather Map 🌍")

# Set your API key
API_KEY = "YOUR_API_KEY_HERE"

# Default map center
m = folium.Map(location=[35.0, 135.0], zoom_start=4)

# Display map and detect clicks
map_data = st_folium(m, width=700, height=500)

# Show weather automatically when clicked
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    weather = get_weather(lat, lon, API_KEY)

    if weather:
        st.subheader("Weather Information 🌦️")
        st.write(f"**Location:** {weather['location']}")
        st.write(f"**Temperature:** {weather['temp']} °C")
        st.write(f"**Humidity:** {weather['humidity']} %")
        st.write(f"**Description:** {weather['desc']}")
    else:
        st.error("No weather data found for this location.")
else:
    st.info("Click anywhere on the map to view weather 🌡️")

