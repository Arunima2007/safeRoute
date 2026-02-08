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

# Modern Custom CSS with beautiful design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Space+Mono:wght@400;700&display=swap');
    
    * {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .main-header {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 2rem 0 0.5rem 0;
        letter-spacing: -2px;
    }
    
    .subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    .content-container {
        background: white;
        border-radius: 24px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 1400px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    .route-card {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .route-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .recommended-route {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 3px solid #10b981;
        box-shadow: 0 8px 16px rgba(16, 185, 129, 0.2);
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .score-high { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }
    .score-medium { 
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    .score-low { 
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }
    
    .transport-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 6px solid;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .transport-card:hover {
        transform: translateX(8px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    .transport-metro {
        border-left-color: #8b5cf6;
        background: linear-gradient(135deg, #faf5ff 0%, #ffffff 100%);
    }
    
    .transport-bus {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%);
    }
    
    .transport-car {
        border-left-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
    }
    
    .transport-walk {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%);
    }
    
    .transport-bike {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
    }
    
    .station-list {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .station-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: white;
        border-radius: 8px;
        border-left: 4px solid #8b5cf6;
        font-family: 'Space Mono', monospace;
        font-size: 0.9rem;
    }
    
    .line-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.75rem;
        color: white;
        margin: 0.25rem;
    }
    
    .line-red { background: #dc2626; }
    .line-yellow { background: #f59e0b; }
    .line-blue { background: #3b82f6; }
    .line-green { background: #10b981; }
    .line-violet { background: #8b5cf6; }
    .line-pink { background: #ec4899; }
    .line-magenta { background: #d946ef; }
    .line-grey { background: #6b7280; }
    
    .stat-box {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        border-color: #667eea;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
    }
    
    .nav-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 700;
        text-decoration: none;
        display: inline-block;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        border: none;
        cursor: pointer;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .priority-badge {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    .change-indicator {
        background: #fee2e2;
        color: #dc2626;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.5rem 0;
        display: inline-block;
    }
    
    /* Streamlit specific overrides */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Delhi Metro Lines Configuration
DELHI_METRO_LINES = {
    "Red Line": {"color": "#dc2626", "stations": ["Rithala", "Rohini West", "Rohini East", "Pitampura", "Kohat Enclave", "Netaji Subhash Place", "Keshav Puram", "Kanhaiya Nagar", "Inderlok", "Shastri Nagar", "Pratap Nagar", "Pulbangash", "Tis Hazari", "Kashmere Gate", "Chandni Chowk", "Chawri Bazar", "New Delhi", "Rajiv Chowk", "Patel Chowk", "Central Secretariat", "Udyog Bhawan", "Lok Kalyan Marg", "Jor Bagh", "INA", "AIIMS", "Green Park", "Hauz Khas", "Malviya Nagar", "Saket", "Qutab Minar", "Chhattarpur", "Sultanpur", "Ghitorni", "Arjan Garh", "Guru Dronacharya", "Sikanderpur", "MG Road", "IFFCO Chowk", "Huda City Centre"]},
    "Yellow Line": {"color": "#f59e0b", "stations": ["Samaypur Badli", "Rohini Sector 18-19", "Haiderpur Badli Mor", "Jahangirpuri", "Adarsh Nagar", "Azadpur", "Model Town", "GTB Nagar", "Vishwa Vidyalaya", "Vidhan Sabha", "Civil Lines", "Kashmere Gate", "Chandni Chowk", "Chawri Bazar", "New Delhi", "Rajiv Chowk", "Patel Chowk", "Central Secretariat", "Udyog Bhawan", "Race Course", "Jor Bagh", "INA", "AIIMS", "Green Park", "Hauz Khas", "Malviya Nagar", "Saket", "Qutab Minar", "Chhattarpur", "Sultanpur", "Ghitorni", "Arjan Garh", "Guru Dronacharya", "Sikanderpur", "MG Road", "IFFCO Chowk", "Huda City Centre"]},
    "Blue Line": {"color": "#3b82f6", "stations": ["Dwarka Sector 21", "Dwarka Sector 8", "Dwarka Sector 9", "Dwarka Sector 10", "Dwarka Sector 11", "Dwarka Sector 12", "Dwarka Sector 13", "Dwarka Sector 14", "Dwarka", "Dwarka Mor", "Nawada", "Uttam Nagar West", "Uttam Nagar East", "Janakpuri West", "Janakpuri East", "Tilak Nagar", "Subhash Nagar", "Tagore Garden", "Rajouri Garden", "Ramesh Nagar", "Moti Nagar", "Kirti Nagar", "Shadipur", "Patel Nagar", "Rajendra Place", "Karol Bagh", "Jhandewalan", "RK Ashram Marg", "Rajiv Chowk", "Barakhamba Road", "Mandi House", "Supreme Court", "Indraprastha", "Yamuna Bank", "Laxmi Nagar", "Nirman Vihar", "Preet Vihar", "Karkarduma", "Anand Vihar", "Kaushambi", "Vaishali", "Noida City Centre", "Noida Sector 62", "Noida Electronic City"]},
    "Green Line": {"color": "#10b981", "stations": ["Inderlok", "Ashok Park Main", "Punjabi Bagh West", "Kirti Nagar"]},
    "Violet Line": {"color": "#8b5cf6", "stations": ["Kashmere Gate", "Lal Quila", "Jama Masjid", "Delhi Gate", "ITO", "Mandi House", "Janpath", "Central Secretariat", "Khan Market", "JLN Stadium", "Jangpura", "Lajpat Nagar", "Moolchand", "Kailash Colony", "Nehru Place", "Kalkaji Mandir", "Govind Puri", "Harkesh Nagar Okhla", "Jasola Apollo", "Sarita Vihar", "Mohan Estate", "Tughlakabad", "Badarpur Border", "Sarai", "NHPC Chowk", "Mewala Maharajpur", "Sector 28", "Badkal Mor", "Old Faridabad", "Neelam Chowk Ajronda", "Bata Chowk", "Escorts Mujesar", "Sant Surdas", "Raja Nahar Singh"]},
    "Pink Line": {"color": "#ec4899", "stations": ["Majlis Park", "Azadpur", "Shalimar Bagh", "Netaji Subhash Place", "Shakurpur", "Punjabi Bagh West", "ESI Hospital", "Rajouri Garden", "Mayapuri", "Naraina Vihar", "Delhi Cantt", "Durgabai Deshmukh South Campus", "Sir Vishweshwaraiah Moti Bagh", "Bhikaji Cama Place", "Sarojini Nagar", "INA", "South Extension", "Lajpat Nagar", "Vinobapuri", "Ashram", "Hazrat Nizamuddin", "Mayur Vihar Phase 1", "Mayur Vihar Pocket 1", "Trilokpuri", "East Vinod Nagar", "Mandawali", "IP Extension", "Anand Vihar", "Karkarduma", "Karkarduma Court", "Krishna Nagar", "East Azad Nagar", "Welcome", "Jaffrabad", "Maujpur", "Gokulpuri", "Johri Enclave", "Shiv Vihar"]},
    "Magenta Line": {"color": "#d946ef", "stations": ["Janakpuri West", "Dabri Mor", "Dashrath Puri", "Palam", "Sadar Bazar Cantonment", "Terminal 1 IGI Airport", "Shankar Vihar", "Vasant Vihar", "Munirka", "RK Puram", "IIT Delhi", "Hauz Khas", "Panchsheel Park", "Chirag Delhi", "Greater Kailash", "Nehru Enclave", "Kalkaji Mandir", "Okhla NSIC", "Sukhdev Vihar", "Jamia Millia Islamia", "Okhla Vihar", "Jasola Vihar Shaheen Bagh", "Kalindi Kunj", "Okhla Bird Sanctuary", "Botanical Garden"]},
    "Grey Line": {"color": "#6b7280", "stations": ["Dwarka", "Nangli", "Najafgarh"]},
}

# Helper function to find nearest metro stations
def find_nearest_metro_stations(location_name, num_stations=3):
    """
    Simulated function to find nearest metro stations
    In production, this would use actual geolocation data
    """
    # Simulated metro stations near common locations
    station_mapping = {
        "Connaught Place": [
            {"name": "Rajiv Chowk", "line": ["Blue Line", "Yellow Line"], "distance": "0.5 km", "walk_time": "6 mins"},
            {"name": "Barakhamba Road", "line": ["Blue Line"], "distance": "0.8 km", "walk_time": "10 mins"},
            {"name": "Patel Chowk", "line": ["Yellow Line"], "distance": "1.2 km", "walk_time": "15 mins"}
        ],
        "Saket": [
            {"name": "Saket", "line": ["Yellow Line"], "distance": "0.3 km", "walk_time": "4 mins"},
            {"name": "Malviya Nagar", "line": ["Yellow Line"], "distance": "2.1 km", "walk_time": "25 mins"},
            {"name": "Qutab Minar", "line": ["Yellow Line"], "distance": "3.5 km", "walk_time": "40 mins"}
        ],
        "India Gate": [
            {"name": "Central Secretariat", "line": ["Yellow Line", "Violet Line"], "distance": "1.0 km", "walk_time": "12 mins"},
            {"name": "Udyog Bhawan", "line": ["Yellow Line"], "distance": "1.5 km", "walk_time": "18 mins"},
            {"name": "Khan Market", "line": ["Violet Line"], "distance": "1.8 km", "walk_time": "22 mins"}
        ],
        "Dwarka": [
            {"name": "Dwarka Sector 21", "line": ["Blue Line"], "distance": "0.5 km", "walk_time": "6 mins"},
            {"name": "Dwarka", "line": ["Blue Line", "Grey Line"], "distance": "1.2 km", "walk_time": "15 mins"},
            {"name": "Dwarka Sector 14", "line": ["Blue Line"], "distance": "2.0 km", "walk_time": "24 mins"}
        ],
        "Noida City Centre": [
            {"name": "Noida City Centre", "line": ["Blue Line"], "distance": "0.2 km", "walk_time": "2 mins"},
            {"name": "Noida Sector 62", "line": ["Blue Line"], "distance": "2.5 km", "walk_time": "30 mins"},
            {"name": "Noida Electronic City", "line": ["Blue Line"], "distance": "4.0 km", "walk_time": "48 mins"}
        ],
        "Rohini": [
            {"name": "Rohini West", "line": ["Red Line"], "distance": "0.8 km", "walk_time": "10 mins"},
            {"name": "Rohini East", "line": ["Red Line"], "distance": "1.5 km", "walk_time": "18 mins"},
            {"name": "Pitampura", "line": ["Red Line"], "distance": "3.0 km", "walk_time": "36 mins"}
        ],
        "Nehru Place": [
            {"name": "Nehru Place", "line": ["Violet Line"], "distance": "0.3 km", "walk_time": "4 mins"},
            {"name": "Kalkaji Mandir", "line": ["Violet Line", "Magenta Line"], "distance": "2.0 km", "walk_time": "24 mins"},
            {"name": "Govind Puri", "line": ["Violet Line"], "distance": "2.5 km", "walk_time": "30 mins"}
        ]
    }
    
    # Return stations or default if location not in mapping
    for key in station_mapping:
        if key.lower() in location_name.lower():
            return station_mapping[key][:num_stations]
    
    # Default stations
    return [
        {"name": "Rajiv Chowk", "line": ["Blue Line", "Yellow Line"], "distance": "~2 km", "walk_time": "~25 mins"},
        {"name": "Central Secretariat", "line": ["Yellow Line", "Violet Line"], "distance": "~3 km", "walk_time": "~35 mins"}
    ]

def generate_metro_route(origin_stations, dest_stations):
    """
    Generate a metro route with line changes
    """
    # Simplified route generation
    origin = origin_stations[0]
    dest = dest_stations[0]
    
    # Find common lines
    common_lines = set(origin['line']) & set(dest['line'])
    
    if common_lines:
        # Direct route on same line
        line = list(common_lines)[0]
        return {
            "type": "direct",
            "line": line,
            "route": [
                {"station": origin['name'], "action": "board", "line": line},
                {"station": dest['name'], "action": "alight", "line": line}
            ],
            "total_time": "~25 mins",
            "fare": "₹30-50"
        }
    else:
        # Route with interchange
        interchange_stations = ["Rajiv Chowk", "Kashmere Gate", "Central Secretariat", "Hauz Khas", "Kalkaji Mandir"]
        interchange = interchange_stations[0]
        
        return {
            "type": "interchange",
            "route": [
                {"station": origin['name'], "action": "board", "line": origin['line'][0]},
                {"station": interchange, "action": "change", "from_line": origin['line'][0], "to_line": dest['line'][0]},
                {"station": dest['name'], "action": "alight", "line": dest['line'][0]}
            ],
            "total_time": "~35-45 mins",
            "fare": "₹40-60"
        }

def generate_bus_routes(origin, destination):
    """
    Generate bus route suggestions
    """
    # Simulated bus routes
    bus_routes = [
        {
            "number": "764",
            "from": "Connaught Place",
            "to": "Saket",
            "via": ["INA", "AIIMS", "Green Park"],
            "frequency": "Every 15 mins",
            "fare": "₹15-25",
            "time": "~40 mins"
        },
        {
            "number": "522",
            "from": "Connaught Place", 
            "to": "Saket",
            "via": ["Mandi House", "Nehru Place", "Kalkaji"],
            "frequency": "Every 20 mins",
            "fare": "₹15-25",
            "time": "~50 mins"
        }
    ]
    return bus_routes

def get_score_class(score):
    """Return CSS class based on score"""
    if score >= 70:
        return "score-high"
    elif score >= 40:
        return "score-medium"
    else:
        return "score-low"

# Header
st.markdown('<div class="main-header">🛡️ SafeRoute Delhi</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Smart Route Navigation for Safety, Speed & Sustainability</div>', unsafe_allow_html=True)

# Main content container
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Route Settings")
    
    # Popular locations
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
    
    # Origin selection
    st.subheader("📍 Starting Point")
    origin_preset = st.selectbox("Quick Select Origin", list(popular_locations.keys()), index=0, key="origin_select")
    
    if origin_preset == "Custom":
        origin = st.text_input("Enter origin address", "Connaught Place, Delhi")
    else:
        origin = popular_locations[origin_preset]
        st.text(f"📌 {origin}")
    
    # Destination selection
    st.subheader("🎯 Destination")
    dest_preset = st.selectbox("Quick Select Destination", list(popular_locations.keys()), index=2, key="dest_select")
    
    if dest_preset == "Custom":
        destination = st.text_input("Enter destination address", "Saket, Delhi")
    else:
        destination = popular_locations[dest_preset]
        st.text(f"📌 {destination}")
    
    # Preference mode
    st.subheader("🎯 Travel Priority")
    preference_icons = {
        "safety": "🛡️ Safety First",
        "fastest": "⚡ Fastest Route",
        "eco": "🌱 Eco-Friendly",
        "balanced": "⚖️ Balanced"
    }
    
    preference = st.radio(
        "Choose your priority:",
        list(preference_icons.keys()),
        format_func=lambda x: preference_icons[x],
        key="preference_radio"
    )
    
    # API endpoint
    api_url = st.text_input("API Endpoint", "http://127.0.0.1:5000/api/compare-routes")
    
    # Find Routes button
    if st.button("🔍 Find Best Routes", type="primary", use_container_width=True):
        st.session_state.show_results = True
        st.session_state.api_result = None

# Main content area
if st.session_state.show_results:
    if not origin or not destination:
        st.error("⚠️ Please enter both origin and destination")
    else:
        if st.session_state.api_result is None:
            with st.spinner("🔄 Analyzing routes with AI..."):
                try:
                    response = requests.post(
                        api_url,
                        json={
                            "origin": origin,
                            "destination": destination,
                            "preference": preference
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        st.session_state.api_result = response.json()
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        st.json(response.json())
                        st.stop()
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the Flask server is running on http://127.0.0.1:5000")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.stop()
        
        result = st.session_state.api_result
        
        # Success message
        st.success(f"✅ Found {result['total_routes']} route options!")
        
        # Get route info
        recommended = result['recommended']
        distance_text = recommended.get('distance_text', '0 km')
        duration_text = recommended.get('duration_text', '0 mins')
        
        try:
            distance_km = float(distance_text.split()[0])
        except:
            distance_km = 10
        
        try:
            duration_mins = float(duration_text.split()[0])
        except:
            duration_mins = 30
        
        # Transport Options Section
        st.markdown("## 🚆 Transport Options & Routes")
        st.markdown(f"**Journey:** {origin} → {destination} | **Distance:** {distance_text} | **Est. Time:** {duration_text}")
        st.markdown("---")
        
        # Metro Option
        origin_metro_stations = find_nearest_metro_stations(origin)
        dest_metro_stations = find_nearest_metro_stations(destination)
        
        if distance_km >= 3 and distance_km <= 30:
            st.markdown('<div class="transport-card transport-metro">', unsafe_allow_html=True)
            st.markdown("### 🚇 Metro Route (Recommended)")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Nearest Metro Stations from Origin:**")
                for station in origin_metro_stations[:2]:
                    line_badges = "".join([f'<span class="line-badge line-{line.split()[0].lower()}">{line}</span>' 
                                          for line in station['line']])
                    st.markdown(f"""
                    <div class="station-item">
                        📍 <strong>{station['name']}</strong> {line_badges}
                        <br><small>🚶 {station['distance']} • {station['walk_time']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("**Nearest Metro Stations to Destination:**")
                for station in dest_metro_stations[:2]:
                    line_badges = "".join([f'<span class="line-badge line-{line.split()[0].lower()}">{line}</span>' 
                                          for line in station['line']])
                    st.markdown(f"""
                    <div class="station-item">
                        📍 <strong>{station['name']}</strong> {line_badges}
                        <br><small>🚶 {station['distance']} • {station['walk_time']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Quick Stats**")
                st.metric("Metro Time", "~25-35 mins")
                st.metric("Fare", "₹30-60")
                st.metric("Frequency", "3-5 mins")
            
            # Generate metro route
            metro_route = generate_metro_route(origin_metro_stations, dest_metro_stations)
            
            st.markdown("**Suggested Metro Route:**")
            st.markdown('<div class="station-list">', unsafe_allow_html=True)
            
            for idx, step in enumerate(metro_route['route']):
                if step['action'] == 'board':
                    line_color = DELHI_METRO_LINES.get(step['line'], {}).get('color', '#6b7280')
                    st.markdown(f"""
                    <div style="margin: 0.5rem 0; padding: 0.75rem; background: white; border-radius: 8px; border-left: 4px solid {line_color};">
                        <strong>🚇 Board at: {step['station']}</strong><br>
                        <span class="line-badge" style="background: {line_color};">{step['line']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif step['action'] == 'change':
                    from_color = DELHI_METRO_LINES.get(step['from_line'], {}).get('color', '#6b7280')
                    to_color = DELHI_METRO_LINES.get(step['to_line'], {}).get('color', '#6b7280')
                    st.markdown(f"""
                    <div class="change-indicator">
                        🔄 <strong>Change at: {step['station']}</strong><br>
                        <span class="line-badge" style="background: {from_color};">{step['from_line']}</span>
                        → <span class="line-badge" style="background: {to_color};">{step['to_line']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif step['action'] == 'alight':
                    line_color = DELHI_METRO_LINES.get(step['line'], {}).get('color', '#6b7280')
                    st.markdown(f"""
                    <div style="margin: 0.5rem 0; padding: 0.75rem; background: white; border-radius: 8px; border-left: 4px solid {line_color};">
                        <strong>🚪 Alight at: {step['station']}</strong><br>
                        <span class="line-badge" style="background: {line_color};">{step['line']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown(f"**Total Journey Time:** {metro_route['total_time']} | **Fare:** {metro_route['fare']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Bus Option
        if distance_km >= 2:
            bus_routes = generate_bus_routes(origin, destination)
            
            st.markdown('<div class="transport-card transport-bus">', unsafe_allow_html=True)
            st.markdown("### 🚌 Bus Routes")
            
            for bus in bus_routes:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Bus No. {bus['number']}**")
                    via_stops = " → ".join(bus['via'])
                    st.markdown(f"📍 {bus['from']} → {via_stops} → {bus['to']}")
                
                with col2:
                    st.markdown(f"**{bus['time']}**")
                    st.markdown(f"{bus['fare']}")
                
                st.caption(f"⏱️ Frequency: {bus['frequency']}")
                st.markdown("---")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Car/Taxi Option
        if distance_km >= 5:
            st.markdown('<div class="transport-card transport-car">', unsafe_allow_html=True)
            st.markdown("### 🚗 Car / Taxi")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Ola/Uber", f"₹{int(distance_km * 15)}-{int(distance_km * 20)}")
            
            with col2:
                st.metric("Auto Rickshaw", f"₹{int(distance_km * 12)}-{int(distance_km * 15)}")
            
            with col3:
                st.metric("Time", duration_text)
            
            # Google Maps navigation
            google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"
            
            st.markdown(f"""
            <a href="{google_maps_url}" target="_blank">
                <button class="nav-button">
                    🗺️ Navigate with Google Maps
                </button>
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Walk/Bike for short distances
        if distance_km <= 5:
            if distance_km <= 2:
                st.markdown('<div class="transport-card transport-walk">', unsafe_allow_html=True)
                st.markdown("### 🚶 Walking")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Distance", distance_text)
                with col2:
                    st.metric("Time", f"~{int(distance_km * 15)} mins")
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown('<div class="transport-card transport-bike">', unsafe_allow_html=True)
            st.markdown("### 🚴 Bicycle / E-Scooter")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Distance", distance_text)
            with col2:
                st.metric("Time", f"~{int(distance_km * 6)} mins")
            with col3:
                st.metric("Cost", "₹10-30")
            st.caption("🌱 Eco-friendly | Available on Yulu, Bounce, Lime apps")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Summary metrics
        if 'summary' in result:
            st.markdown("## 📊 Route Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">🛡️ Safety Range</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{result["summary"]["score_range"]["safety"]}</div>', unsafe_allow_html=True)
                st.caption(f"Safest: {result['summary']['safest_route']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">⚡ Speed Range</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{result["summary"]["score_range"]["speed"]}</div>', unsafe_allow_html=True)
                st.caption(f"Fastest: {result['summary']['fastest_route']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">🌱 Eco Range</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{result["summary"]["score_range"]["eco"]}</div>', unsafe_allow_html=True)
                st.caption(f"Greenest: {result['summary']['greenest_route']}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📋 Route Details", "📊 Analytics"])
        
        with tab1:
            st.markdown("### 🗺️ Interactive Route Map")
            
            routes = result['routes']
            
            # Get center point
            if routes and 'polyline' in routes[0]:
                first_route_coords = polyline.decode(routes[0]['polyline'])
                center_lat = sum(coord[0] for coord in first_route_coords) / len(first_route_coords)
                center_lng = sum(coord[1] for coord in first_route_coords) / len(first_route_coords)
            else:
                center_lat, center_lng = 28.6139, 77.2090
            
            # Create map
            m = folium.Map(
                location=[center_lat, center_lng],
                zoom_start=12,
                tiles='OpenStreetMap'
            )
            
            colors = ['green', 'blue', 'red', 'orange', 'purple']
            
            for idx, route in enumerate(routes):
                if 'polyline' in route:
                    coords = polyline.decode(route['polyline'])
                    
                    color = colors[min(idx, len(colors)-1)]
                    if route.get('is_recommended', False):
                        color = 'green'
                        weight = 6
                    else:
                        weight = 4
                    
                    folium.PolyLine(
                        coords,
                        color=color,
                        weight=weight,
                        opacity=0.8,
                        popup=f"{route['summary']}<br>Safety: {route['safety_score']:.0f}<br>Speed: {route['speed_score']:.0f}",
                    ).add_to(m)
                    
                    if idx == 0:
                        folium.Marker(
                            coords[0],
                            popup="Start",
                            icon=folium.Icon(color='green', icon='play')
                        ).add_to(m)
                        
                        folium.Marker(
                            coords[-1],
                            popup="Destination",
                            icon=folium.Icon(color='red', icon='stop')
                        ).add_to(m)
            
            st_folium(m, width=None, height=500)
        
        with tab2:
            st.markdown("### 📋 Detailed Route Comparison")
            
            routes = result['routes']
            
            for idx, route in enumerate(routes):
                is_recommended = route.get('is_recommended', False)
                
                if is_recommended:
                    st.markdown('<div class="route-card recommended-route">', unsafe_allow_html=True)
                    st.markdown(f"### ⭐ {route['summary']} (RECOMMENDED)")
                else:
                    st.markdown('<div class="route-card">', unsafe_allow_html=True)
                    st.markdown(f"### {route['summary']}")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Rank:** #{route['rank']} | **Overall Score:** {route['composite_score']:.0f}/100")
                
                with col2:
                    st.markdown(f"📏 **{route['distance_text']}**")
                
                with col3:
                    st.markdown(f"⏱️ **{route['duration_text']}**")
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    score_class = get_score_class(route['safety_score'])
                    st.markdown(f"""
                    <div style="text-align: center">
                        <div class="metric-label">🛡️ Safety</div>
                        <span class="score-badge {score_class}">
                            {route['safety_score']:.0f}/100
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    score_class = get_score_class(route['speed_score'])
                    st.markdown(f"""
                    <div style="text-align: center">
                        <div class="metric-label">⚡ Speed</div>
                        <span class="score-badge {score_class}">
                            {route['speed_score']:.0f}/100
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    score_class = get_score_class(route['eco_score'])
                    st.markdown(f"""
                    <div style="text-align: center">
                        <div class="metric-label">🌱 Eco</div>
                        <span class="score-badge {score_class}">
                            {route['eco_score']:.0f}/100
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                if 'risk_name' in route:
                    risk_emoji = {'Safe': '🟢', 'Moderate': '🟡', 'Risky': '🔴'}
                    st.markdown(f"**Risk Level:** {risk_emoji.get(route['risk_name'], '⚪')} {route['risk_name']}")
                
                # Navigation button
                if 'polyline' in route:
                    route_coords = polyline.decode(route['polyline'])
                    waypoints_str = ""
                    if len(route_coords) > 2:
                        sample_points = route_coords[len(route_coords)//3:len(route_coords)*2//3:len(route_coords)//6]
                        waypoints = "|".join([f"{lat},{lng}" for lat, lng in sample_points[:3]])
                        if waypoints:
                            waypoints_str = f"&waypoints={waypoints}"
                    
                    route_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}{waypoints_str}&travelmode=driving"
                    
                    st.markdown(f"""
                    <a href="{route_maps_url}" target="_blank">
                        <button class="nav-button">
                            🗺️ Navigate This Route
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        
        with tab3:
            st.markdown("### 📊 Route Analytics")
            
            routes = result['routes']
            
            # Bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Safety',
                x=[r['summary'] for r in routes],
                y=[r['safety_score'] for r in routes],
                marker_color='#10b981'
            ))
            
            fig.add_trace(go.Bar(
                name='Speed',
                x=[r['summary'] for r in routes],
                y=[r['speed_score'] for r in routes],
                marker_color='#3b82f6'
            ))
            
            fig.add_trace(go.Bar(
                name='Eco',
                x=[r['summary'] for r in routes],
                y=[r['eco_score'] for r in routes],
                marker_color='#8b5cf6'
            ))
            
            fig.update_layout(
                title='Route Score Comparison',
                xaxis_title='Route',
                yaxis_title='Score (0-100)',
                barmode='group',
                height=500,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Radar chart
            st.markdown("### 🎯 Recommended Route Profile")
            
            recommended = result['recommended']
            
            fig_radar = go.Figure()
            
            categories = ['Safety', 'Speed', 'Eco', 'Overall']
            values = [
                recommended['safety_score'],
                recommended['speed_score'],
                recommended['eco_score'],
                recommended['composite_score']
            ]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name=recommended['summary'],
                line_color='#667eea'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Metrics table
            st.markdown("### 📈 Detailed Metrics")
            
            import pandas as pd
            
            metrics_data = []
            for route in routes:
                metrics_data.append({
                    'Route': route['summary'],
                    'Rank': route['rank'],
                    'Distance': route['distance_text'],
                    'Duration': route['duration_text'],
                    'Safety': f"{route['safety_score']:.0f}",
                    'Speed': f"{route['speed_score']:.0f}",
                    'Eco': f"{route['eco_score']:.0f}",
                    'Overall': f"{route['composite_score']:.0f}",
                    'Risk': route.get('risk_name', 'N/A')
                })
            
            df = pd.DataFrame(metrics_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

else:
    # Welcome screen
    st.info("👆 Configure your route settings in the sidebar and click 'Find Best Routes' to get started!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Safety First
        Routes analyzed for:
        - Crime statistics
        - Street lighting
        - Traffic conditions
        - Historical safety data
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌱 Eco-Friendly
        Environmental metrics:
        - Air quality (PM2.5)
        - Carbon emissions
        - Traffic congestion
        - Green route options
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🤖 AI-Powered
        Machine learning features:
        - Real-time risk prediction
        - Multi-factor scoring
        - Explainable AI insights
        - Route optimization
        """)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255, 255, 255, 0.8); padding: 2rem;">
    <p style="font-weight: 600; font-size: 1.1rem;">🏆 Built for LeanIn Hackathon | Powered by AI & Real-time Data</p>
    <p style="font-size: 0.9rem;">📊 Using: Random Forest ML | Google Maps API | OpenAQ | Delhi Police Data</p>
</div>
""", unsafe_allow_html=True)
