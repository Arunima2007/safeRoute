# services/scoring_service.py

import numpy as np
import pandas as pd
import joblib
import random

class RouteScorer:
    def __init__(self, model_path, feature_cols_path, crime_data, maps_helper, openaq_api_key=None):
        self.model = joblib.load(model_path)
        self.feature_cols = joblib.load(feature_cols_path)
        self.crime_data = crime_data
        self.maps = maps_helper
        self.openaq_api_key = openaq_api_key
    
    def score_route(self, route, hour_of_day, is_weekend):
        """
        Calculate safety, speed, and eco scores for a route
        """
        
        print(f"     Scoring route: {route['summary']}")
        
        # 1. Get sample points along the route
        points = self.maps.decode_polyline_to_points(
            route['polyline'], 
            sample_interval=500
        )
        
        print(f"       → Sampled {len(points)} points")
        
        # 2. Calculate features for each point
        point_features = []
        
        for lat, lng in points:
            features = self._get_point_features(
                lat, lng, hour_of_day, is_weekend
            )
            point_features.append(features)
        
        # 3. Calculate raw averages
        avg_crime = np.mean([f['crime_rate'] for f in point_features])
        avg_pollution = np.mean([f['pollution_level'] for f in point_features])
        avg_traffic = np.mean([f['traffic_density'] for f in point_features])
        avg_lighting = np.mean([f['lighting_score'] for f in point_features])
        avg_carbon = np.mean([f['carbon_factor'] for f in point_features])
        
        print(f"       → Crime: {avg_crime:.3f}, Pollution: {avg_pollution:.3f}, Traffic: {avg_traffic:.3f}, Lighting: {avg_lighting:.3f}")
        
        # 4. Predict risk using ML model
        df = pd.DataFrame(point_features)
        df = df[self.feature_cols]
        
        try:
            risk_predictions = self.model.predict_proba(df)
            
            # Get risk probabilities
            safe_prob = np.mean([pred[0] for pred in risk_predictions])
            moderate_prob = np.mean([pred[1] for pred in risk_predictions])
            risky_prob = np.mean([pred[2] for pred in risk_predictions])
            
            # Weighted risk score (0 = safe, 1 = risky)
            avg_risk = (safe_prob * 0.0) + (moderate_prob * 0.5) + (risky_prob * 1.0)
            
            print(f"       → ML Risk: {avg_risk:.3f} (Safe: {safe_prob:.2f}, Mod: {moderate_prob:.2f}, Risky: {risky_prob:.2f})")
            
        except Exception as e:
            print(f"       → ML prediction failed: {e}, using heuristic")
            # Fallback heuristic
            avg_risk = (avg_crime * 0.4 + (1 - avg_lighting) * 0.3 + avg_traffic * 0.3)
            safe_prob = moderate_prob = risky_prob = None
        
        # 5. Calculate scores (0-100 scale)
        safety_score = self._calculate_safety_score(
            avg_crime, avg_lighting, avg_traffic, avg_risk
        )
        
        eco_score = self._calculate_eco_score(avg_pollution, avg_carbon)
        
        # Risk classification
        # More lenient thresholds
        if avg_risk < 0.45:  # Was 0.35
            risk_label = 0
            risk_name = 'Safe'
        elif avg_risk < 0.75:  # Was 0.65
            risk_label = 1
            risk_name = 'Moderate'
        else:
            risk_label = 2
            risk_name = 'Risky'
        
        print(f"       → Scores: Safety={safety_score:.1f}, Eco={eco_score:.1f}, Risk={risk_name}")
        
        # Generate explanation
        explanation = self._generate_explanation(
            risk_name, avg_crime, avg_lighting, avg_pollution, avg_carbon
        )
        
        # IMPORTANT: Return ALL the values
        result = {
            'safety_score': float(safety_score),
            'eco_score': float(eco_score),
            'avg_risk': float(avg_risk),
            'avg_crime': float(avg_crime),           # THIS WAS MISSING
            'avg_pollution': float(avg_pollution),   # THIS WAS MISSING
            'avg_traffic': float(avg_traffic),       # THIS WAS MISSING
            'avg_lighting': float(avg_lighting),     # THIS WAS MISSING
            'avg_carbon': float(avg_carbon),
            'sample_points': len(points),
            'risk_label': int(risk_label),
            'risk_name': risk_name,
            'explanation': explanation,
        }
        
        # Add ML probabilities if available
        if safe_prob is not None:
            result['safe_probability'] = float(safe_prob)
            result['moderate_probability'] = float(moderate_prob)
            result['risky_probability'] = float(risky_prob)
        
        return result
    
    def _calculate_safety_score(self, crime, lighting, traffic, ml_risk):
        """
        Calculate safety score from multiple factors
        """
        
        # Component scores (0-100, higher is better)
        crime_score = (1 - crime) * 100
        lighting_score = lighting * 100
        traffic_safety_score = (1 - traffic) * 50  # Traffic affects accidents
        ml_score = (1 - ml_risk) * 100
        
        # Weighted combination - balance between data and ML
        safety_score = (
            crime_score * 0.40 +
            lighting_score * 0.35 +
            traffic_safety_score * 0.20 +
            ml_score * 0.05
        )
        
        return max(0, min(100, safety_score))
    
    def _calculate_eco_score(self, pollution, carbon):
        """
        Calculate eco-friendliness score
        """
        
        pollution_score = (1 - pollution) * 100
        carbon_score = (1 - carbon) * 100
        
        eco_score = (pollution_score * 0.5 + carbon_score * 0.5)
        
        return max(0, min(100, eco_score))
    
    def _generate_explanation(self, risk_name, crime, lighting, pollution, carbon):
        """Generate explanation text"""
        
        parts = []
        
        # Risk level
        if risk_name == 'Safe':
            parts.append("🛡️ Safe route")
        elif risk_name == 'Moderate':
            parts.append("⚠️ Moderately safe route")
        else:
            parts.append("🚨 Higher risk route")
        
        # Crime
        if crime < 0.3:
            parts.append("through low-crime areas")
        elif crime < 0.5:
            parts.append("through moderate-crime areas")
        else:
            parts.append("through higher-crime areas")
        
        # Lighting
        if lighting > 0.7:
            parts.append("with excellent street lighting")
        elif lighting > 0.5:
            parts.append("with adequate lighting")
        else:
            parts.append("with limited lighting")
        
        # Air quality
        if pollution < 0.3:
            parts.append(". 🌱 Excellent air quality")
        elif pollution < 0.5:
            parts.append(". 🌿 Moderate air quality")
        else:
            parts.append(". 🏭 Poor air quality")
        
        # Carbon
        if carbon < 0.4:
            parts.append("and minimal emissions")
        elif carbon < 0.6:
            parts.append("with moderate emissions")
        
        return " ".join(parts) + "."
    
    def _get_point_features(self, lat, lng, hour, is_weekend):
        """Calculate features for a single point"""
        
        crime_rate = self._get_crime_score(lat, lng)
        pollution = self._get_pollution_estimate(lat, lng)
        traffic = self._get_traffic_estimate(hour, is_weekend, lat, lng)
        lighting = self._get_lighting_estimate(lat, lng, hour)
        
        carbon_factor = (traffic * 0.7) + (pollution * 0.3)
        is_night = 1 if (hour < 6 or hour > 20) else 0
        
        return {
            'crime_rate': crime_rate,
            'pollution_level': pollution,
            'traffic_density': traffic,
            'lighting_score': lighting,
            'carbon_factor': carbon_factor,
            'hour_of_day': hour,
            'is_night': is_night,
            'is_weekend': is_weekend
        }
    
    def _get_crime_score(self, lat, lng):
        """Calculate crime risk based on proximity to hotspots"""
        
        indices = self.crime_data['tree'].query_ball_point([lat, lng], 0.027)
        
        if not indices:
            return random.uniform(0.15, 0.25)
        
        total_weighted_crime = 0
        total_weight = 0
        
        for idx in indices:
            hotspot = self.crime_data['df'].iloc[idx]
            crime_count = hotspot['crime_count']
            
            distance = np.sqrt(
                (lat - hotspot['lat'])**2 + 
                (lng - hotspot['lng'])**2
            )
            
            weight = 1 / (distance + 0.001)
            total_weighted_crime += crime_count * weight
            total_weight += weight
        
        avg_crime = total_weighted_crime / total_weight if total_weight > 0 else 20
        crime_score = min(avg_crime / 100, 1.0)
        crime_score = max(0, min(1, crime_score + random.uniform(-0.05, 0.05)))
        
        return crime_score
    
    def _get_pollution_estimate(self, lat, lng):
        """Get pollution estimate"""
        # Delhi typical PM2.5 levels: 100-200 µg/m³
        return random.uniform(0.3, 0.5)
    
    def _get_traffic_estimate(self, hour, is_weekend, lat, lng):
        """Estimate traffic based on time and location"""
        
        city_center = (28.6139, 77.2090)
        distance_from_center = np.sqrt(
            (lat - city_center[0])**2 + 
            (lng - city_center[1])**2
        )
        
        # Base traffic by time
        if is_weekend:
            if 10 <= hour <= 13 or 18 <= hour <= 21:
                base_traffic = 0.5
            else:
                base_traffic = 0.25
        else:
            if 8 <= hour <= 10 or 17 <= hour <= 20:
                base_traffic = 0.85
            elif 11 <= hour <= 16:
                base_traffic = 0.55
            elif 21 <= hour <= 23:
                base_traffic = 0.40
            else:
                base_traffic = 0.20
        
        # Location multiplier
        if distance_from_center < 0.05:
            traffic_multiplier = 1.2
        elif distance_from_center < 0.15:
            traffic_multiplier = 1.0
        else:
            traffic_multiplier = 0.8
        
        traffic = base_traffic * traffic_multiplier
        traffic = max(0, min(1, traffic + random.uniform(-0.1, 0.1)))
        
        return traffic
    
    def _get_lighting_estimate(self, lat, lng, hour):
        """Estimate lighting based on location and time"""
        
        # Daytime - lighting not critical
        if 6 <= hour <= 18:
            return random.uniform(0.85, 0.95)
        
        # Nighttime - depends on area
        city_center = (28.6139, 77.2090)
        distance = np.sqrt(
            (lat - city_center[0])**2 + 
            (lng - city_center[1])**2
        )
        
        if distance < 0.03:  # Central (~3km)
            lighting = random.uniform(0.75, 0.90)
        elif distance < 0.10:  # Mid (~10km)
            lighting = random.uniform(0.55, 0.75)
        else:  # Outer
            lighting = random.uniform(0.35, 0.60)
        
        return lighting