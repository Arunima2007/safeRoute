# SafeRoute Delhi - Enhanced UI with Calm Authority Design
import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import polyline
from datetime import datetime, timedelta

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"

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

# Color Scheme - "Calm Authority"
COLORS = {
    'deep_slate_blue': '#1E3A5F',      # Primary - Safety & Trust
    'steel_blue': '#4A6FA5',           # Primary - Reliability
    'muted_evergreen': '#2F6F5E',      # Secondary - Eco
    'soft_moss': '#A8C3B5',            # Secondary - Low-stress overlays
    'caution_amber': '#F2B705',        # Alerts - Risk zones
    'off_white': '#F4F6F8',            # Neutrals - Background
    'graphite_grey': '#2A2E35',        # Neutrals - Text
    'dark_bg': '#0B1620',              # Dark mode background
    'dark_primary': '#5C8DCA',         # Dark mode primary route
    'text_light': '#F8EEF5',           # Dark mode text
}

# Custom CSS with Calm Authority color scheme
st.markdown(f"""
<style>
    /* Global Styles */
    .stApp {{
        background-color: {COLORS['off_white']};
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Custom Header */
    .main-header {{
        font-size: 3.5rem;
        font-weight: 800;
        color: {COLORS['deep_slate_blue']};
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 2rem 0 1rem 0;
        letter-spacing: -1px;
    }}
    
    .subtitle {{
        text-align: center;
        color: {COLORS['graphite_grey']};
        font-size: 1.3rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }}
    
    /* Navigation Pills */
    .nav-pills {{
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 2rem 0;
        padding: 0;
    }}
    
    .nav-pill {{
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid {COLORS['steel_blue']};
        background: white;
        color: {COLORS['steel_blue']};
        text-decoration: none;
        display: inline-block;
    }}
    
    .nav-pill:hover {{
        background: {COLORS['steel_blue']};
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
    }}
    
    .nav-pill.active {{
        background: {COLORS['deep_slate_blue']};
        color: white;
        border-color: {COLORS['deep_slate_blue']};
    }}
    
    /* Hero Section */
    .hero-section {{
        background: linear-gradient(135deg, {COLORS['deep_slate_blue']} 0%, {COLORS['steel_blue']} 100%);
        padding: 4rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(30, 58, 95, 0.3);
    }}
    
    .hero-title {{
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
    }}
    
    .hero-subtitle {{
        font-size: 1.4rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }}
    
    /* Feature Cards */
    .feature-card {{
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border-left: 4px solid {COLORS['steel_blue']};
        height: 100%;
    }}
    
    .feature-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }}
    
    .feature-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
    }}
    
    .feature-title {{
        color: {COLORS['deep_slate_blue']};
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }}
    
    .feature-text {{
        color: {COLORS['graphite_grey']};
        line-height: 1.6;
    }}
    
    /* Route Cards */
    .route-card {{
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #E8EEF3;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }}
    
    .route-card:hover {{
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transform: translateY(-3px);
    }}
    
    .recommended {{
        border: 3px solid {COLORS['steel_blue']};
        background: linear-gradient(to right, #f8fbff 0%, #ffffff 100%);
        box-shadow: 0 4px 20px rgba(74, 111, 165, 0.2);
    }}
    
    .recommended-badge {{
        background: {COLORS['deep_slate_blue']};
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
    }}
    
    /* Score Badges */
    .score-badge {{
        display: inline-block;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-weight: 700;
        color: white;
        font-size: 1.1rem;
    }}
    
    .score-high {{ 
        background: {COLORS['muted_evergreen']};
    }}
    .score-medium {{ 
        background: {COLORS['caution_amber']};
        color: {COLORS['graphite_grey']};
    }}
    .score-low {{ 
        background: #E57373;
    }}
    
    /* Transport Badges */
    .transport-section {{
        background: {COLORS['off_white']};
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid {COLORS['muted_evergreen']};
    }}
    
    .transport-badge {{
        display: inline-block;
        padding: 0.7rem 1.3rem;
        border-radius: 50px;
        font-weight: 600;
        margin: 0.4rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }}
    
    .transport-badge:hover {{
        transform: scale(1.05);
    }}
    
    .transport-metro {{ 
        background: {COLORS['deep_slate_blue']};
        color: white;
    }}
    .transport-bus {{ 
        background: {COLORS['caution_amber']};
        color: {COLORS['graphite_grey']};
    }}
    .transport-car {{ 
        background: {COLORS['steel_blue']};
        color: white;
    }}
    .transport-walk {{ 
        background: {COLORS['muted_evergreen']};
        color: white;
    }}
    .transport-bike {{ 
        background: {COLORS['soft_moss']};
        color: {COLORS['graphite_grey']};
    }}
    
    /* Transport Details */
    .transport-details {{
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 0.8rem;
        border: 1px solid #E0E5EA;
    }}
    
    .transport-step {{
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 3px solid {COLORS['steel_blue']};
        padding-left: 1rem;
    }}
    
    /* Buttons */
    .cta-button {{
        background: {COLORS['steel_blue']};
        color: white;
        padding: 1rem 2.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
    }}
    
    .cta-button:hover {{
        background: {COLORS['deep_slate_blue']};
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 58, 95, 0.3);
    }}
    
    .nav-button {{
        background: {COLORS['muted_evergreen']};
        color: white;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .nav-button:hover {{
        background: #256551;
        box-shadow: 0 4px 12px rgba(47, 111, 94, 0.3);
    }}
    
    /* Risk Indicators */
    .risk-safe {{
        color: {COLORS['muted_evergreen']};
        font-weight: 700;
    }}
    
    .risk-moderate {{
        color: {COLORS['caution_amber']};
        font-weight: 700;
    }}
    
    .risk-high {{
        color: #E57373;
        font-weight: 700;
    }}
    
    /* Stats */
    .stat-box {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 2px solid {COLORS['off_white']};
        transition: all 0.3s ease;
    }}
    
    .stat-box:hover {{
        border-color: {COLORS['steel_blue']};
        box-shadow: 0 4px 15px rgba(74, 111, 165, 0.15);
    }}
    
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 800;
        color: {COLORS['deep_slate_blue']};
        margin-bottom: 0.5rem;
    }}
    
    .stat-label {{
        color: {COLORS['graphite_grey']};
        font-size: 1rem;
        font-weight: 500;
    }}
    
    /* Sidebar Styling */
    .css-1d391kg {{
        background-color: white;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid #E8EEF3;
    }}
    
    /* Info boxes */
    .info-box {{
        background: linear-gradient(135deg, {COLORS['steel_blue']}15 0%, {COLORS['muted_evergreen']}15 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid {COLORS['steel_blue']};
        margin: 1rem 0;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin: 0.5rem 0;
    }}
</style>
""", unsafe_allow_html=True)

