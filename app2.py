import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ---- Weather Fetcher (Daily Forecast) ----
def get_forecast(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max"
        "&timezone=auto"
    )
    data = requests.get(url).json()
    
    if "daily" not in data:
        return None
    
    return data["daily"]

# Weather icon decoder
ICONS = {
    0: "☀️ Clear",
    1: "🌤️ Mainly clear",
    2: "⛅ Partly cloudy",
    3: "☁️ Overcast",
    45: "🌫️ Fog",
    48: "🌫️ Fog",
    51: "🌦️ Drizzle",
    53: "🌦️ Drizzle",
    55: "🌧️ Drizzle",
    61: "🌧️ Rain",
    63: "🌧️ Rain",
    65: "🌧️ Heavy rain",
    71: "🌨️ Snow",
    73: "🌨️ Snow",
    75: "❄️ Heavy snow",
    80: "🌦️ Rain showers",
    81: "🌧️ Rain showers",
    82: "⛈️ Rain showers",
    95: "⛈️ Thunderstorm",
    96: "⛈️ Thunderstorm",
    99: "⛈️ Thunderstorm",
}

st.title("7-Day Weather Forecast (Open-Meteo) 🌎")
st.write("Click anywhere on the map to instantly view the 7-day forecast.")

# ---- Interactive map ----
m = folium.Map(location=[35, 135], zoom_start=4)
map_data = st_folium(m, key="map", height=500, width=900)

# ---- Auto-update on click ----
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    st.success(f"Coordinates: {lat:.4f}, {lon:.4f}")

    daily = get_forecast(lat, lon)

    if daily:
        # Convert to DataFrame
        df = pd.DataFrame({
            "date": pd.to_datetime(daily["time"]),
            "tmax": daily["temperature_2m_max"],
            "tmin": daily["temperature_2m_min"],
            "precip": daily["precipitation_sum"],
            "wind": daily["windspeed_10m_max"],
            "code": daily["weathercode"]
        })

        # ---- Display daily cards ----
        st.subheader("📅 Daily Forecast")
        cols = st.columns(7)

        for i, row in df.iterrows():
            with cols[i]:
                st.markdown(f"**{row['date'].strftime('%a')}**")
                st.caption(row['date'].strftime('%m/%d'))
                st.markdown(f"### {ICONS.get(row['code'], '🌡️')}")
                st.write(f"**High:** {row['tmax']}°C")
                st.write(f"**Low:** {row['tmin']}°C")
                st.caption(f"💧 {row['precip']} mm")
                st.caption(f"💨 {row['wind']} km/h")

        # ---- Temperature trend chart ----
        st.write("---")
        st.subheader("🌡️ Temperature Trend")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["tmax"],
            name="High Temp", mode="lines+markers", line=dict(width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["tmin"],
            name="Low Temp", mode="lines+markers", line=dict(width=3)
        ))
        fig.update_layout(height=400, yaxis_title="°C")

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Failed to retrieve forecast data.")
else:
    st.info("Click a point on the map to view the weekly forecast.")
