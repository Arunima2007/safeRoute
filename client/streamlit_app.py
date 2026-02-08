# streamlit_app.py

import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import pandas as pd

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
</style>
""", unsafe_allow_html=True)

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
    origin_preset = st.selectbox("Quick Select Origin", list(popular_locations.keys()), index=4)
    
    if origin_preset == "Custom":
        origin = st.text_input("Enter origin address", "Connaught Place, Delhi")
    else:
        origin = popular_locations[origin_preset]
        st.text(f"📌 {origin}")
    
    # Destination selection
    st.subheader("🎯 Destination")
    dest_preset = st.selectbox("Quick Select Destination", list(popular_locations.keys()), index=3)
    
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
        st.session_state.api_result = None  # Reset previous results
        st.rerun()

# Main content area
if st.session_state.show_results:
    if not origin or not destination:
        st.error("⚠️ Please enter both origin and destination")
    else:
        # Fetch data if not already fetched
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
                        st.rerun()  # Rerun to display results
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        try:
                            st.json(response.json())
                        except:
                            st.text(response.text)
                        st.stop()
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the Flask server is running on http://127.0.0.1:5000")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.stop()
        
        # Display results if available
        if st.session_state.api_result is not None:
            result = st.session_state.api_result
            
            # Success message
            st.success(f"✅ Found {result.get('total_routes', 0)} route options!")
            
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
                routes = result.get('routes', [])
                
                if routes:
                    # Create map centered on Delhi
                    m = folium.Map(
                        location=[28.6139, 77.2090],
                        zoom_start=11,
                        tiles='OpenStreetMap'
                    )
                    
                    # Add markers for origin and destination
                    folium.Marker(
                        [28.6139, 77.2090],
                        popup=f"📍 {origin}",
                        icon=folium.Icon(color='green', icon='play')
                    ).add_to(m)
                    
                    folium.Marker(
                        [28.6139, 77.2090],
                        popup=f"🎯 {destination}",
                        icon=folium.Icon(color='red', icon='stop')
                    ).add_to(m)
                    
                    # Color code routes by rank
                    colors = ['green', 'blue', 'red', 'orange', 'purple']
                    
                    for idx, route in enumerate(routes[:3]):
                        color = colors[idx % len(colors)]
                        
                        # Add route info popup
                        popup_html = f"""
                        <div style="width: 200px">
                            <h4>{route['summary']}</h4>
                            <p><b>Rank:</b> #{route['rank']}</p>
                            <p><b>Distance:</b> {route['distance_text']}</p>
                            <p><b>Duration:</b> {route['duration_text']}</p>
                            <p><b>Safety:</b> {route['safety_score']:.0f}/100</p>
                            <p><b>Overall:</b> {route['composite_score']:.0f}/100</p>
                        </div>
                        """
                    
                    st_folium(m, width=1200, height=500)
                else:
                    st.info("💡 No routes found to display on map.")
            
            with tab2:
                st.subheader("📋 Detailed Route Comparison")
                
                routes = result.get('routes', [])
                
                # Display each route
                for route in routes:
                    is_recommended = route['rank'] == 1
                    
                    with st.container():
                        if is_recommended:
                            st.markdown("### ⭐ RECOMMENDED ROUTE")
                        else:
                            st.markdown(f"### Route #{route['rank']}")
                        
                        # Route name and basic info
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown(f"**📍 {route['summary']}**")
                            st.caption(route.get('explanation', ''))
                        
                        with col2:
                            st.metric("Distance", route['distance_text'])
                            st.metric("Duration", route['duration_text'])
                        
                        with col3:
                            st.metric("Overall Score", f"{route['composite_score']:.0f}/100")
                        
                        # Score breakdown
                        st.markdown("#### Score Breakdown")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        def get_score_class(score):
                            if score >= 70:
                                return "score-high"
                            elif score >= 50:
                                return "score-medium"
                            else:
                                return "score-low"
                        
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
                        
                        st.divider()
            
            with tab3:
                st.subheader("📊 Route Analytics")
                
                routes = result.get('routes', [])
                
                if routes:
                    # Create comparison chart
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
                    if 'recommended' in result:
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