# Delhi Metro and Bus route simulator (Enhanced)
def get_detailed_transport_recommendations(distance_km, duration_mins, origin, destination):
    """
    Provides detailed transport recommendations with estimated times and routes
    """
    recommendations = []
    
    # Metro recommendation (3-30 km range)
    if 3 <= distance_km <= 30:
        metro_time = int(distance_km * 3)  # Approximate: 3 mins per km
        metro_changes = min(int(distance_km / 8), 2)  # Estimate line changes
        
        recommendations.append({
            'mode': '🚇 Delhi Metro',
            'badge_class': 'transport-metro',
            'priority': 1,
            'estimated_time': f"{metro_time} mins",
            'cost': f"₹{min(10 + (distance_km * 2), 60):.0f}",
            'details': {
                'steps': [
                    f"Board at nearest metro station to {origin.split(',')[0]}",
                    f"Travel on {'Blue' if 'Noida' in destination or 'Dwarka' in origin else 'Yellow' if 'Saket' in destination else 'Red'} Line",
                    f"Change at Rajiv Chowk (if needed)" if metro_changes > 0 else "Direct route available",
                    f"Alight at nearest station to {destination.split(',')[0]}"
                ],
                'frequency': '5-7 mins',
                'advantages': ['Fast', 'Predictable', 'Air-conditioned', 'Eco-friendly'],
                'ideal_for': 'Peak hours and long distances'
            }
        })
    
    # Bus recommendation (2+ km)
    if distance_km >= 2:
        bus_time = int(duration_mins * 1.3)  # Buses typically 30% slower
        
        recommendations.append({
            'mode': '🚌 DTC Bus',
            'badge_class': 'transport-bus',
            'priority': 3,
            'estimated_time': f"{bus_time} mins",
            'cost': f"₹{min(5 + distance_km, 25):.0f}",
            'details': {
                'steps': [
                    f"Board route 534/413 or similar from {origin.split(',')[0]}",
                    "Stay on main route - minimal changes needed",
                    f"Alight near {destination.split(',')[0]}"
                ],
                'frequency': '10-15 mins',
                'advantages': ['Economical', 'Extensive coverage', 'Direct routes'],
                'ideal_for': 'Budget travel and short distances'
            }
        })
    
    # Auto/Cab recommendation (5+ km)
    if distance_km >= 5:
        recommendations.append({
            'mode': '🚗 Cab/Auto',
            'badge_class': 'transport-car',
            'priority': 2,
            'estimated_time': f"{duration_mins} mins",
            'cost': f"₹{int(distance_km * 15)}-{int(distance_km * 20)}",
            'details': {
                'steps': [
                    "Book Uber/Ola or hail auto rickshaw",
                    f"Direct route via {origin.split(',')[0]} to {destination.split(',')[0]}",
                    "Door-to-door convenience"
                ],
                'frequency': 'On-demand',
                'advantages': ['Convenient', 'Door-to-door', 'Flexible timing'],
                'ideal_for': 'Late hours, heavy luggage, comfort priority'
            }
        })
    
    # Bike/E-scooter (1-7 km)
    if 1 <= distance_km <= 7:
        bike_time = int(distance_km * 5)  # ~12 kmph average
        
        recommendations.append({
            'mode': '🚴 Bike/E-Scooter',
            'badge_class': 'transport-bike',
            'priority': 2 if distance_km <= 5 else 3,
            'estimated_time': f"{bike_time} mins",
            'cost': f"₹{int(distance_km * 3)}-{int(distance_km * 5)}",
            'details': {
                'steps': [
                    "Rent from Yulu/Bounce station",
                    f"Ride approximately {distance_km:.1f} km",
                    "Park at designated zone"
                ],
                'frequency': 'On-demand',
                'advantages': ['Eco-friendly', 'Avoid traffic', 'Healthy', 'Cost-effective'],
                'ideal_for': 'Short distances, good weather, avoiding congestion'
            }
        })
    
    # Walking (< 2 km)
    if distance_km <= 2:
        walk_time = int(distance_km * 12)  # ~5 kmph walking speed
        
        recommendations.append({
            'mode': '🚶 Walking',
            'badge_class': 'transport-walk',
            'priority': 1,
            'estimated_time': f"{walk_time} mins",
            'cost': "Free",
            'details': {
                'steps': [
                    f"Walk {distance_km:.1f} km from {origin.split(',')[0]}",
                    "Use pedestrian crossings and footpaths",
                    f"Arrive at {destination.split(',')[0]}"
                ],
                'frequency': 'Anytime',
                'advantages': ['Healthy', 'Zero cost', 'Zero emissions', 'Scenic'],
                'ideal_for': 'Pleasant weather, exercise, short distances'
            }
        })
    
    # Sort by priority
    recommendations.sort(key=lambda x: x['priority'])
    
    return recommendations

