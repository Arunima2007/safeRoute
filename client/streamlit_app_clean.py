# streamlit_app.py

import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import polyline
from datetime import datetime

# Initialize session state
if "show_results" not in st.session_state:
    st.session_state.show_results = False

if "api_result" not in st.session_state:
    st.session_state.api_result = None

# Page config
st.set_page_config(
    page_title="SafeRoute Delhi",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, Modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main background */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 0;
        text-align: center;
    }
    
    .app-subtitle {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    }
    
    .card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transition: box-shadow 0.3s ease;
    }
    
    .recommended-card {
        border: 2px solid #10b981;
        background: linear-gradient(to right, #f0fdf4, #ffffff);
    }
    
    /* Transport cards */
    .transport-option {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    .metro-card { border-left-color: #8b5cf6; }
    .bus-card { border-left-color: #f59e0b; }
    .car-card { border-left-color: #3b82f6; }
    .walk-card { border-left-color: #10b981; }
    .bike-card { border-left-color: #ef4444; }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Metro station styling */
    .metro-station {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .metro-route-step {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        border-left: 3px solid;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .line-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
        margin-right: 0.25rem;
    }
    
    /* Score badges */
    .score-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.25rem;
        color: white;
    }
    
    .score-high { background: #10b981; }
    .score-medium { background: #f59e0b; }
    .score-low { background: #ef4444; }
    
    /* Button styling */
    .nav-btn {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s;
        border: none;
        cursor: pointer;
        text-align: center;
    }
    
    .nav-btn:hover {
        background: #5568d3;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-item {
        background: white;
        padding: 1.25rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1f2937;
    }
    
    /* Metro line colors */
    .line-red { background-color: #dc2626; }
    .line-yellow { background-color: #f59e0b; }
    .line-blue { background-color: #3b82f6; }
    .line-green { background-color: #10b981; }
    .line-violet { background-color: #8b5cf6; }
    .line-pink { background-color: #ec4899; }
    .line-magenta { background-color: #d946ef; }
    .line-grey { background-color: #6b7280; }
    
    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .badge-recommended {
        background: #dcfce7;
        color: #16a34a;
    }
    
    .badge-warning {
        background: #fef3c7;
        color: #d97706;
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background: #e5e7eb;
        margin: 2rem 0;
    }
    
    /* Journey info */
    .journey-info {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.25rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #3b82f6;
    }
    
    .journey-detail {
        display: inline-block;
        margin-right: 2rem;
        font-size: 0.95rem;
    }
    
    .journey-detail strong {
        color: #1f2937;
        font-weight: 600;
    }
    
    /* Change indicator */
    .change-point {
        background: #fef3c7;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border-left: 3px solid #f59e0b;
        margin: 0.75rem 0;
        font-weight: 500;
    }
    
    /* Info box */
    .info-box {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Streamlit button override */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Delhi Metro Lines Configuration
DELHI_METRO_LINES = {
    "Red Line": {"color": "#dc2626", "stations": ["Rithala", "Rohini West", "Rohini East", "Pitampura", "Kohat Enclave", "Netaji Subhash Place", "Inderlok", "Kashmere Gate", "Chandni Chowk", "New Delhi", "Rajiv Chowk", "Patel Chowk", "Central Secretariat", "INA", "AIIMS", "Green Park", "Hauz Khas", "Malviya Nagar", "Saket", "Qutab Minar", "Sultanpur", "Ghitorni", "MG Road", "IFFCO Chowk", "Huda City Centre"]},
    "Yellow Line": {"color": "#f59e0b", "stations": ["Samaypur Badli", "Jahangirpuri", "Azadpur", "GTB Nagar", "Vishwa Vidyalaya", "Kashmere Gate", "Rajiv Chowk", "Central Secretariat", "Hauz Khas", "Malviya Nagar", "Saket", "Huda City Centre"]},
    "Blue Line": {"color": "#3b82f6", "stations": ["Dwarka Sector 21", "Dwarka", "Nawada", "Uttam Nagar West", "Janakpuri West", "Tilak Nagar", "Rajouri Garden", "Karol Bagh", "Rajiv Chowk", "Mandi House", "Yamuna Bank", "Vaishali", "Noida City Centre"]},
    "Violet Line": {"color": "#8b5cf6", "stations": ["Kashmere Gate", "ITO", "Mandi House", "Central Secretariat", "Nehru Place", "Kalkaji Mandir", "Govind Puri", "Badarpur Border"]},
    "Pink Line": {"color": "#ec4899", "stations": ["Majlis Park", "Netaji Subhash Place", "Rajouri Garden", "INA", "Lajpat Nagar", "Mayur Vihar Phase 1", "Anand Vihar", "Welcome", "Shiv Vihar"]},
    "Magenta Line": {"color": "#d946ef", "stations": ["Janakpuri West", "Terminal 1 IGI Airport", "Hauz Khas", "Nehru Enclave", "Kalkaji Mandir", "Botanical Garden"]},
}

def find_nearest_metro_stations(location_name):
    """Find nearest metro stations based on location"""
    station_mapping = {
        "Connaught Place": [
            {"name": "Rajiv Chowk", "lines": ["Blue Line", "Yellow Line"], "distance": "0.5 km", "walk_time": "6 min"},
            {"name": "Barakhamba Road", "lines": ["Blue Line"], "distance": "0.8 km", "walk_time": "10 min"},
        ],
        "Saket": [
            {"name": "Saket", "lines": ["Yellow Line"], "distance": "0.3 km", "walk_time": "4 min"},
            {"name": "Malviya Nagar", "lines": ["Yellow Line"], "distance": "2.1 km", "walk_time": "25 min"},
        ],
        "India Gate": [
            {"name": "Central Secretariat", "lines": ["Yellow Line", "Violet Line"], "distance": "1.0 km", "walk_time": "12 min"},
            {"name": "Khan Market", "lines": ["Violet Line"], "distance": "1.8 km", "walk_time": "22 min"},
        ],
        "Dwarka": [
            {"name": "Dwarka Sector 21", "lines": ["Blue Line"], "distance": "0.5 km", "walk_time": "6 min"},
            {"name": "Dwarka", "lines": ["Blue Line"], "distance": "1.2 km", "walk_time": "15 min"},
        ],
        "Noida City Centre": [
            {"name": "Noida City Centre", "lines": ["Blue Line"], "distance": "0.2 km", "walk_time": "2 min"},
        ],
        "Rohini": [
            {"name": "Rohini West", "lines": ["Red Line"], "distance": "0.8 km", "walk_time": "10 min"},
            {"name": "Rohini East", "lines": ["Red Line"], "distance": "1.5 km", "walk_time": "18 min"},
        ],
        "Nehru Place": [
            {"name": "Nehru Place", "lines": ["Violet Line"], "distance": "0.3 km", "walk_time": "4 min"},
            {"name": "Kalkaji Mandir", "lines": ["Violet Line", "Magenta Line"], "distance": "2.0 km", "walk_time": "24 min"},
        ]
    }
    
    for key in station_mapping:
        if key.lower() in location_name.lower():
            return station_mapping[key]
    
    return [{"name": "Rajiv Chowk", "lines": ["Blue Line", "Yellow Line"], "distance": "~2 km", "walk_time": "~25 min"}]

def generate_metro_route(origin_stations, dest_stations):
    """Generate metro route with interchanges"""
    origin = origin_stations[0]
    dest = dest_stations[0]
    
    common_lines = set(origin['lines']) & set(dest['lines'])
    
    if common_lines:
        line = list(common_lines)[0]
        return {
            "type": "direct",
            "steps": [
                {"type": "board", "station": origin['name'], "line": line},
                {"type": "travel", "line": line, "stations": 8},
                {"type": "alight", "station": dest['name'], "line": line}
            ],
            "duration": "~25 min",
            "fare": "₹30-50",
            "changes": 0
        }
    else:
        interchange = "Rajiv Chowk"
        return {
            "type": "interchange",
            "steps": [
                {"type": "board", "station": origin['name'], "line": origin['lines'][0]},
                {"type": "travel", "line": origin['lines'][0], "stations": 5},
                {"type": "change", "station": interchange, "from_line": origin['lines'][0], "to_line": dest['lines'][0]},
                {"type": "travel", "line": dest['lines'][0], "stations": 6},
                {"type": "alight", "station": dest['name'], "line": dest['lines'][0]}
            ],
            "duration": "~35-45 min",
            "fare": "₹40-60",
            "changes": 1
        }

def generate_bus_routes():
    """Generate bus route options"""
    return [
        {
            "number": "764",
            "route": "Connaught Place → INA → AIIMS → Saket",
            "frequency": "Every 15 min",
            "fare": "₹15-25",
            "duration": "~40 min"
        },
        {
            "number": "522",
            "route": "Connaught Place → Nehru Place → Kalkaji → Saket",
            "frequency": "Every 20 min",
            "fare": "₹15-25",
            "duration": "~50 min"
        }
    ]

def get_score_class(score):
    if score >= 70:
        return "score-high"
    elif score >= 40:
        return "score-medium"
    else:
        return "score-low"

# Header
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🛡️ SafeRoute Delhi</h1>
    <p class="app-subtitle">Smart route planning with safety, speed, and sustainability insights</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Route Settings")
    
    popular_locations = {
        "Connaught Place": "Connaught Place, Delhi",
        "India Gate": "India Gate, Delhi",
        "Saket": "Saket, Delhi",
        "Dwarka": "Dwarka, Delhi",
        "Noida City Centre": "Noida City Centre",
        "Rohini": "Rohini, Delhi",
        "Nehru Place": "Nehru Place, Delhi",
        "Custom": "Custom"
    }
    
    st.markdown("**📍 Starting Point**")
    origin_preset = st.selectbox("Select origin", list(popular_locations.keys()), label_visibility="collapsed")
    
    if origin_preset == "Custom":
        origin = st.text_input("Enter address", "Connaught Place, Delhi")
    else:
        origin = popular_locations[origin_preset]
        st.caption(f"📌 {origin}")
    
    st.markdown("**🎯 Destination**")
    dest_preset = st.selectbox("Select destination", list(popular_locations.keys()), index=2, label_visibility="collapsed")
    
    if dest_preset == "Custom":
        destination = st.text_input("Enter address", "Saket, Delhi", key="dest_input")
    else:
        destination = popular_locations[dest_preset]
        st.caption(f"📌 {destination}")
    
    st.markdown("**🎯 Priority**")
    preference = st.radio(
        "Choose priority",
        ["safety", "fastest", "eco", "balanced"],
        format_func=lambda x: {"safety": "🛡️ Safety", "fastest": "⚡ Speed", "eco": "🌱 Eco", "balanced": "⚖️ Balanced"}[x],
        label_visibility="collapsed"
    )
    
    api_url = st.text_input("API Endpoint", "http://127.0.0.1:5000/api/compare-routes")
    
    if st.button("🔍 Find Routes", type="primary", use_container_width=True):
        st.session_state.show_results = True
        st.session_state.api_result = None

# Main Content
if st.session_state.show_results:
    if not origin or not destination:
        st.error("⚠️ Please enter both origin and destination")
    else:
        if st.session_state.api_result is None:
            with st.spinner("Analyzing routes..."):
                try:
                    response = requests.post(
                        api_url,
                        json={"origin": origin, "destination": destination, "preference": preference},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        st.session_state.api_result = response.json()
                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.stop()
                        
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API. Make sure the Flask server is running.")
                    st.stop()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.stop()
        
        result = st.session_state.api_result
        recommended = result['recommended']
        
        # Journey Info
        st.markdown(f"""
        <div class="journey-info">
            <div class="journey-detail"><strong>From:</strong> {origin}</div>
            <div class="journey-detail"><strong>To:</strong> {destination}</div>
            <div class="journey-detail"><strong>Distance:</strong> {recommended.get('distance_text', 'N/A')}</div>
            <div class="journey-detail"><strong>Duration:</strong> {recommended.get('duration_text', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Extract distance
        try:
            distance_km = float(recommended.get('distance_text', '10 km').split()[0])
        except:
            distance_km = 10
        
        # Transport Options
        st.markdown('<div class="section-header">🚆 Transport Options</div>', unsafe_allow_html=True)
        
        # Metro
        if 3 <= distance_km <= 30:
            origin_stations = find_nearest_metro_stations(origin)
            dest_stations = find_nearest_metro_stations(destination)
            metro_route = generate_metro_route(origin_stations, dest_stations)
            
            st.markdown('<div class="card metro-card">', unsafe_allow_html=True)
            st.markdown("#### 🚇 Metro")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Duration", metro_route['duration'])
            col2.metric("Fare", metro_route['fare'])
            col3.metric("Changes", metro_route['changes'])
            
            st.markdown("**Your Route:**")
            
            for step in metro_route['steps']:
                if step['type'] == 'board':
                    line_class = f"line-{step['line'].split()[0].lower()}"
                    st.markdown(f"""
                    <div class="metro-route-step" style="border-left-color: var(--{line_class});">
                        <div style="font-size: 1.5rem;">🚇</div>
                        <div>
                            <strong>Board at {step['station']}</strong><br>
                            <span class="line-tag {line_class}">{step['line']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif step['type'] == 'change':
                    from_class = f"line-{step['from_line'].split()[0].lower()}"
                    to_class = f"line-{step['to_line'].split()[0].lower()}"
                    st.markdown(f"""
                    <div class="change-point">
                        <strong>🔄 Change at {step['station']}</strong><br>
                        <span class="line-tag {from_class}">{step['from_line']}</span> → 
                        <span class="line-tag {to_class}">{step['to_line']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif step['type'] == 'alight':
                    line_class = f"line-{step['line'].split()[0].lower()}"
                    st.markdown(f"""
                    <div class="metro-route-step" style="border-left-color: var(--{line_class});">
                        <div style="font-size: 1.5rem;">🚪</div>
                        <div>
                            <strong>Alight at {step['station']}</strong><br>
                            <span class="line-tag {line_class}">{step['line']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("**Nearest Stations:**")
            st.caption(f"📍 From origin: {', '.join([s['name'] for s in origin_stations[:2]])}")
            st.caption(f"📍 To destination: {', '.join([s['name'] for s in dest_stations[:2]])}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Bus
        if distance_km >= 2:
            bus_routes = generate_bus_routes()
            
            st.markdown('<div class="card bus-card">', unsafe_allow_html=True)
            st.markdown("#### 🚌 Bus")
            
            for bus in bus_routes:
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.markdown(f"**Bus {bus['number']}** • {bus['route']}")
                col2.markdown(f"⏱️ {bus['duration']}")
                col3.markdown(f"💰 {bus['fare']}")
                st.caption(f"Frequency: {bus['frequency']}")
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Car/Taxi
        if distance_km >= 5:
            st.markdown('<div class="card car-card">', unsafe_allow_html=True)
            st.markdown("#### 🚗 Car / Taxi")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Ola/Uber", f"₹{int(distance_km * 15)}-{int(distance_km * 20)}")
            col2.metric("Auto", f"₹{int(distance_km * 12)}-{int(distance_km * 15)}")
            col3.metric("Duration", recommended.get('duration_text', 'N/A'))
            
            google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"
            st.markdown(f'<a href="{google_maps_url}" target="_blank" class="nav-btn">🗺️ Navigate with Google Maps</a>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Walk/Bike
        if distance_km <= 5:
            st.markdown('<div class="card walk-card">', unsafe_allow_html=True)
            
            if distance_km <= 2:
                st.markdown("#### 🚶 Walking")
                col1, col2 = st.columns(2)
                col1.metric("Distance", f"{distance_km:.1f} km")
                col2.metric("Time", f"~{int(distance_km * 15)} min")
            
            st.markdown("#### 🚴 Bike / E-Scooter")
            col1, col2, col3 = st.columns(3)
            col1.metric("Distance", f"{distance_km:.1f} km")
            col2.metric("Time", f"~{int(distance_km * 6)} min")
            col3.metric("Cost", "₹10-30")
            st.caption("🌱 Eco-friendly • Available on Yulu, Bounce")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Route Analysis
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Route Analysis</div>', unsafe_allow_html=True)
        
        # Summary Stats
        if 'summary' in result:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-label">🛡️ Safety Range</div>
                    <div class="stat-value">{result['summary']['score_range']['safety']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-label">⚡ Speed Range</div>
                    <div class="stat-value">{result['summary']['score_range']['speed']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-item">
                    <div class="stat-label">🌱 Eco Range</div>
                    <div class="stat-value">{result['summary']['score_range']['eco']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["🗺️ Map", "📋 Routes", "📊 Analytics"])
        
        with tab1:
            routes = result['routes']
            
            if routes and 'polyline' in routes[0]:
                first_route_coords = polyline.decode(routes[0]['polyline'])
                center_lat = sum(c[0] for c in first_route_coords) / len(first_route_coords)
                center_lng = sum(c[1] for c in first_route_coords) / len(first_route_coords)
            else:
                center_lat, center_lng = 28.6139, 77.2090
            
            m = folium.Map(location=[center_lat, center_lng], zoom_start=12, tiles='OpenStreetMap')
            
            colors = ['green', 'blue', 'red', 'orange', 'purple']
            
            for idx, route in enumerate(routes):
                if 'polyline' in route:
                    coords = polyline.decode(route['polyline'])
                    color = 'green' if route.get('is_recommended') else colors[min(idx, len(colors)-1)]
                    weight = 6 if route.get('is_recommended') else 4
                    
                    folium.PolyLine(coords, color=color, weight=weight, opacity=0.8).add_to(m)
                    
                    if idx == 0:
                        folium.Marker(coords[0], popup="Start", icon=folium.Icon(color='green', icon='play')).add_to(m)
                        folium.Marker(coords[-1], popup="End", icon=folium.Icon(color='red', icon='stop')).add_to(m)
            
            st_folium(m, width=None, height=500)
        
        with tab2:
            routes = result['routes']
            
            for route in routes:
                is_rec = route.get('is_recommended', False)
                
                st.markdown(f'<div class="card {"recommended-card" if is_rec else ""}">', unsafe_allow_html=True)
                
                badge = '<span class="badge badge-recommended">RECOMMENDED</span>' if is_rec else ""
                st.markdown(
                    f"### {route['summary']} {badge}",
                    unsafe_allow_html=True
                )
                
                col1, col2, col3, col4 = st.columns(4)
                col1.markdown(f"**Rank:** #{route['rank']}")
                col2.markdown(f"**Score:** {route['composite_score']:.0f}/100")
                col3.markdown(f"📏 {route['distance_text']}")
                col4.markdown(f"⏱️ {route['duration_text']}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    score_class = get_score_class(route['safety_score'])
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="stat-label">🛡️ Safety</div>
                        <div class="score-badge {score_class}">{route['safety_score']:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    score_class = get_score_class(route['speed_score'])
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="stat-label">⚡ Speed</div>
                        <div class="score-badge {score_class}">{route['speed_score']:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    score_class = get_score_class(route['eco_score'])
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="stat-label">🌱 Eco</div>
                        <div class="score-badge {score_class}">{route['eco_score']:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            routes = result['routes']
            
            # Bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Safety', x=[r['summary'] for r in routes], y=[r['safety_score'] for r in routes], marker_color='#10b981'))
            fig.add_trace(go.Bar(name='Speed', x=[r['summary'] for r in routes], y=[r['speed_score'] for r in routes], marker_color='#3b82f6'))
            fig.add_trace(go.Bar(name='Eco', x=[r['summary'] for r in routes], y=[r['eco_score'] for r in routes], marker_color='#8b5cf6'))
            
            fig.update_layout(
                title='Route Comparison',
                xaxis_title='Route',
                yaxis_title='Score',
                barmode='group',
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Metrics table
            import pandas as pd
            
            df = pd.DataFrame([{
                'Route': r['summary'],
                'Rank': r['rank'],
                'Distance': r['distance_text'],
                'Duration': r['duration_text'],
                'Safety': f"{r['safety_score']:.0f}",
                'Speed': f"{r['speed_score']:.0f}",
                'Eco': f"{r['eco_score']:.0f}",
                'Overall': f"{r['composite_score']:.0f}"
            } for r in routes])
            
            st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.markdown('<div class="info-box">👆 Configure your route in the sidebar and click "Find Routes"</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>🛡️ Safety First</h3>
            <p>Routes analyzed for crime statistics, lighting, and traffic conditions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🌱 Eco-Friendly</h3>
            <p>Air quality, carbon emissions, and green route options</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <h3>🤖 AI-Powered</h3>
            <p>Real-time risk prediction and route optimization</p>
        </div>
        """, unsafe_allow_html=True)
