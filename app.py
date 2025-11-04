import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Page setup
st.set_page_config(
    page_title="Weather Forecast App",
    page_icon="🌤️",
    layout="wide"
)

# Title
st.title("🌤️ Weather Forecast App")
st.write("Get 7-day weather forecast for any location!")

# Initialize session state
if 'latitude' not in st.session_state:
    st.session_state.latitude = 37.5665
if 'longitude' not in st.session_state:
    st.session_state.longitude = 126.9780

# Sidebar
with st.sidebar:
    st.header("📍 Select Location")
    
    # Method tabs
    tab1, tab2 = st.tabs(["🗺️ Map", "🔍 Search"])
    
    with tab1:
        st.write("**Click on the map in the main area →**")
        st.write("The map will update your location automatically!")
    
    with tab2:
        city_name = st.text_input("Enter city name", placeholder="e.g., Seoul, London, New York")
        if st.button("Search City", use_container_width=True):
            if city_name:
                try:
                    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
                    response = requests.get(url, timeout=10)
                    data = response.json()
                    
                    if data.get('results'):
                        result = data['results'][0]
                        st.session_state.latitude = result['latitude']
                        st.session_state.longitude = result['longitude']
                        st.success(f"✅ Found: {result['name']}, {result.get('country', '')}")
                        st.rerun()
                    else:
                        st.error("City not found. Try another name.")
                except:
                    st.error("Error searching city.")
    
    st.write("---")
    
    # Manual coordinates
    st.write("**Or enter coordinates:**")
    lat_input = st.number_input("Latitude", value=float(st.session_state.latitude), format="%.4f", key="lat_input")
    lon_input = st.number_input("Longitude", value=float(st.session_state.longitude), format="%.4f", key="lon_input")
    
    if st.button("Use These Coordinates", use_container_width=True):
        st.session_state.latitude = lat_input
        st.session_state.longitude = lon_input
        st.rerun()
    
    st.write("---")
    
    # Current location
    st.info(f"**Current Location:**\n\nLat: {st.session_state.latitude:.4f}\n\nLon: {st.session_state.longitude:.4f}")
    
    # Temperature unit
    temp_unit = st.radio("Temperature unit", ["Celsius (°C)", "Fahrenheit (°F)"])
    
    st.write("---")
    
    get_weather_btn = st.button("🔍 GET WEATHER FORECAST", type="primary", use_container_width=True)