# Helper function for score colors
def get_score_class(score):
    if score >= 70:
        return "score-high"
    elif score >= 40:
        return "score-medium"
    else:
        return "score-low"

# Navigation
def show_navigation():
    home_active = "active" if st.session_state.page == "home" else ""
    planner_active = "active" if st.session_state.page == "planner" else ""
    
    st.markdown(f"""
    <div class="nav-pills">
        <a class="nav-pill {home_active}" onclick="return false;" href="#">🏠 Home</a>
        <a class="nav-pill {planner_active}" onclick="return false;" href="#">🗺️ Route Planner</a>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🏠 Home", use_container_width=True, type="secondary" if st.session_state.page != "home" else "primary"):
            st.session_state.page = "home"
            st.rerun()
    
    with col2:
        if st.button("🗺️ Route Planner", use_container_width=True, type="secondary" if st.session_state.page != "planner" else "primary"):
            st.session_state.page = "planner"
            st.rerun()
    
    with col3:
        if st.button("ℹ️ About", use_container_width=True, type="secondary"):
            st.session_state.page = "about"
            st.rerun()

# HOME PAGE
def show_home_page():
    st.markdown('<div class="main-header">🛡️ SafeRoute Delhi</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Navigate Delhi Safely, Smartly & Sustainably</div>', unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">Your AI-Powered Journey Companion</div>
        <div class="hero-subtitle">Intelligent route planning that prioritizes your safety, time, and environmental impact</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">98%</div>
            <div class="stat-label">Safety Rating</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">45k+</div>
            <div class="stat-label">Routes Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Real-time Updates</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">5+</div>
            <div class="stat-label">Transport Modes</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features Grid
    st.markdown("## 🌟 Why Choose SafeRoute?")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">Safety-First Navigation</div>
            <div class="feature-text">
                AI-powered analysis of crime data, street lighting, and real-time safety metrics to recommend the safest routes for your journey.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Smart Route Optimization</div>
            <div class="feature-text">
                Real-time traffic analysis and intelligent routing to get you to your destination faster while avoiding congestion.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌱</div>
            <div class="feature-title">Eco-Conscious Travel</div>
            <div class="feature-text">
                Environmental impact tracking with air quality monitoring and carbon footprint calculation for sustainable choices.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🚇</div>
            <div class="feature-title">Multi-Modal Transport</div>
            <div class="feature-text">
                Comprehensive recommendations for Metro, Bus, Cab, Bike, and Walking with detailed timings and transfer information.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Data-Driven Insights</div>
            <div class="feature-text">
                Powered by machine learning models trained on Delhi Police data, traffic patterns, and environmental metrics.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Personalized Routes</div>
            <div class="feature-text">
                Choose your priority - safety, speed, or sustainability. Get routes tailored to your specific needs and preferences.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0;">
        <h2 style="color: #1E3A5F; margin-bottom: 1.5rem;">Ready to Navigate Safely?</h2>
        <p style="color: #2A2E35; font-size: 1.2rem; margin-bottom: 2rem;">
            Start planning your journey with AI-powered route recommendations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗺️ Plan Your Route", use_container_width=True, type="primary"):
            st.session_state.page = "planner"
            st.rerun()
    
    # How it works
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## 🔍 How SafeRoute Works")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">1️⃣</div>
            <h4 style="color: #1E3A5F;">Enter Journey</h4>
            <p style="color: #2A2E35;">Input your origin and destination</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">2️⃣</div>
            <h4 style="color: #1E3A5F;">Set Priority</h4>
            <p style="color: #2A2E35;">Choose safety, speed, or eco-friendly</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">3️⃣</div>
            <h4 style="color: #1E3A5F;">AI Analysis</h4>
            <p style="color: #2A2E35;">Real-time route evaluation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">4️⃣</div>
            <h4 style="color: #1E3A5F;">Get Routes</h4>
            <p style="color: #2A2E35;">Receive optimal recommendations</p>
        </div>
        """, unsafe_allow_html=True)

