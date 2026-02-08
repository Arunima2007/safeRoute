# debug_scores.py

import requests
import json

url = "http://127.0.0.1:5000/api/compare-routes"

test_data = {
    "origin": "Connaught Place, Delhi",
    "destination": "Rohini, Delhi",
    "preference": "safety"
}

response = requests.post(url, json=test_data)
result = response.json()

print("="*70)
print("DETAILED SCORE BREAKDOWN")
print("="*70)

for route in result['routes']:
    print(f"\n{route['rank']}. {route['summary']}")
    print(f"   Distance: {route['distance_text']}")
    print(f"   Duration: {route['duration_text']}")
    print(f"   Duration (seconds): {route['duration_seconds']}")
    print(f"\n   Raw Metrics:")
    print(f"   - avg_risk: {route.get('avg_risk', 'N/A')}")
    print(f"   - avg_crime: {route.get('avg_crime', 'N/A')}")
    print(f"   - avg_pollution: {route.get('avg_pollution', 'N/A')}")
    print(f"   - avg_carbon: {route.get('avg_carbon', 'N/A')}")
    print(f"   - avg_lighting: {route.get('avg_lighting', 'N/A')}")
    print(f"   - sample_points: {route.get('sample_points', 'N/A')}")
    print(f"\n   Calculated Scores:")
    print(f"   - Safety: {route['safety_score']:.1f}/100")
    print(f"   - Speed: {route['speed_score']:.1f}/100")
    print(f"   - Eco: {route['eco_score']:.1f}/100")
    print(f"   - Composite: {route['composite_score']:.1f}/100")