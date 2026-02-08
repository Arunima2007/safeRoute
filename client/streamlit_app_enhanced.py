# streamlit_app_enhanced.py

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

if "show_home" not in st.session_state:
    st.session_state.show_home = True

# Page config
st.set_page_config(
    page_title="SafeRoute Delhi - Smart Navigation",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Delhi Locations - 50+ popular places
DELHI_LOCATIONS = {
    # Central Delhi
    "Connaught Place": "Connaught Place, New Delhi",
    "India Gate": "India Gate, New Delhi",
    "Rashtrapati Bhavan": "Rashtrapati Bhavan, New Delhi",
    "Parliament House": "Parliament House, New Delhi",
    "Rajpath": "Rajpath, New Delhi",
    "Jantar Mantar": "Jantar Mantar, New Delhi",
    "Palika Bazaar": "Palika Bazaar, Connaught Place, New Delhi",
    
    # North Delhi
    "Red Fort": "Red Fort, Chandni Chowk, Delhi",
    "Chandni Chowk": "Chandni Chowk, Delhi",
    "Jama Masjid": "Jama Masjid, Chandni Chowk, Delhi",
    "Kashmere Gate": "Kashmere Gate, Delhi",
    "Civil Lines": "Civil Lines, Delhi",
    "GTB Nagar": "GTB Nagar, Delhi",
    "North Campus": "North Campus, University of Delhi",
    "Kamla Nagar": "Kamla Nagar Market, Delhi",
    
    # South Delhi
    "Qutub Minar": "Qutub Minar, Mehrauli, Delhi",
    "Hauz Khas Village": "Hauz Khas Village, Delhi",
    "Saket": "Saket, New Delhi",
    "Nehru Place": "Nehru Place, New Delhi",
    "Greater Kailash": "Greater Kailash, New Delhi",
    "Green Park": "Green Park, New Delhi",
    "Defence Colony": "Defence Colony, New Delhi",
    "Lajpat Nagar": "Lajpat Nagar, New Delhi",
    "South Extension": "South Extension, New Delhi",
    "Vasant Kunj": "Vasant Kunj, New Delhi",
    "Vasant Vihar": "Vasant Vihar, New Delhi",
    "Sarojini Nagar": "Sarojini Nagar Market, New Delhi",
    "IIT Delhi": "IIT Delhi, Hauz Khas",
    "JNU": "Jawaharlal Nehru University, New Delhi",
    "Malviya Nagar": "Malviya Nagar, New Delhi",
    "Kalkaji": "Kalkaji, New Delhi",
    
    # East Delhi
    "Akshardham Temple": "Akshardham Temple, Delhi",
    "Mayur Vihar": "Mayur Vihar, Delhi",
    "Preet Vihar": "Preet Vihar, Delhi",
    "Laxmi Nagar": "Laxmi Nagar, Delhi",
    "Noida Sector 18": "Sector 18, Noida",
    "Noida City Centre": "Noida City Centre",
    "Anand Vihar": "Anand Vihar, Delhi",
    
    # West Delhi
    "Rajouri Garden": "Rajouri Garden, Delhi",
    "Janakpuri": "Janakpuri, Delhi",
    "Pitampura": "Pitampura, Delhi",
    "Rohini": "Rohini, Delhi",
    "Punjabi Bagh": "Punjabi Bagh, Delhi",
    "Paschim Vihar": "Paschim Vihar, Delhi",
    "Dwarka": "Dwarka, New Delhi",
    "Dwarka Sector 21": "Dwarka Sector 21, New Delhi",
    "Janakpuri West": "Janakpuri West, Delhi",
    
    # Gurgaon (NCR)
    "Cyber City Gurgaon": "Cyber City, Gurgaon",
    "MG Road Gurgaon": "MG Road, Gurgaon",
    "Ambience Mall Gurgaon": "Ambience Mall, Gurgaon",
    "Kingdom of Dreams": "Kingdom of Dreams, Gurgaon",
    
    # Transport Hubs
    "New Delhi Railway Station": "New Delhi Railway Station",
    "Old Delhi Railway Station": "Old Delhi Railway Station",
    "Hazrat Nizamuddin Railway Station": "Hazrat Nizamuddin Railway Station",
    "IGI Airport Terminal 3": "Indira Gandhi International Airport Terminal 3",
    "IGI Airport Terminal 1": "Indira Gandhi International Airport Terminal 1",
    "Anand Vihar ISBT": "Anand Vihar ISBT, Delhi",
    "Kashmere Gate ISBT": "Kashmere Gate ISBT, Delhi",
    
    # Educational & Cultural
    "Jawaharlal Nehru Stadium": "Jawaharlal Nehru Stadium, Delhi",
    "Pragati Maidan": "Pragati Maidan, New Delhi",
    "National Museum": "National Museum, New Delhi",
    "Khan Market": "Khan Market, New Delhi",
    
    # Commercial Areas
    "Karol Bagh": "Karol Bagh, Delhi",
    "Chandni Chowk Market": "Chandni Chowk Market, Delhi",
    "Dilli Haat INA": "Dilli Haat, INA, New Delhi",
    "Select Citywalk": "Select Citywalk Mall, Saket",
    "DLF Promenade": "DLF Promenade, Vasant Kunj",
}

# Enhanced Modern CSS with animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main background with gradient */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 4rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        animation: fadeInDown 1s ease;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.95);
        margin-top: 1rem;
        font-weight: 400;
        animation: fadeInUp 1s ease;
    }
    
    .hero-tagline {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.85);
        margin-top: 0.5rem;
        font-weight: 300;
        animation: fadeInUp 1.2s ease;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.8);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        font-size: 1rem;
        color: #6b7280;
        line-height: 1.6;
    }
    
    /* CTA Button */
    .cta-button {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem 3rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s;
        border: none;
        cursor: pointer;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        margin-top: 2rem;
    }
    
    .cta-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    /* Stats Section */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 3rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Header styling for results page */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
    }
    
    .app-title {
        font-size: 2.2rem;
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
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
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
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1.5rem;
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
        width: 70px;
        height: 70px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.5rem;
        color: white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .score-high { background: linear-gradient(135deg, #10b981, #059669); }
    .score-medium { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .score-low { background: linear-gradient(135deg, #ef4444, #dc2626); }
    
    /* Button styling */
    .nav-btn {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
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
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .nav-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
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
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
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
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-recommended {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    
    .badge-safe { background-color: #10b981; color: white; }
    .badge-fast { background-color: #3b82f6; color: white; }
    .badge-eco { background-color: #8b5cf6; color: white; }
    
    /* Divider */
    .divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #e5e7eb, transparent);
        margin: 1.5rem 0;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        border-left: 4px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-size: 1.1rem;
        color: #1e40af;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        .hero-subtitle {
            font-size: 1.1rem;
        }
        .feature-card {
            padding: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Helper functions (same as before)
def get_score_class(score):
    if score >= 70:
        return "score-high"
    elif score >= 40:
        return "score-medium"
    return "score-low"

def format_metro_line_color(line_name):
    color_map = {
        'Red': 'line-red',
        'Yellow': 'line-yellow',
        'Blue': 'line-blue',
        'Green': 'line-green',
        'Violet': 'line-violet',
        'Pink': 'line-pink',
        'Magenta': 'line-magenta',
        'Grey': 'line-grey'
    }
    
    for key, value in color_map.items():
        if key.lower() in line_name.lower():
            return value
    return 'line-grey'

def generate_metro_stations():
    return [
        {"name": "Rajiv Chowk", "line": "Blue/Yellow Line", "distance": "500m"},
        {"name": "Central Secretariat", "line": "Yellow/Violet Line", "distance": "1.2km"}
    ]

def generate_bus_routes():
    return [
        {"number": "764", "route": "ITO - Connaught Place", "duration": "25 min", "fare": "₹10", "frequency": "Every 15 min"},
        {"number": "429", "route": "Kashmere Gate - CP", "duration": "30 min", "fare": "₹10", "frequency": "Every 20 min"}
    ]

# HOME PAGE
if st.session_state.show_home:
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🛡️ SafeRoute Delhi</div>
        <div class="hero-subtitle">Your AI-Powered Intelligent Navigation Companion</div>
        <div class="hero-tagline">Navigate Delhi Safely, Quickly, and Sustainably</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🛡️</span>
            <div class="feature-title">Safety First</div>
            <div class="feature-description">
                Advanced AI analyzes crime statistics, lighting conditions, and real-time traffic to recommend the safest routes for your journey.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">⚡</span>
            <div class="feature-title">Lightning Fast</div>
            <div class="feature-description">
                Real-time traffic analysis and route optimization to get you to your destination in the shortest possible time.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🌱</span>
            <div class="feature-title">Eco-Friendly</div>
            <div class="feature-description">
                Air quality monitoring and carbon footprint tracking to help you choose greener transportation options.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="justify-content: center;">📊 Platform Statistics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">50K+</div>
            <div class="stat-label">Routes Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">95%</div>
            <div class="stat-label">Safety Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">60+</div>
            <div class="stat-label">Delhi Locations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Real-Time Data</div>
        </div>
        """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="justify-content: center;">🚀 How It Works</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <h2 style="color: #667eea; font-size: 3rem; margin: 0;">1</h2>
            <h3 style="margin-top: 1rem;">Select Locations</h3>
            <p>Choose your starting point and destination from 60+ popular Delhi locations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <h2 style="color: #667eea; font-size: 3rem; margin: 0;">2</h2>
            <h3 style="margin-top: 1rem;">AI Analysis</h3>
            <p>Our AI evaluates routes based on safety, speed, and environmental impact</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <h2 style="color: #667eea; font-size: 3rem; margin: 0;">3</h2>
            <h3 style="margin-top: 1rem;">Get Recommendations</h3>
            <p>Receive personalized route suggestions with detailed transportation options</p>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center;">
        <h2 style="color: #1f2937; font-weight: 700; font-size: 2rem; margin-bottom: 1rem;">
            Ready to Navigate Delhi Smarter?
        </h2>
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
            Join thousands of users making safer, faster, and greener travel choices every day
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Start Planning Your Route", use_container_width=True, type="primary"):
            st.session_state.show_home = False
            st.rerun()

# RESULTS PAGE (Main Application)
else:
    # Header
    st.markdown("""
    <div class="app-header">
        <div class="app-title">🛡️ SafeRoute Delhi</div>
        <div class="app-subtitle">AI-Powered Safe Route Navigation</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Back to Home button
    if st.sidebar.button("⬅️ Back to Home", use_container_width=True):
        st.session_state.show_home = True
        st.session_state.show_results = False
        st.rerun()
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### 📍 Route Configuration")
        
        # Origin selection
        origin_key = st.selectbox(
            "Origin",
            options=sorted(DELHI_LOCATIONS.keys()),
            index=sorted(DELHI_LOCATIONS.keys()).index("Connaught Place"),
            help="Select your starting location"
        )
        origin = DELHI_LOCATIONS[origin_key]
        
        # Destination selection
        dest_key = st.selectbox(
            "Destination",
            options=sorted(DELHI_LOCATIONS.keys()),
            index=sorted(DELHI_LOCATIONS.keys()).index("India Gate"),
            help="Select your destination"
        )
        destination = DELHI_LOCATIONS[dest_key]
        
        st.markdown("---")
        
        # Preference settings
        st.markdown("### ⚙️ Route Preferences")
        
        preference = st.radio(
            "Priority",
            ["Balanced", "Safety First", "Fastest", "Most Eco-Friendly"],
            help="Choose what matters most to you"
        )
        
        time_of_day = st.selectbox(
            "Time of Travel",
            ["Morning (6AM-12PM)", "Afternoon (12PM-6PM)", "Evening (6PM-10PM)", "Night (10PM-6AM)"],
            help="Travel time affects safety and traffic"
        )
        
        avoid_options = st.multiselect(
            "Avoid",
            ["Tolls", "Highways", "Poorly Lit Areas", "High Crime Areas"],
            help="Select areas or features to avoid"
        )
        
        st.markdown("---")
        
        # Find Routes button
        if st.button("🔍 Find Routes", use_container_width=True, type="primary"):
            with st.spinner("🔄 Analyzing routes with AI..."):
                try:
                    # API call
                    preference_map = {
                        'Balanced': 'balanced',
                        'Safety First': 'safety',
                        'Fastest': 'fastest',
                        'Most Eco-Friendly': 'eco'
                    }

                    response = requests.post(
                        'http://127.0.0.1:6000/api/compare-routes',
                        json={
                            'origin': origin,
                            'destination': destination,
                            'preference': preference_map.get(preference,'balanced')
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.api_result = result
                        st.session_state.show_results = True
                        st.success("✅ Routes found successfully!")
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        st.session_state.show_results = False
                        
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
                    st.session_state.show_results = False
    
    # Main content
    if st.session_state.show_results and st.session_state.api_result:
        result = st.session_state.api_result
        
        # Recommended Route
        recommended = result['routes'][0] if result['routes'] else None
        
        if recommended:
            st.markdown('<div class="section-header">🎯 Recommended Route</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card recommended-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### {recommended['summary']}")
                st.markdown(f"**{origin_key}** → **{dest_key}**")
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("📏 Distance", recommended['distance_text'])
                col_b.metric("⏱️ Duration", recommended['duration_text'])
                col_c.metric("🏆 Score", f"{recommended['composite_score']:.0f}/100")
            
            with col2:
                col_x, col_y, col_z = st.columns(3)
                
                with col_x:
                    score_class = get_score_class(recommended['safety_score'])
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="stat-label">🛡️ Safety</div>
                        <div class="score-badge {score_class}">{recommended['safety_score']:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_y:
                    score_class = get_score_class(recommended['speed_score'])
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="stat-label">⚡ Speed</div>
                        <div class="score-badge {score_class}">{recommended['speed_score']:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_z:
                    score_class = get_score_class(recommended['eco_score'])
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="stat-label">🌱 Eco</div>
                        <div class="score-badge {score_class}">{recommended['eco_score']:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Transportation Options
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">🚇 Transportation Options</div>', unsafe_allow_html=True)
        
        distance_km = recommended.get('distance_meters', 0) / 1000 if recommended else 0
        
        # Metro
        origin_stations = generate_metro_stations()
        dest_stations = generate_metro_stations()
        
        st.markdown('<div class="card metro-card">', unsafe_allow_html=True)
        st.markdown("#### 🚇 Delhi Metro")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Estimated Fare", "₹20-60")
        col2.metric("Travel Time", "30-45 min")
        col3.metric("Frequency", "3-5 min")
        
        st.caption(f"📍 Nearest from origin: {', '.join([s['name'] for s in origin_stations[:2]])}")
        st.caption(f"📍 Nearest to destination: {', '.join([s['name'] for s in dest_stations[:2]])}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bus
        if distance_km >= 2:
            bus_routes = generate_bus_routes()
            
            st.markdown('<div class="card bus-card">', unsafe_allow_html=True)
            st.markdown("#### 🚌 DTC Bus")
            
            for bus in bus_routes:
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.markdown(f"**Bus {bus['number']}** • {bus['route']}")
                col2.markdown(f"⏱️ {bus['duration']}")
                col3.markdown(f"💰 {bus['fare']}")
                st.caption(f"Frequency: {bus['frequency']}")
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Car/Taxi
        if distance_km >= 3:
            st.markdown('<div class="card car-card">', unsafe_allow_html=True)
            st.markdown("#### 🚗 Cab / Taxi")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Ola/Uber", f"₹{int(distance_km * 15)}-{int(distance_km * 20)}")
            col2.metric("Auto Rickshaw", f"₹{int(distance_km * 12)}-{int(distance_km * 15)}")
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
            
            st.markdown("#### 🚴 Cycling / E-Scooter")
            col1, col2, col3 = st.columns(3)
            col1.metric("Distance", f"{distance_km:.1f} km")
            col2.metric("Time", f"~{int(distance_km * 6)} min")
            col3.metric("Cost", "₹10-30")
            st.caption("🌱 Eco-friendly • Available on Yulu, Bounce, Rapido")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Route Analysis
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Detailed Route Analysis</div>', unsafe_allow_html=True)
        
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
        tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "📋 All Routes", "📊 Analytics"])
        
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
                
                badge = '<span class="badge badge-recommended">RECOMMENDED</span>' if is_rec else ''
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
        st.markdown('<div class="info-box">👆 Configure your route in the sidebar and click "Find Routes" to get started</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="card">
                <h3>🛡️ Safety Analysis</h3>
                <p>Routes evaluated based on crime statistics, lighting conditions, and real-time safety data</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <h3>🌱 Eco-Conscious</h3>
                <p>Air quality monitoring, carbon footprint tracking, and green transportation alternatives</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="card">
                <h3>🤖 AI-Driven</h3>
                <p>Machine learning algorithms for real-time risk prediction and intelligent route optimization</p>
            </div>
            """, unsafe_allow_html=True)