# ROUTE PLANNER PAGE
def show_planner_page():
    st.markdown('<div class="main-header">🗺️ Route Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Find the best route for your journey</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['deep_slate_blue']} 0%, {COLORS['steel_blue']} 100%); 
                    padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
            <h2 style="margin: 0; font-size: 1.5rem;">⚙️ Trip Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Popular locations
        popular_locations = {
            "Connaught Place": "Connaught Place, Delhi",
            "India Gate": "India Gate, Delhi",
            "Saket": "Saket, Delhi",
            "Dwarka": "Dwarka, Delhi",
            "Noida City Centre": "Noida City Centre",
            "Rohini": "Rohini, Delhi",
            "Nehru Place": "Nehru Place, Delhi",
            "Hauz Khas": "Hauz Khas, Delhi",
            "Karol Bagh": "Karol Bagh, Delhi",
            "Custom": "Custom"
        }
        
        # Origin
        st.markdown("### 📍 Starting Point")
        origin_preset = st.selectbox("Quick Select", list(popular_locations.keys()), index=0, key="origin_preset")
        
        if origin_preset == "Custom":
            origin = st.text_input("Enter address", "Connaught Place, Delhi", key="origin_custom")
        else:
            origin = popular_locations[origin_preset]
            st.info(f"📌 {origin}")
        
        st.markdown("---")
        
        # Destination
        st.markdown("### 🎯 Destination")
        dest_preset = st.selectbox("Quick Select", list(popular_locations.keys()), index=2, key="dest_preset")
        
        if dest_preset == "Custom":
            destination = st.text_input("Enter address", "Saket, Delhi", key="dest_custom")
        else:
            destination = popular_locations[dest_preset]
            st.info(f"📌 {destination}")
        
        st.markdown("---")
        
        # Travel Priority
        st.markdown("### 🎯 Your Priority")
        preference_options = {
            "safety": {"icon": "🛡️", "label": "Safety First", "color": COLORS['deep_slate_blue']},
            "fastest": {"icon": "⚡", "label": "Fastest Route", "color": COLORS['steel_blue']},
            "eco": {"icon": "🌱", "label": "Eco-Friendly", "color": COLORS['muted_evergreen']},
            "balanced": {"icon": "⚖️", "label": "Balanced", "color": COLORS['graphite_grey']}
        }
        
        preference = st.radio(
            "Choose priority:",
            list(preference_options.keys()),
            format_func=lambda x: f"{preference_options[x]['icon']} {preference_options[x]['label']}",
            key="preference"
        )
        
        st.markdown("---")
        
        # API Configuration
        api_url = st.text_input("API Endpoint", "http://127.0.0.1:6000/api/compare-routes", key="api_url")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Search button
        if st.button("🔍 Find Best Routes", type="primary", use_container_width=True):
            st.session_state.show_results = True
            st.session_state.api_result = None
            st.rerun()
    
    # Main content
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
                            return
                    
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Connection Error: {str(e)}")
                        st.info("💡 Make sure the backend API is running on http://127.0.0.1:5000")
                        return
            
            result = st.session_state.api_result
            
            if result and 'routes' in result:
                # Create tabs
                tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Overview", "🚦 Route Details", "🚇 Transport Options", "📊 Analytics"])
                
                with tab1:
                    st.markdown("### 🎯 Recommended Route")
                    
                    recommended = result['recommended']
                    
                    # Recommended route card
                    st.markdown('<div class="route-card recommended">', unsafe_allow_html=True)
                    st.markdown('<span class="recommended-badge">✨ BEST MATCH FOR YOUR PRIORITY</span>', unsafe_allow_html=True)
                    
                    st.markdown(f"### {recommended['summary']}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**📏 Distance:** {recommended['distance_text']}")
                    with col2:
                        st.markdown(f"**⏱️ Duration:** {recommended['duration_text']}")
                    with col3:
                        risk_class = {
                            'Safe': 'risk-safe',
                            'Moderate': 'risk-moderate',
                            'Risky': 'risk-high'
                        }.get(recommended.get('risk_name', 'Safe'), 'risk-safe')
                        
                        risk_emoji = {'Safe': '🟢', 'Moderate': '🟡', 'Risky': '🔴'}
                        st.markdown(f"""**Risk:** <span class="{risk_class}">{risk_emoji.get(recommended.get('risk_name', 'Safe'), '⚪')} {recommended.get('risk_name', 'N/A')}</span>""", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Scores
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        score_class = get_score_class(recommended['safety_score'])
                        st.markdown(f"""
                        <div style="text-align: center">
                            <h4 style="color: {COLORS['deep_slate_blue']};">🛡️ Safety</h4>
                            <span class="score-badge {score_class}">
                                {recommended['safety_score']:.0f}/100
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        score_class = get_score_class(recommended['speed_score'])
                        st.markdown(f"""
                        <div style="text-align: center">
                            <h4 style="color: {COLORS['steel_blue']};">⚡ Speed</h4>
                            <span class="score-badge {score_class}">
                                {recommended['speed_score']:.0f}/100
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        score_class = get_score_class(recommended['eco_score'])
                        st.markdown(f"""
                        <div style="text-align: center">
                            <h4 style="color: {COLORS['muted_evergreen']};">🌱 Eco</h4>
                            <span class="score-badge {score_class}">
                                {recommended['eco_score']:.0f}/100
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        score_class = get_score_class(recommended['composite_score'])
                        st.markdown(f"""
                        <div style="text-align: center">
                            <h4 style="color: {COLORS['graphite_grey']};">⭐ Overall</h4>
                            <span class="score-badge {score_class}">
                                {recommended['composite_score']:.0f}/100
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Map visualization
                    if 'polyline' in recommended:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("### 🗺️ Route Visualization")
                        
                        try:
                            decoded = polyline.decode(recommended['polyline'])
                            
                            m = folium.Map(
                                location=[decoded[0][0], decoded[0][1]],
                                zoom_start=12,
                                tiles='OpenStreetMap'
                            )
                            
                            # Route color based on safety
                            route_color = COLORS['muted_evergreen'] if recommended['safety_score'] >= 70 else COLORS['caution_amber'] if recommended['safety_score'] >= 40 else '#E57373'
                            
                            folium.PolyLine(
                                decoded,
                                color=route_color,
                                weight=5,
                                opacity=0.8
                            ).add_to(m)
                            
                            # Markers
                            folium.Marker(
                                decoded[0],
                                popup=f"Start: {origin}",
                                icon=folium.Icon(color='green', icon='play')
                            ).add_to(m)
                            
                            folium.Marker(
                                decoded[-1],
                                popup=f"End: {destination}",
                                icon=folium.Icon(color='red', icon='stop')
                            ).add_to(m)
                            
                            st_folium(m, width=None, height=500)
                        
                        except Exception as e:
                            st.warning(f"Could not render map: {str(e)}")
                    
                    # Alternative routes
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.markdown("### 🔄 Alternative Routes")
                    
                    for route in result['routes']:
                        if route['rank'] != 1:
                            st.markdown('<div class="route-card">', unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"#### {route['summary']}")
                                st.markdown(f"**Rank:** #{route['rank']} | **Distance:** {route['distance_text']} | **Duration:** {route['duration_text']}")
                            
                            with col2:
                                score_class = get_score_class(route['composite_score'])
                                st.markdown(f"""
                                <div style="text-align: center">
                                    <span class="score-badge {score_class}">
                                        {route['composite_score']:.0f}/100
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("### 🚦 Detailed Route Information")
                    
                    for idx, route in enumerate(result['routes'], 1):
                        is_recommended = route['rank'] == 1
                        card_class = "route-card recommended" if is_recommended else "route-card"
                        
                        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                        
                        if is_recommended:
                            st.markdown('<span class="recommended-badge">⭐ RECOMMENDED</span>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"### Route {idx}: {route['summary']}")
                        
                        with col2:
                            # Navigate button
                            sample_points = polyline.decode(route['polyline']) if 'polyline' in route else []
                            waypoints_str = ""
                            
                            if len(sample_points) > 2:
                                sample_points = sample_points[::len(sample_points)//min(3, len(sample_points)-1)]
                                waypoints = "|".join([f"{lat},{lng}" for lat, lng in sample_points[:3]])
                                if waypoints:
                                    waypoints_str = f"&waypoints={waypoints}"
                            
                            maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}{waypoints_str}&travelmode=driving"
                            
                            st.markdown(f"""
                            <a href="{maps_url}" target="_blank" style="text-decoration: none;">
                                <button class="nav-button" style="width: 100%;">
                                    🗺️ Navigate
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
                        
                        # Basic info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**📏 Distance:** {route['distance_text']}")
                        with col2:
                            st.markdown(f"**⏱️ Duration:** {route['duration_text']}")
                        with col3:
                            risk_emoji = {'Safe': '🟢', 'Moderate': '🟡', 'Risky': '🔴'}
                            st.markdown(f"**Risk:** {risk_emoji.get(route.get('risk_name', 'Safe'), '⚪')} {route.get('risk_name', 'N/A')}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Detailed scores
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            score_class = get_score_class(route['safety_score'])
                            st.markdown(f"""
                            <div style="text-align: center">
                                <h4 style="color: {COLORS['deep_slate_blue']};">🛡️ Safety Score</h4>
                                <span class="score-badge {score_class}">
                                    {route['safety_score']:.0f}/100
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'avg_crime' in route:
                                st.caption(f"Crime Index: {route['avg_crime']:.2f}")
                            if 'avg_lighting' in route:
                                st.caption(f"Lighting Score: {route['avg_lighting']:.2f}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            score_class = get_score_class(route['speed_score'])
                            st.markdown(f"""
                            <div style="text-align: center">
                                <h4 style="color: {COLORS['steel_blue']};">⚡ Speed Score</h4>
                                <span class="score-badge {score_class}">
                                    {route['speed_score']:.0f}/100
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'avg_traffic' in route:
                                st.caption(f"Traffic Level: {route['avg_traffic']:.2f}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            score_class = get_score_class(route['eco_score'])
                            st.markdown(f"""
                            <div style="text-align: center">
                                <h4 style="color: {COLORS['muted_evergreen']};">🌱 Eco Score</h4>
                                <span class="score-badge {score_class}">
                                    {route['eco_score']:.0f}/100
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'avg_pollution' in route:
                                st.caption(f"Pollution Index: {route['avg_pollution']:.2f}")
                            if 'avg_carbon' in route:
                                st.caption(f"Carbon Footprint: {route['avg_carbon']:.2f}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                
                with tab3:
                    st.markdown("### 🚇 Transport Mode Recommendations")
                    st.info("💡 Based on distance, time, and route characteristics")
                    
                    # Get transport recommendations for the recommended route
                    recommended_route = result['recommended']
                    distance_km = recommended_route.get('distance', 0) / 1000  # Convert to km
                    duration_mins = recommended_route.get('duration', 0) / 60  # Convert to minutes
                    
                    transport_recs = get_detailed_transport_recommendations(
                        distance_km, 
                        duration_mins,
                        origin,
                        destination
                    )
                    
                    st.markdown(f"""
                    <div class="info-box">
                        <h4 style="margin-top: 0;">📍 Journey Summary</h4>
                        <p><strong>From:</strong> {origin}</p>
                        <p><strong>To:</strong> {destination}</p>
                        <p><strong>Distance:</strong> {distance_km:.1f} km | <strong>Estimated Time:</strong> {int(duration_mins)} mins</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display transport recommendations
                    for rec in transport_recs:
                        st.markdown('<div class="transport-section">', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <span class="transport-badge {rec['badge_class']}">{rec['mode']}</span>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"**⏱️ Time:** {rec['estimated_time']}")
                        
                        with col3:
                            st.markdown(f"**💰 Cost:** {rec['cost']}")
                        
                        # Detailed steps
                        if 'details' in rec:
                            with st.expander(f"View detailed {rec['mode']} route"):
                                st.markdown("#### 📋 Journey Steps")
                                
                                for step_num, step in enumerate(rec['details']['steps'], 1):
                                    st.markdown(f"""
                                    <div class="transport-step">
                                        <strong>Step {step_num}:</strong> {step}
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown(f"**🔄 Frequency:** {rec['details']['frequency']}")
                                    st.markdown(f"**✨ Ideal For:** {rec['details']['ideal_for']}")
                                
                                with col2:
                                    st.markdown("**✅ Advantages:**")
                                    for adv in rec['details']['advantages']:
                                        st.markdown(f"• {adv}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Comparison table
                    st.markdown("### 📊 Quick Comparison")
                    
                    comparison_data = []
                    for rec in transport_recs:
                        comparison_data.append({
                            'Mode': rec['mode'],
                            'Time': rec['estimated_time'],
                            'Cost': rec['cost'],
                            'Best For': rec['details']['ideal_for'] if 'details' in rec else 'N/A'
                        })
                    
                    import pandas as pd
                    df_comparison = pd.DataFrame(comparison_data)
                    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                
                with tab4:
                    st.markdown("### 📊 Route Analytics & Comparison")
                    
                    # Comparison chart
                    routes = result['routes']
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        name='Safety',
                        x=[r['summary'] for r in routes],
                        y=[r['safety_score'] for r in routes],
                        marker_color=COLORS['deep_slate_blue']
                    ))
                    
                    fig.add_trace(go.Bar(
                        name='Speed',
                        x=[r['summary'] for r in routes],
                        y=[r['speed_score'] for r in routes],
                        marker_color=COLORS['steel_blue']
                    ))
                    
                    fig.add_trace(go.Bar(
                        name='Eco',
                        x=[r['summary'] for r in routes],
                        y=[r['eco_score'] for r in routes],
                        marker_color=COLORS['muted_evergreen']
                    ))
                    
                    fig.update_layout(
                        title='Route Score Comparison',
                        xaxis_title='Route',
                        yaxis_title='Score (0-100)',
                        barmode='group',
                        height=500,
                        font=dict(family="Arial, sans-serif")
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
                        line_color=COLORS['deep_slate_blue'],
                        fillcolor=COLORS['steel_blue'],
                        opacity=0.6
                    ))
                    
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )
                        ),
                        showlegend=True,
                        height=450
                    )
                    
                    st.plotly_chart(fig_radar, use_container_width=True)
                    
                    # Detailed metrics table
                    st.markdown("### 📈 Detailed Route Metrics")
                    
                    metrics_data = []
                    for route in routes:
                        metrics_data.append({
                            'Rank': f"#{route['rank']}",
                            'Route': route['summary'],
                            'Distance': route['distance_text'],
                            'Duration': route['duration_text'],
                            'Safety': f"{route['safety_score']:.0f}/100",
                            'Speed': f"{route['speed_score']:.0f}/100",
                            'Eco': f"{route['eco_score']:.0f}/100",
                            'Overall': f"{route['composite_score']:.0f}/100",
                            'Risk Level': route.get('risk_name', 'N/A')
                        })
                    
                    df_metrics = pd.DataFrame(metrics_data)
                    st.dataframe(df_metrics, use_container_width=True, hide_index=True)
    
    else:
        # Welcome screen for planner
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">👈 Get Started</h3>
            <p>Configure your route settings in the sidebar and click <strong>'Find Best Routes'</strong> to get personalized recommendations!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <div class="feature-title">Safety Analysis</div>
                <div class="feature-text">
                    Routes evaluated for crime statistics, street lighting, and safety metrics
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🚇</div>
                <div class="feature-title">Multi-Modal Options</div>
                <div class="feature-text">
                    Detailed recommendations for Metro, Bus, Cab, Bike, and Walking
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Smart Analytics</div>
                <div class="feature-text">
                    Real-time data visualization and route comparison tools
                </div>
            </div>
            """, unsafe_allow_html=True)

# Main app logic
show_navigation()

if st.session_state.page == "home":
    show_home_page()
elif st.session_state.page == "planner":
    show_planner_page()
elif st.session_state.page == "about":
    st.markdown('<div class="main-header">ℹ️ About SafeRoute</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Building safer journeys through AI and data</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>🏆 Built for LeanIn Hackathon</h3>
        <p>SafeRoute Delhi is an AI-powered navigation system designed to make urban travel safer, faster, and more sustainable.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔧 Technology Stack")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Machine Learning:**
        - Random Forest Classification
        - Real-time Risk Prediction
        - Multi-factor Optimization
        
        **Data Sources:**
        - Delhi Police Crime Data
        - Google Maps API
        - OpenAQ Air Quality
        - Real-time Traffic Data
        """)
    
    with col2:
        st.markdown("""
        **Frontend:**
        - Streamlit
        - Plotly Charts
        - Folium Maps
        - Custom CSS/HTML
        
        **Backend:**
        - Flask API
        - Python Data Processing
        - Route Optimization Algorithms
        """)
    
    st.markdown("### 👥 Team")
    st.info("Developed with ❤️ for making Delhi safer for everyone")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: {COLORS['graphite_grey']}; padding: 2rem 0;">
    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">🏆 <strong>SafeRoute Delhi</strong> - Navigate with Confidence</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">Powered by AI • Real-time Data • Built for Safety</p>
    <p style="font-size: 0.85rem; opacity: 0.7; margin-top: 1rem;">
        Using: Random Forest ML | Google Maps API | OpenAQ | Delhi Police Data
    </p>
</div>
""", unsafe_allow_html=True)
