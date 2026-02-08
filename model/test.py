import joblib
import pandas as pd

model = joblib.load("risk_model.pkl")

scenarios = [
    {
        'name': 'Safe Morning Commute',
        'crime_rate': 0.2, 'pollution_level': 0.3, 
        'traffic_density': 0.5, 'lighting_score': 0.9,
        'carbon_factor': 0.44, 'hour_of_day': 8, 
        'is_night': 0, 'is_weekend': 0
    },
    {
        'name': 'Risky Night Route',
        'crime_rate': 0.8, 'pollution_level': 0.5, 
        'traffic_density': 0.3, 'lighting_score': 0.2,
        'carbon_factor': 0.36, 'hour_of_day': 23, 
        'is_night': 1, 'is_weekend': 0
    },
    {
        'name': 'Moderate Evening',
        'crime_rate': 0.4, 'pollution_level': 0.6, 
        'traffic_density': 0.7, 'lighting_score': 0.6,
        'carbon_factor': 0.67, 'hour_of_day': 18, 
        'is_night': 0, 'is_weekend': 1
    }
]

print("="*60)
print("SCENARIO TESTING")
print("="*60)

for scenario in scenarios:
    name = scenario.pop('name')
    df = pd.DataFrame([scenario])
    pred = model.predict(df)[0]
    prob = model.predict_proba(df)[0]
    
    print(f"\n📍 {name}")
    print(f"   Prediction: {['✅ Safe', '⚠️ Moderate', '❌ Risky'][pred]}")
    print(f"   Confidence: {max(prob):.1%}")