# Main area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🗺️ Select Location on Map")
    st.write("Click anywhere on the map to set your location!")
    
    # Create a simple clickable map using HTML/JavaScript
    map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            #map {{ height: 500px; width: 100%; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([{st.session_state.latitude}, {st.session_state.longitude}], 6);
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);
            
            var marker = L.marker([{st.session_state.latitude}, {st.session_state.longitude}]).addTo(map);
            
            map.on('click', function(e) {{
                var lat = e.latlng.lat.toFixed(4);
                var lon = e.latlng.lng.toFixed(4);
                
                if (marker) {{
                    map.removeLayer(marker);
                }}
                marker = L.marker([lat, lon]).addTo(map);
                
                // Send data back to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: {{ lat: parseFloat(lat), lon: parseFloat(lon) }}
                }}, '*');
            }});
        </script>
    </body>
    </html>
    """
    
    # Display map with component
    import streamlit.components.v1 as components
    map_data = components.html(map_html, height=500)
    
    # Try to get clicked location
    if map_data and isinstance(map_data, dict):
        if 'lat' in map_data and 'lon' in map_data:
            st.session_state.latitude = map_data['lat']
            st.session_state.longitude = map_data['lon']
            st.rerun()
    
    st.caption("💡 Tip: Click directly on the map to choose any location in the world!")

with col2:
    st.subheader("📊 Weather Information")
    
    if get_weather_btn:
        with st.spinner("Fetching weather forecast..."):
            try:
                # Get weather data
                temp_unit_param = "celsius" if temp_unit == "Celsius (°C)" else "fahrenheit"
                temp_symbol = "°C" if temp_unit == "Celsius (°C)" else "°F"
                
                url = "https://api.open-meteo.com/v1/forecast"
                params = {
                    "latitude": st.session_state.latitude,
                    "longitude": st.session_state.longitude,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max",
                    "temperature_unit": temp_unit_param,
                    "timezone": "auto"
                }
                
                response = requests.get(url, params=params, timeout=10)
                weather_data = response.json()
                
                if 'daily' in weather_data:
                    st.success("✅ Forecast retrieved!")
                    
                    # Weather codes
                    def get_weather_icon(code):
                        icons = {
                            0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
                            45: "🌫️", 48: "🌫️",
                            51: "🌦️", 53: "🌦️", 55: "🌧️",
                            61: "🌧️", 63: "🌧️", 65: "🌧️",
                            71: "🌨️", 73: "🌨️", 75: "❄️",
                            80: "🌦️", 81: "🌧️", 82: "⛈️",
                            95: "⛈️", 96: "⛈️", 99: "⛈️"
                        }
                        return icons.get(code, "🌡️")
                    
                    daily = weather_data['daily']
                    dates = pd.to_datetime(daily['time'])
                    
                    # Show today's weather prominently
                    st.markdown(f"### Today: {dates[0].strftime('%B %d, %Y')}")
                    st.markdown(f"## {get_weather_icon(daily['weathercode'][0])} {daily['temperature_2m_max'][0]:.0f}{temp_symbol} / {daily['temperature_2m_min'][0]:.0f}{temp_symbol}")
                    st.write(f"💧 Precipitation: {daily['precipitation_sum'][0]:.1f}mm")
                    st.write(f"💨 Wind: {daily['windspeed_10m_max'][0]:.0f}km/h")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.info("👈 Click 'GET WEATHER FORECAST' in the sidebar after selecting your location!")
        st.write("### Quick Start:")
        st.write("1️⃣ Click anywhere on the map")
        st.write("2️⃣ Or search for a city name")
        st.write("3️⃣ Click the forecast button")

# Full forecast display (below map)
if get_weather_btn:
    st.write("---")
    st.subheader("📅 7-Day Forecast")
    
    try:
        temp_unit_param = "celsius" if temp_unit == "Celsius (°C)" else "fahrenheit"
        temp_symbol = "°C" if temp_unit == "Celsius (°C)" else "°F"
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": st.session_state.latitude,
            "longitude": st.session_state.longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max",
            "temperature_unit": temp_unit_param,
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        weather_data = response.json()
        
        if 'daily' in weather_data:
            daily = weather_data['daily']
            dates = pd.to_datetime(daily['time'])
            temp_max = daily['temperature_2m_max']
            temp_min = daily['temperature_2m_min']
            precipitation = daily['precipitation_sum']
            weather_codes = daily['weathercode']
            wind_speed = daily['windspeed_10m_max']
            
            def get_weather_icon(code):
                icons = {
                    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
                    45: "🌫️", 48: "🌫️", 51: "🌦️", 53: "🌦️", 55: "🌧️",
                    61: "🌧️", 63: "🌧️", 65: "🌧️",
                    71: "🌨️", 73: "🌨️", 75: "❄️",
                    80: "🌦️", 81: "🌧️", 82: "⛈️",
                    95: "⛈️", 96: "⛈️", 99: "⛈️"
                }
                return icons.get(code, "🌡️")
            
            # Daily cards
            cols = st.columns(7)
            for i, col in enumerate(cols):
                with col:
                    day_name = dates[i].strftime("%a")
                    date_str = dates[i].strftime("%m/%d")
                    
                    st.markdown(f"**{day_name}**")
                    st.caption(date_str)
                    st.markdown(f"## {get_weather_icon(weather_codes[i])}")
                    st.metric("High", f"{temp_max[i]:.0f}{temp_symbol}")
                    st.metric("Low", f"{temp_min[i]:.0f}{temp_symbol}")
                    st.caption(f"💧 {precipitation[i]:.1f}mm")
            
            # Temperature chart
            st.write("---")
            st.subheader("🌡️ Temperature Trend")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=temp_max, name='High', mode='lines+markers', line=dict(color='red', width=3)))
            fig.add_trace(go.Scatter(x=dates, y=temp_min, name='Low', mode='lines+markers', line=dict(color='blue', width=3)))
            fig.update_layout(xaxis_title="Date", yaxis_title=f"Temperature ({temp_symbol})", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error fetching forecast: {str(e)}")

st.caption("Data provided by Open-Meteo API")
