# streamlit_app_fixed.py
"""
SafeRoute Delhi - AI-Powered Sustainable and Safe Route Recommendation System
Fixed Version - Proper Colors & Working Map
"""

import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import polyline

# Initialize session state
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "api_result" not in st.session_state:
    st.session_state.api_result = None

# Page config
st.set_page_config(
    page_title="SafeRoute Delhi - AI-Powered Safe & Sustainable Routes",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fixed CSS with proper color contrast
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #F9FAFB 0%, #FFFFFF 100%);
        color: #111827;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 2rem 0 0.5rem 0;
        line-height: 1.2;
    }
    
    .subtitle {
        text-align: center;
        color: #374151;
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
        font-weight: 500;
    }
    
    .sdg-badges {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin: 1.5rem 0 2.5rem 0;
        flex-wrap: wrap;
    }
    
    .sdg-badge {
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .sdg-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.25);
    }
    
    .sdg-11 {
        background: linear-gradient(135deg, #F59E0B 0%, #F97316 100%);
        color: white;
    }
    
    .sdg-13 {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white;
    }
    
    .route-type-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 24px;
        font-weight: 700;
        font-size: 0.875rem;
        margin-bottom: 1rem;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .badge-safest { background: linear-gradient(135deg, #10B981 0%, #059669 100%); }
    .badge-eco { background: linear-gradient(135deg, #34D399 0%, #10B981 100%); }
    .badge-fastest { background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); }
    .badge-balanced { background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); }
    
    .score-circle {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.5rem;
        margin: 0.5rem;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .score-excellent { background: linear-gradient(135deg, #10B981 0%, #059669 100%); }
    .score-good { background: linear-gradient(135deg, #84CC16 0%, #65A30D 100%); }
    .score-moderate { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); }
    .score-poor { background: linear-gradient(135deg, #F97316 0%, #EA580C 100%); }
    .score-critical { background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); }
    
    .carbon-badge {
        display: inline-block;
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.875rem;
        margin: 0.75rem 0;
    }
    
    .carbon-low {
        background: #ECFDF5;
        color: #047857;
        border: 2px solid #10B981;
    }
    .carbon-medium {
        background: #FFFBEB;
        color: #92400E;
        border: 2px solid #F59E0B;
    }
    .carbon-high {
        background: #FEF2F2;
        color: #991B1B;
        border: 2px solid #EF4444;
    }
    
    .feature-box {
        padding: 2rem;
        border-radius: 16px;
        background: white;
        border: 2px solid #E5E7EB;
        height: 100%;
        transition: all 0.3s;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .feature-box:hover {
        border-color: #10B981;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        transform: translateY(-4px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .feature-text {
        font-size: 0.95rem;
        color: #374151;
        line-height: 1.7;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white;
        font-weight: 700;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        border: none;
        transition: all 0.2s;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #047857 0%, #059669 100%);
        box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    .info-box {
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .info-box.success-box {
        background-color: #ECFDF5;
        border-left-color: #10B981;
        color: #065F46;
    }
    
    .info-box.warning-box {
        background-color: #FFFBEB;
        border-left-color: #F59E0B;
        color: #92400E;
    }
    
    .info-box.alert-box {
        background-color: #FEF2F2;
        border-left-color: #EF4444;
        color: #991B1B;
    }
    
    .risk-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9rem;
        margin: 0.75rem 0;
    }
    
    .risk-safe {
        background: #ECFDF5;
        color: #047857;
        border: 2px solid #10B981;
    }
    
    .risk-moderate {
        background: #FFFBEB;
        color: #92400E;
        border: 2px solid #F59E0B;
    }
    
    .risk-high {
        background: #FEF2F2;
        color: #991B1B;
        border: 2px solid #EF4444;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 800;
        color: #111827;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: #6B7280;
        font-weight: 600;
    }
    
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_score_class(score):
    if score >= 80: return "score-excellent"
    elif score >= 60: return "score-good"
    elif score >= 40: return "score-moderate"
    elif score >= 20: return "score-poor"
    else: return "score-critical"

def get_score_label(score):
    if score >= 80: return "Excellent"
    elif score >= 60: return "Good"
    elif score >= 40: return "Moderate"
    elif score >= 20: return "Poor"
    else: return "Critical"

def get_route_badge(summary):
    route_summary = summary.lower()
    if 'safe' in route_summary:
        return 'badge-safest', '🛡️ SAFEST ROUTE'
    elif 'eco' in route_summary or 'green' in route_summary:
        return 'badge-eco', '🌱 ECO-FRIENDLY'
    elif 'fast' in route_summary or 'quick' in route_summary:
        return 'badge-fastest', '⚡ FASTEST'
    else:
        return 'badge-balanced', '⚖️ BALANCED'

def decode_polyline(encoded):
    """Decode a polyline string into lat/lng coordinates"""
    try:
        return polyline.decode(encoded)
    except:
        return []

# Header
st.markdown('<div class="main-header">🛡️ SafeRoute Delhi</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Smart Route Navigation for Safety, Speed & Sustainability</div>', unsafe_allow_html=True)
st.markdown('''
<div class="sdg-badges">
    <span class="sdg-badge sdg-11">SDG 11: Sustainable Cities</span>
    <span class="sdg-badge sdg-13">SDG 13: Climate Action</span>
</div>
''', unsafe_allow_html=True)

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
        "Karol Bagh": "Karol Bagh, Delhi",
        "Custom": "Custom"
    }
    
    st.markdown("#### 📍 Starting Point")
    origin_preset = st.selectbox(
        "Quick Select Origin", 
        list(popular_locations.keys()), 
        index=4,
        label_visibility="collapsed"
    )
    
    if origin_preset == "Custom":
        origin = st.text_input("Enter origin address", "Connaught Place, Delhi")
    else:
        origin = popular_locations[origin_preset]
        st.caption(f"📌 {origin}")
    
    st.markdown("---")
    
    st.markdown("#### 🎯 Destination")
    dest_preset = st.selectbox(
        "Quick Select Destination", 
        list(popular_locations.keys()), 
        index=3,
        label_visibility="collapsed"
    )
    
    if dest_preset == "Custom":
        destination = st.text_input("Enter destination address", "Saket, Delhi")
    else:
        destination = popular_locations[dest_preset]
        st.caption(f"📌 {destination}")
    
    st.markdown("---")
    
    st.markdown("#### 🎯 Travel Priority")
    preference_options = {
        "balanced": {"icon": "⚖️", "label": "Balanced", "desc": "Optimal tradeoff"},
        "safety": {"icon": "🛡️", "label": "Safety First", "desc": "Prioritize safety"},
        "eco": {"icon": "🌱", "label": "Eco-Friendly", "desc": "Minimize carbon"},
        "fastest": {"icon": "⚡", "label": "Fastest Route", "desc": "Quickest arrival"}
    }
    
    preference = st.radio(
        "Choose your priority:",
        list(preference_options.keys()),
        format_func=lambda x: f"{preference_options[x]['icon']} {preference_options[x]['label']}",
        label_visibility="collapsed"
    )
    
    st.caption(preference_options[preference]['desc'])
    
    st.markdown("---")
    
    api_url = st.text_input(
        "API Endpoint", 
        "http://127.0.0.1:5000/api/compare-routes",
        help="Backend API URL"
    )
    
    st.markdown("---")
    
    if st.button("🔍 Find Best Routes", type="primary", use_container_width=True):
        st.session_state.show_results = True
        st.session_state.api_result = None
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### 💡 About")
    st.caption("AI-powered route analysis for safer, greener cities.")
    st.caption(f"Version 1.0 | {datetime.now().strftime('%B %Y')}")

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
                        st.rerun()
                    else:
                        st.markdown(f"""
                        <div class="info-box alert-box">
                            <strong>❌ API Error {response.status_code}</strong><br>
                            Unable to fetch route data.
                        </div>
                        """, unsafe_allow_html=True)
                        st.stop()
                        
                except requests.exceptions.ConnectionError:
                    st.markdown("""
                    <div class="info-box alert-box">
                        <strong>❌ Connection Error</strong><br>
                        Cannot connect to API. Start server with: <code>python route_server.py</code>
                    </div>
                    """, unsafe_allow_html=True)
                    st.stop()
                except Exception as e:
                    st.markdown(f"""
                    <div class="info-box alert-box">
                        <strong>❌ Error</strong><br>
                        {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
                    st.stop()
        
        if st.session_state.api_result is not None:
            result = st.session_state.api_result
            
            st.markdown(f"""
            <div class="info-box success-box">
                <strong>✅ Analysis Complete!</strong><br>
                Found <strong>{result.get('total_routes', 0)} route options</strong> based on your 
                <strong>{preference_options[preference]['label']}</strong> preference.
            </div>
            """, unsafe_allow_html=True)
            
            if 'summary' in result:
                st.markdown("### 📊 Quick Comparison")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🛡️ Safety Range", result['summary']['score_range']['safety'])
                    st.caption(f"Best: {result['summary']['safest_route']}")
                
                with col2:
                    st.metric("⚡ Speed Range", result['summary']['score_range']['speed'])
                    st.caption(f"Best: {result['summary']['fastest_route']}")
                
                with col3:
                    st.metric("🌱 Eco Range", result['summary']['score_range']['eco'])
                    st.caption(f"Best: {result['summary']['greenest_route']}")
                
                with col4:
                    if 'recommended' in result:
                        st.metric("⭐ Recommended", f"Route #{result['recommended']['rank']}")
                        st.caption(result['recommended'].get('summary', '')[:25] + "...")
                
                st.markdown("---")
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Route Details",
                "🗺️ Interactive Map", 
                "📊 Analytics",
                "🤖 AI Insights"
            ])
            
            with tab1:
                st.markdown("### 📋 All Routes")
                
                routes = result.get('routes', [])
                
                for route in routes:
                    is_recommended = route['rank'] == 1
                    badge_class, badge_text = get_route_badge(route['summary'])
                    
                    with st.container():
                        if is_recommended:
                            st.markdown("#### ⭐ RECOMMENDED ROUTE")
                        else:
                            st.markdown(f"#### Route #{route['rank']}")
                        
                        st.markdown(f'<span class="route-type-badge {badge_class}">{badge_text}</span>', 
                                  unsafe_allow_html=True)
                        
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.markdown(f"**📍 {route['summary']}**")
                            if route.get('explanation'):
                                st.caption(route['explanation'])
                        
                        with col2:
                            st.metric("Distance", route['distance_text'])
                        
                        with col3:
                            st.metric("Duration", route['duration_text'])
                        
                        with col4:
                            st.metric("Overall", f"{route['composite_score']:.0f}/100")
                        
                        st.markdown("#### Scores")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            score_class = get_score_class(route['safety_score'])
                            st.markdown(f"""
                            <div style="text-align: center">
                                <h4 style="color: #374151;">🛡️ Safety</h4>
                                <div class="score-circle {score_class}">
                                    {route['safety_score']:.0f}
                                </div>
                                <p style="margin-top: 0.5rem; color: #6B7280; font-weight: 600;">
                                    {get_score_label(route['safety_score'])}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'avg_crime' in route:
                                st.caption(f"Crime: {route['avg_crime']:.2f}/10")
                            if 'avg_lighting' in route:
                                st.caption(f"Lighting: {route['avg_lighting']:.2f}/10")
                        
                        with col2:
                            score_class = get_score_class(route['speed_score'])
                            st.markdown(f"""
                            <div style="text-align: center">
                                <h4 style="color: #374151;">⚡ Speed</h4>
                                <div class="score-circle {score_class}">
                                    {route['speed_score']:.0f}
                                </div>
                                <p style="margin-top: 0.5rem; color: #6B7280; font-weight: 600;">
                                    {get_score_label(route['speed_score'])}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'avg_traffic' in route:
                                st.caption(f"Traffic: {route['avg_traffic']:.2f}/10")
                        
                        with col3:
                            score_class = get_score_class(route['eco_score'])
                            st.markdown(f"""
                            <div style="text-align: center">
                                <h4 style="color: #374151;">🌱 Eco</h4>
                                <div class="score-circle {score_class}">
                                    {route['eco_score']:.0f}
                                </div>
                                <p style="margin-top: 0.5rem; color: #6B7280; font-weight: 600;">
                                    {get_score_label(route['eco_score'])}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'avg_pollution' in route:
                                st.caption(f"Pollution: {route['avg_pollution']:.2f}/10")
                        
                        if 'avg_carbon' in route:
                            carbon = route['avg_carbon']
                            if carbon < 1:
                                carbon_class = 'carbon-low'
                                carbon_label = 'Low Carbon'
                            elif carbon < 3:
                                carbon_class = 'carbon-medium'
                                carbon_label = 'Medium Carbon'
                            else:
                                carbon_class = 'carbon-high'
                                carbon_label = 'High Carbon'
                            
                            st.markdown(f"""
                            <div style="margin-top: 1rem;">
                                <span class="carbon-badge {carbon_class}">
                                    🌍 {carbon_label}: {carbon:.2f} kg CO₂
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if 'risk_name' in route:
                            risk_name = route['risk_name']
                            if risk_name == 'Safe':
                                risk_class = 'risk-safe'
                                risk_emoji = '🟢'
                            elif risk_name == 'Moderate':
                                risk_class = 'risk-moderate'
                                risk_emoji = '🟡'
                            else:
                                risk_class = 'risk-high'
                                risk_emoji = '🔴'
                            
                            st.markdown(f"""
                            <div class="risk-indicator {risk_class}">
                                {risk_emoji} Risk: {risk_name}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
            
            with tab2:
                st.markdown("### 🗺️ Interactive Route Map")
                
                routes = result.get('routes', [])
                
                if routes:
                    # Create map
                    m = folium.Map(
                        location=[28.6139, 77.2090],
                        zoom_start=11,
                        tiles='OpenStreetMap'
                    )
                    
                    # Try to get actual coordinates from routes
                    start_lat, start_lng = 28.6139, 77.2090
                    end_lat, end_lng = 28.6139, 77.2090
                    
                    # Use first route for start/end if available
                    if routes and 'start_location' in routes[0]:
                        start_lat = routes[0]['start_location'].get('lat', start_lat)
                        start_lng = routes[0]['start_location'].get('lng', start_lng)
                    if routes and 'end_location' in routes[0]:
                        end_lat = routes[0]['end_location'].get('lat', end_lat)
                        end_lng = routes[0]['end_location'].get('lng', end_lng)
                    
                    # Add start marker
                    folium.Marker(
                        [start_lat, start_lng],
                        popup=folium.Popup(f"""
                        <div style="min-width: 200px; font-family: Inter;">
                            <h4 style="margin: 0; color: #111827;">📍 Start</h4>
                            <p style="margin: 0.5rem 0 0 0; color: #374151;">{origin}</p>
                        </div>
                        """, max_width=250),
                        icon=folium.Icon(color='green', icon='play', prefix='fa')
                    ).add_to(m)
                    
                    # Add end marker
                    folium.Marker(
                        [end_lat, end_lng],
                        popup=folium.Popup(f"""
                        <div style="min-width: 200px; font-family: Inter;">
                            <h4 style="margin: 0; color: #111827;">🎯 Destination</h4>
                            <p style="margin: 0.5rem 0 0 0; color: #374151;">{destination}</p>
                        </div>
                        """, max_width=250),
                        icon=folium.Icon(color='red', icon='stop', prefix='fa')
                    ).add_to(m)
                    
                    # Route colors
                    route_colors = {
                        1: '#10B981',
                        2: '#3B82F6',
                        3: '#8B5CF6',
                        4: '#F59E0B'
                    }
                    
                    # Add routes
                    for idx, route in enumerate(routes[:4]):
                        color = route_colors.get(route['rank'], '#6B7280')
                        
                        # Try to decode and draw polyline if available
                        if 'polyline' in route and route['polyline']:
                            try:
                                points = decode_polyline(route['polyline'])
                                if points:
                                    folium.PolyLine(
                                        points,
                                        color=color,
                                        weight=5 if route['rank'] == 1 else 3,
                                        opacity=0.8,
                                        popup=f"Route #{route['rank']}: {route['summary']}"
                                    ).add_to(m)
                            except:
                                pass
                        
                        # Add route info marker
                        popup_html = f"""
                        <div style="min-width: 280px; font-family: Inter; padding: 0.5rem;">
                            <h3 style="margin: 0 0 0.75rem 0; color: #111827; 
                                       border-bottom: 2px solid {color}; padding-bottom: 0.5rem;">
                                {'⭐ ' if route['rank'] == 1 else ''}Route #{route['rank']}
                            </h3>
                            <p style="margin: 0.5rem 0; font-weight: 600; color: #374151;">
                                📍 {route['summary']}
                            </p>
                            <div style="background: #F9FAFB; padding: 0.75rem; border-radius: 8px; margin: 0.75rem 0;">
                                <p style="margin: 0.25rem 0; color: #111827;"><strong>📏</strong> {route['distance_text']}</p>
                                <p style="margin: 0.25rem 0; color: #111827;"><strong>⏱️</strong> {route['duration_text']}</p>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                                <div style="text-align: center; padding: 0.5rem; background: #ECFDF5; border-radius: 6px;">
                                    <div style="font-size: 1.25rem; font-weight: bold; color: #047857;">
                                        {route['safety_score']:.0f}
                                    </div>
                                    <div style="font-size: 0.75rem; color: #065F46;">🛡️ Safety</div>
                                </div>
                                <div style="text-align: center; padding: 0.5rem; background: #EFF6FF; border-radius: 6px;">
                                    <div style="font-size: 1.25rem; font-weight: bold; color: #1E40AF;">
                                        {route['speed_score']:.0f}
                                    </div>
                                    <div style="font-size: 0.75rem; color: #1E3A8A;">⚡ Speed</div>
                                </div>
                                <div style="text-align: center; padding: 0.5rem; background: #F0FDF4; border-radius: 6px;">
                                    <div style="font-size: 1.25rem; font-weight: bold; color: #15803D;">
                                        {route['eco_score']:.0f}
                                    </div>
                                    <div style="font-size: 0.75rem; color: #166534;">🌱 Eco</div>
                                </div>
                                <div style="text-align: center; padding: 0.5rem; background: #F5F3FF; border-radius: 6px;">
                                    <div style="font-size: 1.25rem; font-weight: bold; color: #6D28D9;">
                                        {route['composite_score']:.0f}
                                    </div>
                                    <div style="font-size: 0.75rem; color: #5B21B6;">⭐ Overall</div>
                                </div>
                            </div>
                        </div>
                        """
                        
                        # Add marker offset for visibility
                        marker_lat = start_lat + (idx * 0.01)
                        marker_lng = start_lng + (idx * 0.01)
                        
                        folium.CircleMarker(
                            location=[marker_lat, marker_lng],
                            radius=12,
                            popup=folium.Popup(popup_html, max_width=320),
                            color=color,
                            fill=True,
                            fillColor=color,
                            fillOpacity=0.8,
                            weight=4
                        ).add_to(m)
                    
                    # Display map
                    st_folium(m, width=1200, height=650, returned_objects=[])
                    
                    st.markdown("""
                    <div class="info-box warning-box">
                        <strong>💡 Map Legend:</strong><br>
                        • 🟢 Green marker = Start location<br>
                        • 🔴 Red marker = Destination<br>
                        • Colored circles = Route information (click for details)<br>
                        • Route polylines shown if available from backend
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("💡 No routes found to display.")
            
            with tab3:
                st.markdown("### 📊 Analytics Dashboard")
                
                routes = result.get('routes', [])
                
                if routes:
                    fig = go.Figure()
                    route_names = [f"Route #{r['rank']}" for r in routes]
                    
                    fig.add_trace(go.Bar(
                        name='🛡️ Safety',
                        x=route_names,
                        y=[r['safety_score'] for r in routes],
                        marker_color='#10B981',
                        text=[f"{r['safety_score']:.0f}" for r in routes],
                        textposition='outside'
                    ))
                    
                    fig.add_trace(go.Bar(
                        name='⚡ Speed',
                        x=route_names,
                        y=[r['speed_score'] for r in routes],
                        marker_color='#3B82F6',
                        text=[f"{r['speed_score']:.0f}" for r in routes],
                        textposition='outside'
                    ))
                    
                    fig.add_trace(go.Bar(
                        name='🌱 Eco',
                        x=route_names,
                        y=[r['eco_score'] for r in routes],
                        marker_color='#34D399',
                        text=[f"{r['eco_score']:.0f}" for r in routes],
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        title={
                            'text': 'Route Performance Comparison',
                            'font': {'size': 22, 'family': 'Inter', 'color': '#111827'}
                        },
                        xaxis_title='Route',
                        yaxis_title='Score (0-100)',
                        barmode='group',
                        height=500,
                        font=dict(family='Inter', size=14),
                        plot_bgcolor='#F9FAFB',
                        paper_bgcolor='white',
                        yaxis=dict(range=[0, 110])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Metrics table
                    st.markdown("#### 📋 Detailed Metrics")
                    
                    metrics_data = []
                    for route in routes:
                        metrics_data.append({
                            'Rank': f"#{route['rank']}",
                            'Route': route['summary'][:50] + '...' if len(route['summary']) > 50 else route['summary'],
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
            
            with tab4:
                st.markdown("### 🤖 AI Insights")
                
                st.markdown("""
                <div class="info-box">
                    <strong>🧠 How Our AI Works</strong><br>
                    Our Random Forest model analyzes routes across 5 criteria: crime rate, traffic density, 
                    pollution level, street lighting, and carbon emissions.
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🔍 Analysis Criteria")
                    st.markdown("""
                    - **Crime Rate**: Delhi Police historical data
                    - **Street Lighting**: Municipal lighting database
                    - **Traffic Density**: Real-time traffic APIs
                    - **Pollution**: Air quality (PM2.5) sensors
                    - **Carbon**: Estimated CO₂ emissions
                    """)
                
                with col2:
                    st.markdown("#### ⚖️ Scoring Method")
                    st.markdown("""
                    - **Safety**: Crime (40%) + Lighting (35%) + Traffic (25%)
                    - **Speed**: Duration + Traffic conditions
                    - **Eco**: Pollution + Carbon emissions
                    - **Overall**: Weighted by your priority
                    """)
                
                st.markdown("---")
                
                if 'recommended' in result:
                    rec = result['recommended']
                    st.markdown("#### ⭐ Why This Route?")
                    
                    insights = []
                    
                    if rec['safety_score'] >= 70:
                        insights.append("✅ **High Safety**: Minimal crime, excellent lighting")
                    elif rec['safety_score'] >= 40:
                        insights.append("⚠️ **Moderate Safety**: Balances safety with other factors")
                    else:
                        insights.append("⚠️ **Lower Safety**: Consider alternatives if safety is critical")
                    
                    if rec['eco_score'] >= 70:
                        insights.append("🌱 **Eco-Friendly**: Low pollution, minimal carbon footprint")
                    
                    if rec['speed_score'] >= 70:
                        insights.append("⚡ **Fast Route**: Minimal traffic congestion")
                    
                    if rec.get('explanation'):
                        insights.append(f"💡 {rec['explanation']}")
                    
                    for insight in insights:
                        st.markdown(insight)

else:
    # Landing page
    st.markdown("""
    <div class="info-box">
        <strong>👋 Welcome to SafeRoute Delhi!</strong><br>
        Configure your route in the sidebar and click "Find Best Routes" to get AI-powered 
        recommendations based on safety, speed, and sustainability.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">Safety First</div>
            <div class="feature-text">
                Routes analyzed for:<br>
                • Crime statistics<br>
                • Street lighting quality<br>
                • Traffic safety<br>
                • Historical data
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🌱</div>
            <div class="feature-title">Eco-Friendly</div>
            <div class="feature-text">
                Environmental metrics:<br>
                • Air quality (PM2.5)<br>
                • Carbon emissions<br>
                • Traffic impact<br>
                • Green routes
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI-Powered</div>
            <div class="feature-text">
                Machine learning:<br>
                • Real-time prediction<br>
                • Multi-factor scoring<br>
                • Explainable insights<br>
                • Route optimization
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #374151; padding: 2rem 0; 
            background: linear-gradient(135deg, #F9FAFB 0%, #FFFFFF 100%); 
            border-radius: 12px;">
    <p style="margin: 0.5rem 0; font-weight: 700; font-size: 1.1rem; color: #111827;">
        🏆 SafeRoute Delhi - Sustainable & Safe Urban Mobility
    </p>
    <p style="margin: 0.5rem 0;">
        📊 Technology: Random Forest ML | Google Maps API | OpenAQ | Delhi Police Data
    </p>
    <p style="margin: 0.5rem 0;">
        🎯 Impact: UN SDG 11 (Sustainable Cities) & SDG 13 (Climate Action)
    </p>
</div>
""", unsafe_allow_html=True)
