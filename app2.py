import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ---- Init marker session state (NEW) ----
if "clicked_lat" not in st.session_state:
    st.session_state.clicked_lat = None
if "clicked_lon" not in st.session_state:
    st.session_state.clicked_lon = None

# ---- Weather Fetcher ----
def get_forecast(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max"
        "&timezone=auto"
    )
    data = requests.get(url).json()
    return data.get("daily")

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
    80: "🌦️ Showers",
    81: "🌧️ Showers",
    82: "⛈️ Showers",
    95: "⛈️ Thunderstorm",
    96: "⛈️ Thunderstorm",
    99: "⛈️ Thunderstorm",
}

st.title("7-Day Weather Forecast (Open-Meteo) 🌍")
st.write("Click the map to view the forecast and see a pin marker.")

# ---- Interactive Map ----
m = folium.Map(location=[35, 135], zoom_start=4)

# (NEW) Draw marker if exists
if st.session_state.clicked_lat is not None:
    folium.Marker(
        location=[st.session_state.clicked_lat, st.session_state.clicked_lon],
        popup="Selected Location",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

map_data = st_folium(m, key="map", height=500, width=900)

# ---- Capture click ----
if map_data and map_data.get("last_clicked"):
    st.session_state.clicked_lat = map_data["last_clicked"]["lat"]
    st.session_state.clicked_lon = map_data["last_clicked"]["lng"]

# ---- Show weather if pin exists ----
if st.session_state.clicked_lat is not None:
    lat = st.session_state.clicked_lat
    lon = st.session_state.clicked_lon

    st.success(f"Coordinates: {lat:.4f}, {lon:.4f}")

    daily = get_forecast(lat, lon)

    if daily:
        df = pd.DataFrame({
            "date": pd.to_datetime(daily["time"]),
            "tmax": daily["temperature_2m_max"],
            "tmin": daily["temperature_2m_min"],
            "precip": daily["precipitation_sum"],
            "wind": daily["windspeed_10m_max"],
            "code": daily["weathercode"]
        })

        # Cards
        st.subheader("📅 Daily Forecast")
        cols = st.columns(7)
        for i, row in df.iterrows():
            with cols[i]:
                st.markdown(f"**{row['date'].strftime('%a')}**")
                st.caption(row['date'].strftime('%m/%d'))
                st.markdown(f"### {ICONS.get(row['code'], '🌡️')}")
                st.write(f"High: {row['tmax']}°C")
                st.write(f"Low: {row['tmin']}°C")
                st.caption(f"💧 {row['precip']} mm")
                st.caption(f"💨 {row['wind']} km/h")

        # Temperature chart
        st.write("---")
        st.subheader("🌡️ Temperature Trend")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["tmax"], name="High Temp",
            mode="lines+markers", line=dict(width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["tmin"], name="Low Temp",
            mode="lines+markers", line=dict(width=3)
        ))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to fetch forecast.")
else:
    st.info("Click the map to view forecast + place a pin!")
