# app.py - CLEAN VERSION

from flask import Flask, request, jsonify
from flask_cors import CORS
from services.route_service import MapsHelper
from services.scoring_service import RouteScorer
from services.route_ranker import RouteRanker
from datetime import datetime

app = Flask(__name__)
CORS(app)

# API Keys
GOOGLE_API_KEY = "AIzaSyDI3wkTRvjH0j0cJ78dNiYIiKfQl25GcGw"
OPENAQ_API_KEY = "1efd3ce0fe5eef3ef9792b516b0eb1b30652ee72b67ada6d9ba274ac4c71b9b4"

# Initialize components
maps_helper = MapsHelper(GOOGLE_API_KEY)

# Load crime data
from stats2 import DatasetPreparer
preparer = DatasetPreparer(GOOGLE_API_KEY, OPENAQ_API_KEY)
crime_data = preparer.crime_data

# Initialize scorer and ranker
scorer = RouteScorer(
    "model/risk_model.pkl", 
    "model/feature_columns.pkl", 
    crime_data,
    maps_helper,
    OPENAQ_API_KEY
)
ranker = RouteRanker()

@app.route('/api/compare-routes', methods=['POST'])
def compare_routes():
    try:
        data = request.get_json()
        
        origin = data.get('origin')
        destination = data.get('destination')
        preference = data.get('preference', 'balanced')
        
        now = datetime.now()
        hour_of_day = now.hour
        is_weekend = 1 if now.weekday() >= 5 else 0
        
        print(f"\nFinding routes from {origin} to {destination}")
        print(f"Preference: {preference}")
        
        routes = maps_helper.get_route_alternatives(origin, destination)
        
        if not routes:
            return jsonify({"error": "No routes found"}), 404
        
        print(f"Found {len(routes)} routes")
        
        routes_with_scores = []
        
        for idx, route in enumerate(routes):
            print(f"Analyzing Route {idx + 1}: {route['summary']}")
            
            try:
                scores = scorer.score_route(route, hour_of_day, is_weekend)
                
                route_complete = {
                    **route,
                    **scores,
                    'crime_index_display': f"{scores.get('avg_crime', 0) * 10:.2f}/10",
                    'lighting_display': f"{scores.get('avg_lighting', 0) * 10:.1f}/10",
                    'traffic_flow_display': f"{(1 - scores.get('avg_traffic', 0)) * 10:.2f}/10",
                    'air_quality_display': f"{(1 - scores.get('avg_pollution', 0)) * 10:.2f}/10",
                    'carbon_footprint_kg': (route['distance_meters'] / 1000) * 0.12 * scores.get('avg_carbon', 0.5)
                }
                
                routes_with_scores.append(route_complete)
                
                print(f"  Safety: {scores['safety_score']:.1f}/100")
                print(f"  Eco: {scores['eco_score']:.1f}/100")
            
            except Exception as e:
                print(f"  Error scoring route: {e}")
                continue
        
        if not routes_with_scores:
            return jsonify({"error": "Failed to score routes"}), 500
        
        ranked_routes = ranker.rank_routes(routes_with_scores, preference)
        
        print(f"Routes ranked by {preference} preference")
        
        response = {
            "origin": origin,
            "destination": destination,
            "preference": preference,
            "total_routes": len(ranked_routes),
            "routes": ranked_routes,
            "recommended": ranked_routes[0] if ranked_routes else None
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "model_loaded": True,
        "crime_data_loaded": True
    })

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Delhi Route Comparison API"
    })

if __name__ == '__main__':
    print("="*60)
    print("Delhi Route Comparison API Starting...")
    print("="*60)
    print(f"Google Maps API configured")
    print(f"Crime data loaded: {len(crime_data['df'])} hotspots")
    print(f"ML Model loaded")
    print("="*60)
    print("Starting Flask server...")
    app.run(debug=True, port=6000, host='0.0.0.0')
