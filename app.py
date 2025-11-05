import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# Page setup
st.set_page_config(
    page_title="Weather Forecast App",
    page_icon="🌤️",
    layout="wide"
)

# Title
st.title("🌤️ Weather Forecast App")
st.write("Get 7-day weather forecast - Search by city or click on the map!")

# Initialize session state
if 'latitude' not in st.session_state:
    st.session_state.latitude = 37.5665
if 'longitude' not in st.session_state:
    st.session_state.longitude = 126.9780
if 'location_name' not in st.session_state:
    st.session_state.location_name = "Seoul, South Korea"

# Sidebar
with st.sidebar:
    st.header("📍 Select Location")
    
    # Method selection
    method = st.radio("Choose method:", ["🗺️ Click on Map", "🔍 Search City", "📝 Enter Coordinates"])
    
    if method == "🔍 Search City":
        city_name = st.text_input("Enter city name", placeholder="e.g., Seoul, London, New York")
        if st.button("Search City"):
            if city_name:
                # Get coordinates from city
                url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if data.get('results'):
                    result = data['results'][0]
                    st.session_state.latitude = result['latitude']
                    st.session_state.longitude = result['longitude']
                    st.session_state.location_name = f"{result['name']}, {result.get('country', '')}"
                    st.success(f"✅ Found: {st.session_state.location_name}")
                else:
                    st.error("City not found. Try another name.")
    
    elif method == "📝 Enter Coordinates":
        st.session_state.latitude = st.number_input("Latitude", value=st.session_state.latitude, format="%.4f")
        st.session_state.longitude = st.number_input("Longitude", value=st.session_state.longitude, format="%.4f")
    
    st.write("---")
    
    # Current location display
    st.info(f"**Current Location:**\n\n{st.session_state.location_name}\n\nLat: {st.session_state.latitude:.4f}\n\nLon: {st.session_state.longitude:.4f}")
    
    # Temperature unit
    temp_unit = st.radio("Temperature unit", ["Celsius (°C)", "Fahrenheit (°F)"])
    
    get_weather_btn = st.button("🔍 Get Forecast", type="primary", use_container_width=True)

# Main area - Map
if method == "🗺️ Click on Map":
    st.subheader("🗺️ Click on the map to select a location")
    
    # Create folium map
    m = folium.Map(
        location=[st.session_state.latitude, st.session_state.longitude],
        zoom_start=5
    )
    
    # Add marker at current location
    folium.Marker(
        [st.session_state.latitude, st.session_state.longitude],
        popup=st.session_state.location_name,
        tooltip="Current Location"
    ).add_to(m)
    
    # Display map and get click data
    map_data = st_folium(m, width=700, height=500)
    
    # Update location if map was clicked
    if map_data and map_data.get('last_clicked'):
        st.session_state.latitude = map_data['last_clicked']['lat']
        st.session_state.longitude = map_data['last_clicked']['lng']
        st.session_state.location_name = f"Custom Location"
        st.rerun()

# Function to get weather forecast
def get_weather_forecast(lat, lon, temp_unit):
    try:
        temp_unit_param = "celsius" if temp_unit == "Celsius (°C)" else "fahrenheit"
        
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max",
            "temperature_unit": temp_unit_param,
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return data
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Weather code descriptions
def get_weather_description(code):
    weather_codes = {
        0: "☀️ Clear sky",
        1: "🌤️ Mainly clear",
        2: "⛅ Partly cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Foggy",
        48: "🌫️ Foggy",
        51: "🌦️ Light drizzle",
        53: "🌦️ Moderate drizzle",
        55: "🌧️ Dense drizzle",
        61: "🌧️ Slight rain",
        63: "🌧️ Moderate rain",
        65: "🌧️ Heavy rain",
        71: "🌨️ Slight snow",
        73: "🌨️ Moderate snow",
        75: "❄️ Heavy snow",
        80: "🌦️ Rain showers",
        81: "🌧️ Rain showers",
        82: "⛈️ Heavy rain showers",
        95: "⛈️ Thunderstorm",
        96: "⛈️ Thunderstorm with hail",
        99: "⛈️ Thunderstorm with hail"
    }
    return weather_codes.get(code, "🌡️ Unknown")

# Get weather when button clicked
if get_weather_btn:
    with st.spinner("Fetching weather forecast..."):
        weather_data = get_weather_forecast(st.session_state.latitude, st.session_state.longitude, temp_unit)
    
    if weather_data and 'daily' in weather_data:
        st.success("✅ Forecast retrieved!")
        
        # Extract data
        daily = weather_data['daily']
        dates = pd.to_datetime(daily['time'])
        temp_max = daily['temperature_2m_max']
        temp_min = daily['temperature_2m_min']
        precipitation = daily['precipitation_sum']
        weather_codes = daily['weathercode']
        wind_speed = daily['windspeed_10m_max']
        
        temp_symbol = "°C" if temp_unit == "Celsius (°C)" else "°F"
        
        # Display current location
        st.subheader(f"📍 {st.session_state.location_name}")
        
        # Create daily forecast cards
        st.subheader("📅 7-Day Forecast")
        
        cols = st.columns(7)
        for i, col in enumerate(cols):
            with col:
                date = dates[i]
                day_name = date.strftime("%a")
                date_str = date.strftime("%m/%d")
                
                st.markdown(f"**{day_name}**")
                st.caption(date_str)
                st.markdown(f"### {get_weather_description(weather_codes[i])}")
                st.metric("High", f"{temp_max[i]:.0f}{temp_symbol}")
                st.metric("Low", f"{temp_min[i]:.0f}{temp_symbol}")
                st.caption(f"💧 {precipitation[i]:.1f}mm")
                st.caption(f"💨 {wind_speed[i]:.0f}km/h")
        
        st.write("---")
        
        # Temperature chart
        st.subheader("🌡️ Temperature Trend")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=temp_max,
            name='High',
            mode='lines+markers',
            line=dict(color='red', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=temp_min,
            name='Low',
            mode='lines+markers',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=f"Temperature ({temp_symbol})",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Precipitation chart
        st.subheader("💧 Precipitation Forecast")
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=dates,
            y=precipitation,
            name='Precipitation',
            marker_color='lightblue'
        ))
        
        fig2.update_layout(
            xaxis_title="Date",
            yaxis_title="Precipitation (mm)",
            height=300
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Data table
        with st.expander("📊 View Detailed Data"):
            df = pd.DataFrame({
                'Date': dates.dt.strftime('%Y-%m-%d'),
                'Weather': [get_weather_description(code) for code in weather_codes],
                f'High ({temp_symbol})': temp_max,
                f'Low ({temp_symbol})': temp_min,
                'Precipitation (mm)': precipitation,
                'Wind Speed (km/h)': wind_speed
            })
            st.dataframe(df, use_container_width=True)

else:
    if not get_weather_btn:
        st.info("👈 Select a location using one of the methods in the sidebar, then click 'Get Forecast'!")
        
        st.write("### 🌍 Try These Popular Cities:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Asia**")
            st.write("- Seoul, South Korea")
            st.write("- Tokyo, Japan")
            st.write("- Singapore")
        
        with col2:
            st.write("**Europe**")
            st.write("- London, UK")
            st.write("- Paris, France")
            st.write("- Berlin, Germany")
        
        with col3:
            st.write("**Americas**")
            st.write("- New York, USA")
            st.write("- Los Angeles, USA")
            st.write("- Toronto, Canada")

st.write("---")
st.caption("Data provided by Open-Meteo API (https://open-meteo.com/)")
