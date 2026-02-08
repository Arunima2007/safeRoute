# streamlit_app.py
"""
SafeRoute Delhi - AI-Powered Sustainable and Safe Route Recommendation System
Aligned with SDG 11 & SDG 13
"""

import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

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

# Custom CSS based on the design system from documentation
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container */
    .main {
        background-color: #FFFFFF;
        color: #111827;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        text-align: center;
        margin: 1.5rem 0 0.5rem 0;
        line-height: 1.2;
    }
    
    .subtitle {
        text-align: center;
        color: #6B7280;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    .sdg-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 1rem 0 2rem 0;
    }
    
    .sdg-badge {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .sdg-11 {
        background-color: #F59E0B;
        color: white;
    }
    
    .sdg-13 {
        background-color: #059669;
        color: white;
    }
    
    /* Route cards */
    .route-card {
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #E5E7EB;
        margin: 1rem 0;
        background: #F9FAFB;
        transition: all 0.2s ease;
    }
    
    .route-card:hover {
        border-color: #D1D5DB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .route-card.recommended {
        border: 3px solid #10B981;
        background: linear-gradient(to bottom, #ECFDF5, #F9FAFB);
    }
    
    .route-type-badge {
        display: inline-block;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.75rem;
        color: white;
    }
    
    .badge-safest { background: #10B981; }
    .badge-eco { background: #34D399; }
    .badge-fastest { background: #3B82F6; }
    .badge-balanced { background: #8B5CF6; }
    
    /* Score visualizer */
    .score-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.25rem;
        margin: 0.5rem;
        color: white;
    }
    
    .score-excellent { background: #10B981; }
    .score-good { background: #84CC16; }
    .score-moderate { background: #F59E0B; }
    .score-poor { background: #F97316; }
    .score-critical { background: #EF4444; }
    
    /* Carbon badge */
    .carbon-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.5rem 0;
    }
    
    .carbon-low { 
        background: #ECFDF5;
        color: #059669;
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
    
    /* Feature highlights */
    .feature-box {
        padding: 1.5rem;
        border-radius: 12px;
        background: #F9FAFB;
        border: 2px solid #E5E7EB;
        height: 100%;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.75rem;
    }
    
    .feature-text {
        font-size: 0.95rem;
        color: #4B5563;
        line-height: 1.6;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #F9FAFB;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #059669;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        border: none;
        transition: background-color 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #047857;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: #111827;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: #6B7280;
        font-weight: 500;
    }
    
    /* Info boxes */
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #ECFDF5;
        border-left-color: #10B981;
    }
    
    .warning-box {
        background-color: #FFFBEB;
        border-left-color: #F59E0B;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #E5E7EB;
    }
    
    /* Risk indicator */
    .risk-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.5rem 0;
    }
    
    .risk-safe {
        background: #ECFDF5;
        color: #065F46;
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
</style>
""", unsafe_allow_html=True)

# Header with SDG alignment
st.markdown('<div class="main-header">🛡️ SafeRoute Delhi</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Smart Route Navigation for Safety, Speed & Sustainability</div>', unsafe_allow_html=True)
st.markdown('''
<div class="sdg-badges">
    <span class="sdg-badge sdg-11">SDG 11: Sustainable Cities</span>
    <span class="sdg-badge sdg-13">SDG 13: Climate Action</span>
</div>
''', unsafe_allow_html=True)

# Sidebar - Route Settings
with st.sidebar:
    st.markdown("### ⚙️ Route Settings")
    
    # Popular locations for quick selection
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
    
    # Origin selection
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
    
    # Destination selection
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
    
    # Preference mode
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
    
    # API endpoint
    api_url = st.text_input(
        "API Endpoint", 
        "http://127.0.0.1:5000/api/compare-routes",
        help="Backend API URL"
    )
    
    st.markdown("---")
    
    # Find Routes button
    if st.button("🔍 Find Best Routes", type="primary", use_container_width=True):
        st.session_state.show_results = True
        st.session_state.api_result = None
        st.rerun()
    
    # Info section
    st.markdown("---")
    st.markdown("#### 💡 About")
    st.caption("This platform uses AI to analyze routes across safety, sustainability, and efficiency metrics.")
    st.caption(f"Last updated: {datetime.now().strftime('%B %Y')}")

# Main content area
if st.session_state.show_results:
    if not origin or not destination:
        st.error("⚠️ Please enter both origin and destination")
    else:
        # Fetch data if not already fetched
        if st.session_state.api_result is None:
            with st.spinner("🔄 Analyzing routes with AI... Please wait."):
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
                        st.error(f"❌ API Error: {response.status_code}")
                        try:
                            st.json(response.json())
                        except:
                            st.text(response.text)
                        st.stop()
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the Flask server is running on the configured endpoint.")
                    st.info("💡 Start your backend server with: `python route_server.py`")
                    st.stop()
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The server took too long to respond.")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    with st.expander("See error details"):
                        import traceback
                        st.code(traceback.format_exc())
                    st.stop()
        
        # Display results if available
        if st.session_state.api_result is not None:
            result = st.session_state.api_result
            
            # Success message
            st.markdown(f"""
            <div class="info-box success-box">
                <strong>✅ Analysis Complete!</strong><br>
                Found {result.get('total_routes', 0)} route options based on your preferences.
            </div>
            """, unsafe_allow_html=True)
            
            # Summary metrics
            if 'summary' in result:
                st.markdown("### 📊 Route Comparison Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "🛡️ Safety Range",
                        result['summary']['score_range']['safety']
                    )
                    st.caption(f"Safest: {result['summary']['safest_route']}")
                
                with col2:
                    st.metric(
                        "⚡ Speed Range",
                        result['summary']['score_range']['speed']
                    )
                    st.caption(f"Fastest: {result['summary']['fastest_route']}")
                
                with col3:
                    st.metric(
                        "🌱 Eco Range",
                        result['summary']['score_range']['eco']
                    )
                    st.caption(f"Greenest: {result['summary']['greenest_route']}")
                
                with col4:
                    if 'recommended' in result:
                        st.metric(
                            "⭐ Recommended",
                            f"#{result['recommended']['rank']}"
                        )
                        st.caption(result['recommended'].get('summary', 'Best match'))
                
                st.markdown("---")
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Route Details",
                "🗺️ Map View", 
                "📊 Analytics",
                "🤖 AI Insights"
            ])
            
            with tab1:
                st.markdown("### 📋 Detailed Route Comparison")
                
                routes = result.get('routes', [])
                
                # Display each route
                for route in routes:
                    is_recommended = route['rank'] == 1
                    
                    # Determine route type badge
                    route_summary = route['summary'].lower()
                    if 'safe' in route_summary or route.get('type') == 'safety':
                        badge_class = 'badge-safest'
                        badge_text = '🛡️ SAFEST ROUTE'
                    elif 'eco' in route_summary or 'green' in route_summary:
                        badge_class = 'badge-eco'
                        badge_text = '🌱 ECO-FRIENDLY'
                    elif 'fast' in route_summary or 'quick' in route_summary:
                        badge_class = 'badge-fastest'
                        badge_text = '⚡ FASTEST'
                    else:
                        badge_class = 'badge-balanced'
                        badge_text = '⚖️ BALANCED'
                    
                    with st.container():
                        # Route header
                        if is_recommended:
                            st.markdown("#### ⭐ RECOMMENDED ROUTE")
                        else:
                            st.markdown(f"#### Route #{route['rank']}")
                        
                        # Route badge
                        st.markdown(f'<span class="route-type-badge {badge_class}">{badge_text}</span>', 
                                  unsafe_allow_html=True)
                        
                        # Basic info
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
                        
                        st.markdown("#### Score Breakdown")
                        
                        col1, col2, col3 = st.columns(3)
                        
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
                        
                        with col1:
                            score_class = get_score_class(route['safety_score'])
                            st.markdown(f"""
                            <div style="text-align: center">
                                <h4>🛡️ Safety Score</h4>
                                <div class="score-circle {score_class}">
                                    {route['safety_score']:.0f}
                                </div>
                                <p style="margin-top: 0.5rem; color: #6B7280; font-size: 0.875rem;">
                                    {get_score_label(route['safety_score'])}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'avg_crime' in route:
                                st.caption(f"Crime Index: {route['avg_crime']:.2f}")
                            if 'avg_lighting' in route:
                                st.caption(f"Lighting Quality: {route['avg_lighting']:.2f}")
                        
                        with col2:
                            score_class = get_score_class(route['speed_score'])
                            st.markdown(f"""
                            <div style="text-align: center">
                                <h4>⚡ Speed Score</h4>
                                <div class="score-circle {score_class}">
                                    {route['speed_score']:.0f}
                                </div>
                                <p style="margin-top: 0.5rem; color: #6B7280; font-size: 0.875rem;">
                                    {get_score_label(route['speed_score'])}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'avg_traffic' in route:
                                st.caption(f"Traffic Density: {route['avg_traffic']:.2f}")
                        
                        with col3:
                            score_class = get_score_class(route['eco_score'])
                            st.markdown(f"""
                            <div style="text-align: center">
                                <h4>🌱 Eco Score</h4>
                                <div class="score-circle {score_class}">
                                    {route['eco_score']:.0f}
                                </div>
                                <p style="margin-top: 0.5rem; color: #6B7280; font-size: 0.875rem;">
                                    {get_score_label(route['eco_score'])}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'avg_pollution' in route:
                                st.caption(f"Pollution Level: {route['avg_pollution']:.2f}")
                        
                        # Carbon footprint badge
                        if 'avg_carbon' in route:
                            carbon = route['avg_carbon']
                            if carbon < 1:
                                carbon_class = 'carbon-low'
                                carbon_label = 'Low Carbon Footprint'
                            elif carbon < 3:
                                carbon_class = 'carbon-medium'
                                carbon_label = 'Medium Carbon Footprint'
                            else:
                                carbon_class = 'carbon-high'
                                carbon_label = 'High Carbon Footprint'
                            
                            st.markdown(f"""
                            <div style="margin-top: 1rem;">
                                <span class="carbon-badge {carbon_class}">
                                    🌍 {carbon_label}: {carbon:.2f} kg CO₂
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Risk assessment
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
                                {risk_emoji} Risk Level: {risk_name}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
            
            with tab2:
                st.markdown("### 🗺️ Interactive Route Map")
                
                routes = result.get('routes', [])
                
                if routes:
                    # Create map centered on Delhi
                    m = folium.Map(
                        location=[28.6139, 77.2090],
                        zoom_start=11,
                        tiles='OpenStreetMap'
                    )
                    
                    # Add markers
                    folium.Marker(
                        [28.6139, 77.2090],
                        popup=f"<b>📍 Start</b><br>{origin}",
                        icon=folium.Icon(color='blue', icon='play', prefix='fa')
                    ).add_to(m)
                    
                    folium.Marker(
                        [28.6139, 77.2090],
                        popup=f"<b>🎯 Destination</b><br>{destination}",
                        icon=folium.Icon(color='red', icon='stop', prefix='fa')
                    ).add_to(m)
                    
                    # Route colors matching design system
                    route_colors = {
                        1: '#10B981',  # Green - Recommended
                        2: '#3B82F6',  # Blue
                        3: '#8B5CF6',  # Purple
                        4: '#F59E0B'   # Amber
                    }
                    
                    # Add route information
                    for idx, route in enumerate(routes[:4]):
                        color = route_colors.get(route['rank'], '#6B7280')
                        
                        popup_html = f"""
                        <div style="min-width: 250px; font-family: Inter, sans-serif;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #111827;">
                                {'⭐ ' if route['rank'] == 1 else ''}Route #{route['rank']}
                            </h4>
                            <p style="margin: 0.25rem 0;"><b>📍</b> {route['summary']}</p>
                            <p style="margin: 0.25rem 0;"><b>📏</b> {route['distance_text']}</p>
                            <p style="margin: 0.25rem 0;"><b>⏱️</b> {route['duration_text']}</p>
                            <hr style="margin: 0.5rem 0;">
                            <p style="margin: 0.25rem 0;"><b>🛡️ Safety:</b> {route['safety_score']:.0f}/100</p>
                            <p style="margin: 0.25rem 0;"><b>⚡ Speed:</b> {route['speed_score']:.0f}/100</p>
                            <p style="margin: 0.25rem 0;"><b>🌱 Eco:</b> {route['eco_score']:.0f}/100</p>
                            <p style="margin: 0.25rem 0;"><b>⭐ Overall:</b> {route['composite_score']:.0f}/100</p>
                        </div>
                        """
                        
                        # Add a circle marker for route indicator
                        folium.CircleMarker(
                            location=[28.6139 + (idx * 0.01), 77.2090 + (idx * 0.01)],
                            radius=10,
                            popup=folium.Popup(popup_html, max_width=300),
                            color=color,
                            fill=True,
                            fillColor=color,
                            fillOpacity=0.7,
                            weight=3
                        ).add_to(m)
                    
                    # Display map
                    st_folium(m, width=1200, height=600, returned_objects=[])
                    
                    st.info("💡 **Note**: Full route polylines require Google Maps API integration. Currently showing route markers and information.")
                else:
                    st.info("💡 No routes found to display on map.")
            
            with tab3:
                st.markdown("### 📊 Route Analytics Dashboard")
                
                routes = result.get('routes', [])
                
                if routes:
                    # Score comparison chart
                    fig = go.Figure()
                    
                    route_names = [f"Route #{r['rank']}: {r['summary'][:30]}..." if len(r['summary']) > 30 
                                 else f"Route #{r['rank']}: {r['summary']}" for r in routes]
                    
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
                            'text': 'Multi-Criteria Route Score Comparison',
                            'font': {'size': 20, 'family': 'Inter', 'color': '#111827'}
                        },
                        xaxis_title='Route',
                        yaxis_title='Score (0-100)',
                        barmode='group',
                        height=500,
                        font=dict(family='Inter', size=14),
                        plot_bgcolor='#F9FAFB',
                        paper_bgcolor='white',
                        yaxis=dict(range=[0, 105])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Radar chart for recommended route
                    if 'recommended' in result:
                        st.markdown("#### 🎯 Recommended Route Profile")
                        
                        recommended = result['recommended']
                        
                        categories = ['Safety', 'Speed', 'Eco', 'Overall']
                        values = [
                            recommended['safety_score'],
                            recommended['speed_score'],
                            recommended['eco_score'],
                            recommended['composite_score']
                        ]
                        
                        fig_radar = go.Figure()
                        
                        fig_radar.add_trace(go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name=recommended['summary'],
                            marker=dict(color='#8B5CF6'),
                            line=dict(color='#8B5CF6', width=2)
                        ))
                        
                        fig_radar.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100],
                                    tickfont=dict(size=12)
                                ),
                                bgcolor='#F9FAFB'
                            ),
                            showlegend=True,
                            height=450,
                            font=dict(family='Inter', size=14),
                            paper_bgcolor='white'
                        )
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.plotly_chart(fig_radar, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### 📈 Key Metrics")
                            st.metric("Safety Score", f"{recommended['safety_score']:.0f}/100")
                            st.metric("Speed Score", f"{recommended['speed_score']:.0f}/100")
                            st.metric("Eco Score", f"{recommended['eco_score']:.0f}/100")
                            st.metric("Overall Score", f"{recommended['composite_score']:.0f}/100")
                            
                            if 'risk_name' in recommended:
                                st.markdown(f"**Risk Level:** {recommended['risk_name']}")
                    
                    # Detailed metrics table
                    st.markdown("#### 📋 Detailed Metrics Table")
                    
                    metrics_data = []
                    for route in routes:
                        metrics_data.append({
                            'Rank': f"#{route['rank']}",
                            'Route': route['summary'][:40] + '...' if len(route['summary']) > 40 else route['summary'],
                            'Distance': route['distance_text'],
                            'Duration': route['duration_text'],
                            'Safety': f"{route['safety_score']:.0f}/100",
                            'Speed': f"{route['speed_score']:.0f}/100",
                            'Eco': f"{route['eco_score']:.0f}/100",
                            'Overall': f"{route['composite_score']:.0f}/100",
                            'Risk': route.get('risk_name', 'N/A')
                        })
                    
                    df = pd.DataFrame(metrics_data)
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )
            
            with tab4:
                st.markdown("### 🤖 Explainable AI Insights")
                
                st.markdown("""
                <div class="info-box">
                    <strong>🧠 How Our AI Works</strong><br>
                    Our machine learning model analyzes routes across five critical dimensions to provide 
                    transparent, trustworthy recommendations aligned with your priorities.
                </div>
                """, unsafe_allow_html=True)
                
                # Analysis criteria
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🔍 Analysis Criteria")
                    st.markdown("""
                    - **Crime Rate**: Historical crime data from Delhi Police
                    - **Street Lighting**: Municipal lighting quality data
                    - **Traffic Density**: Real-time traffic conditions
                    - **Pollution Level**: Air quality (PM2.5) measurements
                    - **Carbon Emissions**: Estimated CO₂ per route
                    """)
                
                with col2:
                    st.markdown("#### ⚖️ Scoring Methodology")
                    st.markdown("""
                    - **Safety Score**: Crime rate (40%) + Lighting (35%) + Traffic (25%)
                    - **Speed Score**: Duration + Traffic conditions
                    - **Eco Score**: Pollution levels + Carbon emissions
                    - **Overall**: Weighted by your selected priority
                    """)
                
                st.markdown("---")
                
                # Recommended route insights
                if 'recommended' in result:
                    recommended = result['recommended']
                    
                    st.markdown("#### ⭐ Why This Route Was Recommended")
                    
                    # Generate AI insights based on scores
                    insights = []
                    
                    if recommended['safety_score'] >= 70:
                        insights.append("✅ **High Safety Score**: This route has minimal crime incidents and excellent street lighting.")
                    elif recommended['safety_score'] >= 40:
                        insights.append("⚠️ **Moderate Safety**: This route balances safety with other priorities.")
                    else:
                        insights.append("⚠️ **Lower Safety Score**: Consider alternative routes if safety is your primary concern.")
                    
                    if recommended['eco_score'] >= 70:
                        insights.append("🌱 **Eco-Friendly**: Low pollution levels and minimal carbon footprint.")
                    
                    if recommended['speed_score'] >= 70:
                        insights.append("⚡ **Fast Route**: Minimal traffic congestion expected.")
                    
                    if recommended.get('explanation'):
                        insights.append(f"💡 **Recommendation**: {recommended['explanation']}")
                    
                    for insight in insights:
                        st.markdown(insight)
                    
                    st.markdown("---")
                
                # Tradeoffs analysis
                st.markdown("#### ⚖️ Route Tradeoffs")
                
                routes = result.get('routes', [])
                if len(routes) >= 2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        safest = max(routes, key=lambda x: x['safety_score'])
                        st.markdown("**🛡️ Safest Route**")
                        st.info(f"{safest['summary']}")
                        st.caption(f"Safety: {safest['safety_score']:.0f}/100 | Duration: {safest['duration_text']}")
                    
                    with col2:
                        fastest = max(routes, key=lambda x: x['speed_score'])
                        st.markdown("**⚡ Fastest Route**")
                        st.info(f"{fastest['summary']}")
                        st.caption(f"Speed: {fastest['speed_score']:.0f}/100 | Duration: {fastest['duration_text']}")
                
                st.markdown("---")
                
                # Data sources
                st.markdown("#### 📊 Data Sources & Transparency")
                st.markdown("""
                Our AI model uses reliable, real-time data sources:
                
                - **Crime Data**: Delhi Police public records and incident reports
                - **Lighting Data**: Municipal Corporation lighting infrastructure database  
                - **Traffic**: Real-time traffic APIs and historical patterns
                - **Air Quality**: OpenAQ and government monitoring stations
                - **Carbon Estimates**: Standard vehicle emission factors
                
                *Last model training: February 2026*
                """)

else:
    # Landing page - Show welcome screen
    st.markdown("""
    <div class="info-box">
        <strong>👋 Welcome to SafeRoute Delhi!</strong><br>
        Configure your route settings in the sidebar and click "Find Best Routes" to get AI-powered 
        recommendations that prioritize your safety, speed, and environmental impact.
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
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
                • Traffic conditions<br>
                • Historical safety data
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
                • Traffic congestion<br>
                • Green route options
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI-Powered</div>
            <div class="feature-text">
                Machine learning features:<br>
                • Real-time risk prediction<br>
                • Multi-factor scoring<br>
                • Explainable AI insights<br>
                • Route optimization
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # How it works
    st.markdown("### 🔄 How It Works")
    
    step1, step2, step3, step4 = st.columns(4)
    
    with step1:
        st.markdown("""
        **1️⃣ Input**  
        Enter your start and end locations
        """)
    
    with step2:
        st.markdown("""
        **2️⃣ Analyze**  
        AI evaluates multiple routes across 5 criteria
        """)
    
    with step3:
        st.markdown("""
        **3️⃣ Compare**  
        View ranked options with detailed scores
        """)
    
    with step4:
        st.markdown("""
        **4️⃣ Choose**  
        Select the route that matches your priority
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.875rem; padding: 1rem 0;">
    <p style="margin: 0.25rem 0;"><strong>🏆 Built for LeanIn Hackathon | Powered by AI & Real-time Data</strong></p>
    <p style="margin: 0.25rem 0;">📊 Using: Random Forest ML | Google Maps API | OpenAQ | Delhi Police Data</p>
    <p style="margin: 0.25rem 0;">🎯 Aligned with UN SDG 11 (Sustainable Cities) & SDG 13 (Climate Action)</p>
    <p style="margin: 0.25rem 0; margin-top: 0.5rem;">Version 1.0 | February 2026</p>
</div>
""", unsafe_allow_html=True)