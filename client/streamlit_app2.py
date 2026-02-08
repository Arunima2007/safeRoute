# streamlit_app.py

import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import polyline
import webbrowser

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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .route-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
        background: white;
    }
    .recommended {
        border: 3px solid #4CAF50;
        background: #f1f8f4;
    }
    .metric-row {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    .score-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        color: white;
    }
    .score-high { background: #4CAF50; }
    .score-medium { background: #FF9800; }
    .score-low { background: #f44336; }
    .transport-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    .transport-metro { background: #9C27B0; color: white; }
    .transport-bus { background: #FF9800; color: white; }
    .transport-car { background: #2196F3; color: white; }
    .transport-walk { background: #4CAF50; color: white; }
    .transport-bike { background: #FF5722; color: white; }
</style>
""", unsafe_allow_html=True)

# Helper function to determine transport recommendations
def get_transport_recommendations(distance_km, duration_mins, traffic_level=None):
    """
    Recommends transport modes based on distance and duration
    """
    recommendations = []
    
    # Distance in km
    if distance_km <= 2:
        recommendations.append({
            'mode': '🚶 Walk',
            'reason': 'Short distance, good for health',
            'badge_class': 'transport-walk',
            'priority': 1
        })
    
    if distance_km <= 5:
        recommendations.append({
            'mode': '🚴 Bike/E-Scooter',
            'reason': 'Eco-friendly, avoid traffic',
            'badge_class': 'transport-bike',
            'priority': 2
        })
    
    if distance_km >= 3 and distance_km <= 30:
        recommendations.append({
            'mode': '🚇 Metro',
            'reason': 'Fast, reliable, eco-friendly',
            'badge_class': 'transport-metro',
            'priority': 1
        })
    
    if distance_km >= 2:
        recommendations.append({
            'mode': '🚌 Bus',
            'reason': 'Affordable public transport',
            'badge_class': 'transport-bus',
            'priority': 3
        })
    
    if distance_km >= 5 or duration_mins >= 30:
        recommendations.append({
            'mode': '🚗 Car/Taxi',
            'reason': 'Convenient for longer distances',
            'badge_class': 'transport-car',
            'priority': 2 if traffic_level and traffic_level > 0.7 else 1
        })
    
    # Sort by priority
    recommendations.sort(key=lambda x: x['priority'])
    
    return recommendations

# Header
st.markdown('<div class="main-header">🛡️ SafeRoute Delhi</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Smart Route Navigation for Safety, Speed & Sustainability</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Route Settings")
    
    # Popular locations for quick selection
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
    origin_preset = st.selectbox("Quick Select Origin", list(popular_locations.keys()), index=0)
    
    if origin_preset == "Custom":
        origin = st.text_input("Enter origin address", "Connaught Place, Delhi")
    else:
        origin = popular_locations[origin_preset]
        st.text(f"📌 {origin}")
    
    # Destination selection
    st.subheader("🎯 Destination")
    dest_preset = st.selectbox("Quick Select Destination", list(popular_locations.keys()), index=2)
    
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
        format_func=lambda x: preference_icons[x]
    )
    
    # API endpoint
    api_url = st.text_input("API Endpoint", "http://127.0.0.1:5000/api/compare-routes")
    
    # Find Routes button
    if st.button("🔍 Find Best Routes", type="primary", use_container_width=True):
        st.session_state.show_results = True
        st.session_state.api_result = None  # Reset to fetch new data

# Helper function for score colors
def get_score_class(score):
    if score >= 70:
        return "score-high"
    elif score >= 40:
        return "score-medium"
    else:
        return "score-low"

# Main content area
if st.session_state.show_results:
    if not origin or not destination:
        st.error("⚠️ Please enter both origin and destination")
    else:
        if st.session_state.api_result is None:
            with st.spinner("🔄 Analyzing routes with AI..."):
                try:
                    # Make API request
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
        
        # Display results
        result = st.session_state.api_result
        
        # Success message
        st.success(f"✅ Found {result['total_routes']} route options!")
        
        # Transport Recommendations Section
        st.subheader("🚆 Recommended Transport Modes")
        
        # Get distance from recommended route
        recommended = result['recommended']
        distance_text = recommended.get('distance_text', '0 km')
        duration_text = recommended.get('duration_text', '0 mins')
        
        # Extract numeric values
        try:
            distance_km = float(distance_text.split()[0])
        except:
            distance_km = 10  # default
        
        try:
            duration_mins = float(duration_text.split()[0])
        except:
            duration_mins = 30  # default
        
        traffic_level = recommended.get('avg_traffic', 0.5)
        
        # Get transport recommendations
        transport_recs = get_transport_recommendations(distance_km, duration_mins, traffic_level)
        
        # Display transport recommendations in a nice format
        st.markdown("**Based on your route distance and conditions:**")
        
        cols = st.columns(len(transport_recs))
        for idx, rec in enumerate(transport_recs):
            with cols[idx]:
                priority_emoji = "⭐" if rec['priority'] == 1 else "✓"
                st.markdown(f"""
                <div class="transport-badge {rec['badge_class']}">
                    {priority_emoji} {rec['mode']}
                </div>
                <p style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
                    {rec['reason']}
                </p>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Summary metrics
        if 'summary' in result:
            st.subheader("📊 Route Comparison Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🛡️ Safety Range",
                    result['summary']['score_range']['safety'],
                    delta=None
                )
                st.caption(f"Safest: {result['summary']['safest_route']}")
            
            with col2:
                st.metric(
                    "⚡ Speed Range",
                    result['summary']['score_range']['speed'],
                    delta=None
                )
                st.caption(f"Fastest: {result['summary']['fastest_route']}")
            
            with col3:
                st.metric(
                    "🌱 Eco Range",
                    result['summary']['score_range']['eco'],
                    delta=None
                )
                st.caption(f"Greenest: {result['summary']['greenest_route']}")
            
            st.divider()
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📋 Route Details", "📊 Analytics"])
        
        with tab1:
            st.subheader("🗺️ Interactive Route Map")
            
            # Create map centered on routes
            routes = result['routes']
            
            # Get center point
            if routes and 'polyline' in routes[0]:
                first_route_coords = polyline.decode(routes[0]['polyline'])
                center_lat = sum(coord[0] for coord in first_route_coords) / len(first_route_coords)
                center_lng = sum(coord[1] for coord in first_route_coords) / len(first_route_coords)
            else:
                center_lat, center_lng = 28.6139, 77.2090  # Delhi center
            
            # Create folium map
            m = folium.Map(
                location=[center_lat, center_lng],
                zoom_start=12,
                tiles='OpenStreetMap'
            )
            
            # Color scheme for routes
            colors = ['green', 'blue', 'red', 'orange', 'purple']
            
            # Add routes to map
            for idx, route in enumerate(routes):
                if 'polyline' in route:
                    coords = polyline.decode(route['polyline'])
                    
                    # Determine color based on ranking
                    color = colors[min(idx, len(colors)-1)]
                    if route.get('is_recommended', False):
                        color = 'green'
                        weight = 6
                    else:
                        weight = 4
                    
                    # Add polyline
                    folium.PolyLine(
                        coords,
                        color=color,
                        weight=weight,
                        opacity=0.8,
                        popup=f"{route['summary']}<br>Safety: {route['safety_score']:.0f}<br>Speed: {route['speed_score']:.0f}",
                    ).add_to(m)
                    
                    # Add markers for start and end
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
            
            # Display map
            st_folium(m, width=None, height=500)
            
            # Google Maps Navigation Button
            st.markdown("### 🗺️ Open in Google Maps")
            
            # Create Google Maps URL
            google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"
            
            st.markdown(f"""
            <a href="{google_maps_url}" target="_blank">
                <button style="
                    background-color: #4285F4;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <span>🗺️</span> Navigate with Google Maps
                </button>
            </a>
            """, unsafe_allow_html=True)
            
            st.caption(f"From: {origin} → To: {destination}")
        
        with tab2:
            st.subheader("📋 Detailed Route Information")
            
            routes = result['routes']
            
            for idx, route in enumerate(routes):
                # Determine if recommended
                is_recommended = route.get('is_recommended', False)
                card_class = "route-card recommended" if is_recommended else "route-card"
                
                # Create route card
                with st.container():
                    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                    
                    # Header
                    col_header1, col_header2 = st.columns([3, 1])
                    with col_header1:
                        rec_badge = "⭐ **RECOMMENDED**" if is_recommended else ""
                        st.markdown(f"### {route['summary']} {rec_badge}")
                        st.markdown(f"**Rank:** #{route['rank']} | **Overall Score:** {route['composite_score']:.0f}/100")
                    
                    with col_header2:
                        # Individual Google Maps button for each route
                        if 'polyline' in route:
                            route_coords = polyline.decode(route['polyline'])
                            # Get waypoints for more accurate route
                            waypoints_str = ""
                            if len(route_coords) > 2:
                                # Sample some intermediate points
                                sample_points = route_coords[len(route_coords)//3:len(route_coords)*2//3:len(route_coords)//6]
                                waypoints = "|".join([f"{lat},{lng}" for lat, lng in sample_points[:3]])
                                if waypoints:
                                    waypoints_str = f"&waypoints={waypoints}"
                            
                            route_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}{waypoints_str}&travelmode=driving"
                            
                            st.markdown(f"""
                            <a href="{route_maps_url}" target="_blank">
                                <button style="
                                    background-color: #34A853;
                                    color: white;
                                    padding: 8px 16px;
                                    border: none;
                                    border-radius: 5px;
                                    font-size: 14px;
                                    cursor: pointer;
                                ">
                                    🗺️ Navigate
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
                    
                    # Basic info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**📏 Distance:** {route['distance_text']}")
                    with col2:
                        st.markdown(f"**⏱️ Duration:** {route['duration_text']}")
                    
                    st.divider()
                    
                    # Scores
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        score_class = get_score_class(route['safety_score'])
                        st.markdown(f"""
                        <div style="text-align: center">
                            <h3>🛡️ Safety</h3>
                            <span class="score-badge {score_class}">
                                {route['safety_score']:.0f}/100
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if 'avg_crime' in route:
                            st.caption(f"Crime: {route['avg_crime']:.2f}")
                        if 'avg_lighting' in route:
                            st.caption(f"Lighting: {route['avg_lighting']:.2f}")
                    
                    with col2:
                        score_class = get_score_class(route['speed_score'])
                        st.markdown(f"""
                        <div style="text-align: center">
                            <h3>⚡ Speed</h3>
                            <span class="score-badge {score_class}">
                                {route['speed_score']:.0f}/100
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if 'avg_traffic' in route:
                            st.caption(f"Traffic: {route['avg_traffic']:.2f}")
                    
                    with col3:
                        score_class = get_score_class(route['eco_score'])
                        st.markdown(f"""
                        <div style="text-align: center">
                            <h3>🌱 Eco</h3>
                            <span class="score-badge {score_class}">
                                {route['eco_score']:.0f}/100
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if 'avg_pollution' in route:
                            st.caption(f"Pollution: {route['avg_pollution']:.2f}")
                        if 'avg_carbon' in route:
                            st.caption(f"Carbon: {route['avg_carbon']:.2f}")
                    
                    # Risk assessment
                    if 'risk_name' in route:
                        risk_emoji = {'Safe': '🟢', 'Moderate': '🟡', 'Risky': '🔴'}
                        st.markdown(f"""
                        **Risk Level:** {risk_emoji.get(route['risk_name'], '⚪')} {route['risk_name']}
                        """)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.divider()
        
        with tab3:
            st.subheader("📊 Route Analytics")
            
            # Create comparison chart
            routes = result['routes']
            
            fig = go.Figure()
            
            # Add bars for each metric
            fig.add_trace(go.Bar(
                name='Safety',
                x=[r['summary'] for r in routes],
                y=[r['safety_score'] for r in routes],
                marker_color='#4CAF50'
            ))
            
            fig.add_trace(go.Bar(
                name='Speed',
                x=[r['summary'] for r in routes],
                y=[r['speed_score'] for r in routes],
                marker_color='#2196F3'
            ))
            
            fig.add_trace(go.Bar(
                name='Eco',
                x=[r['summary'] for r in routes],
                y=[r['eco_score'] for r in routes],
                marker_color='#8BC34A'
            ))
            
            fig.update_layout(
                title='Route Score Comparison',
                xaxis_title='Route',
                yaxis_title='Score (0-100)',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Radar chart for recommended route
            st.subheader("🎯 Recommended Route Profile")
            
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
                name=recommended['summary']
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
            
            # Detailed metrics table
            st.subheader("📈 Detailed Metrics")
            
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
            st.dataframe(df, use_container_width=True)

else:
    # Show welcome screen
    st.info("👆 Configure your route settings in the sidebar and click 'Find Best Routes' to get started!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🛡️ Safety First
        Routes analyzed for:
        - Crime statistics
        - Street lighting
        - Traffic conditions
        - Historical safety data
        """)
    
    with col2:
        st.markdown("""
        ### 🌱 Eco-Friendly
        Environmental metrics:
        - Air quality (PM2.5)
        - Carbon emissions
        - Traffic congestion
        - Green route options
        """)
    
    with col3:
        st.markdown("""
        ### 🤖 AI-Powered
        Machine learning features:
        - Real-time risk prediction
        - Multi-factor scoring
        - Explainable AI insights
        - Route optimization
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🏆 Built for LeanIn Hackathon | Powered by AI & Real-time Data</p>
    <p>📊 Using: Random Forest ML | Google Maps API | OpenAQ | Delhi Police Data</p>
</div>
""", unsafe_allow_html=True)
