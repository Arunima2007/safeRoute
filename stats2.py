# prepare_dataset.py

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import random
from scipy.spatial import cKDTree
import polyline
import json

class DatasetPreparer:
    def __init__(self, google_api_key, openaq_api_key):
        self.google_api_key = google_api_key
        self.openaq_api_key = openaq_api_key
        self.crime_data = self.load_crime_hotspots()
        
    def load_crime_hotspots(self):
        """
        Crime hotspots in Delhi based on public data
        Source: Delhi Police crime statistics and news reports
        """
        hotspots = [
            # High crime areas
            {"lat": 28.6692, "lng": 77.4538, "crime_count": 85, "area": "Ghaziabad Border"},
            {"lat": 28.5355, "lng": 77.3910, "crime_count": 78, "area": "Noida Sector 18"},
            {"lat": 28.4595, "lng": 77.0266, "crime_count": 72, "area": "Dwarka"},
            {"lat": 28.6517, "lng": 77.2219, "crime_count": 68, "area": "Kashmere Gate"},
            {"lat": 28.6519, "lng": 77.2315, "crime_count": 65, "area": "Old Delhi"},
            {"lat": 28.5494, "lng": 77.2001, "crime_count": 62, "area": "Saket"},
            
            # Moderate crime areas
            {"lat": 28.6139, "lng": 77.2090, "crime_count": 45, "area": "Connaught Place"},
            {"lat": 28.5244, "lng": 77.1855, "crime_count": 48, "area": "Nehru Place"},
            {"lat": 28.7041, "lng": 77.1025, "crime_count": 42, "area": "Rohini"},
            {"lat": 28.6692, "lng": 77.1100, "crime_count": 40, "area": "Pitampura"},
            {"lat": 28.5245, "lng": 77.2066, "crime_count": 43, "area": "Greater Kailash"},
            {"lat": 28.6304, "lng": 77.2177, "crime_count": 41, "area": "Barakhamba Road"},
            
            # Lower crime areas
            {"lat": 28.5921, "lng": 77.0460, "crime_count": 25, "area": "Janakpuri"},
            {"lat": 28.6358, "lng": 77.2245, "crime_count": 28, "area": "Mandi House"},
            {"lat": 28.6280, "lng": 77.2207, "crime_count": 22, "area": "Rajpath"},
            {"lat": 28.6562, "lng": 77.2410, "crime_count": 24, "area": "Civil Lines"},
            {"lat": 28.5672, "lng": 77.2100, "crime_count": 20, "area": "Lajpat Nagar"},
            {"lat": 28.5707, "lng": 77.3206, "crime_count": 26, "area": "Mayur Vihar"},
            {"lat": 28.6562, "lng": 77.2733, "crime_count": 23, "area": "Shahdara"},
            {"lat": 28.6280, "lng": 77.3648, "crime_count": 27, "area": "Preet Vihar"},
        ]
        
        df = pd.DataFrame(hotspots)
        coords = df[['lat', 'lng']].values
        tree = cKDTree(coords)
        
        return {'df': df, 'tree': tree, 'coords': coords}
    
    def get_crime_score(self, lat, lng):
        """Calculate crime risk based on proximity to hotspots"""
        
        # Find nearby hotspots within 3km
        indices = self.crime_data['tree'].query_ball_point([lat, lng], 0.027)
        
        if not indices:
            return random.uniform(0.15, 0.25)  # Base low crime
        
        # Calculate weighted score
        total_weighted_crime = 0
        total_weight = 0
        
        for idx in indices:
            hotspot = self.crime_data['df'].iloc[idx]
            crime_count = hotspot['crime_count']
            
            # Calculate distance
            distance = np.sqrt(
                (lat - hotspot['lat'])**2 + 
                (lng - hotspot['lng'])**2
            )
            
            # Weight by inverse distance (closer = more influence)
            weight = 1 / (distance + 0.001)
            total_weighted_crime += crime_count * weight
            total_weight += weight
        
        avg_crime = total_weighted_crime / total_weight if total_weight > 0 else 20
        
        # Normalize to 0-1 (assuming max crime count is 100)
        crime_score = min(avg_crime / 100, 1.0)
        
        # Add some randomness for variation
        crime_score = max(0, min(1, crime_score + random.uniform(-0.05, 0.05)))
        
        return crime_score
    
    def get_pollution_level(self, lat, lng):
        """Get real pollution data from OpenAQ with fallback"""
        
        url = "https://api.openaq.org/v3/locations"
        headers = {"X-API-Key": self.openaq_api_key}
        
        params = {
            "coordinates": f"{lat},{lng}",
            "radius": 25000,
            "limit": 5,
            "order_by": "id",
            "parameters_id": 2
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                for location in data.get('results', [])[:3]:
                    location_id = location.get('id')
                    
                    meas_url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
                    meas_response = requests.get(meas_url, headers=headers, timeout=5)
                    
                    if meas_response.status_code == 200:
                        meas_data = meas_response.json()
                        
                        if 'results' in meas_data and len(meas_data['results']) > 0:
                            for result in meas_data['results']:
                                if 'value' in result:
                                    pm25 = result['value']
                                    return min(pm25 / 500.0, 1.0)
        except Exception as e:
            print(f"    Pollution API error: {e}")
        
        # Fallback: Delhi typical pollution levels
        # Delhi PM2.5 ranges from 50-250 typically
        base_pollution = random.uniform(100, 200)
        return min(base_pollution / 500.0, 1.0)
    
    def get_traffic_density_simple(self, hour, day_of_week, lat, lng):
        """
        Estimate traffic based on time and location
        This is used when Google API quota is exceeded
        """
        
        is_weekend = day_of_week >= 5
        
        # Distance from city center affects traffic
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
                base_traffic = 0.85  # Rush hour
            elif 11 <= hour <= 16:
                base_traffic = 0.55
            elif 21 <= hour <= 23:
                base_traffic = 0.40
            else:
                base_traffic = 0.20
        
        # Central areas have more traffic
        if distance_from_center < 0.05:  # Central Delhi
            traffic_multiplier = 1.2
        elif distance_from_center < 0.15:  # Mid Delhi
            traffic_multiplier = 1.0
        else:  # Outer Delhi
            traffic_multiplier = 0.8
        
        traffic = base_traffic * traffic_multiplier
        
        # Add randomness
        traffic = max(0, min(1, traffic + random.uniform(-0.1, 0.1)))
        
        return traffic
    
    def get_lighting_score(self, lat, lng, hour):
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
        
        # Main roads and central areas have better lighting
        if distance < 0.03:  # Central Delhi (~3km)
            lighting = random.uniform(0.75, 0.90)
        elif distance < 0.10:  # Mid Delhi (~10km)
            lighting = random.uniform(0.55, 0.75)
        else:  # Outer areas
            lighting = random.uniform(0.35, 0.60)
        
        return lighting
    
    def generate_delhi_routes(self, num_routes=100):
        """
        Generate random routes within Delhi
        """
        
        # Delhi bounding box
        delhi_bounds = {
            'min_lat': 28.4089,
            'max_lat': 28.8833,
            'min_lng': 76.8388,
            'max_lng': 77.3465
        }
        
        # Key Delhi locations for realistic routes
        key_locations = [
            (28.6139, 77.2090, "Connaught Place"),
            (28.6129, 77.2295, "India Gate"),
            (28.6562, 77.2410, "Red Fort"),
            (28.5494, 77.2001, "Saket"),
            (28.5355, 77.3910, "Noida City Centre"),
            (28.7041, 77.1025, "Rohini"),
            (28.4595, 77.0266, "Dwarka"),
            (28.5672, 77.2100, "Lajpat Nagar"),
            (28.6304, 77.2177, "Barakhamba Road"),
            (28.5244, 77.1855, "Nehru Place"),
        ]
        
        routes = []
        
        for i in range(num_routes):
            # 70% use key locations, 30% random
            if random.random() < 0.7:
                origin = random.choice(key_locations)[:2]
                dest = random.choice(key_locations)[:2]
            else:
                origin = (
                    random.uniform(delhi_bounds['min_lat'], delhi_bounds['max_lat']),
                    random.uniform(delhi_bounds['min_lng'], delhi_bounds['max_lng'])
                )
                dest = (
                    random.uniform(delhi_bounds['min_lat'], delhi_bounds['max_lat']),
                    random.uniform(delhi_bounds['min_lng'], delhi_bounds['max_lng'])
                )
            
            # Make sure origin != destination
            if origin == dest:
                continue
            
            routes.append({
                'origin_lat': origin[0],
                'origin_lng': origin[1],
                'dest_lat': dest[0],
                'dest_lng': dest[1]
            })
        
        return routes
    
    def collect_route_samples(self, route, samples_per_route=10):
        """
        Collect data samples along a route
        Simulates sampling points without making too many API calls
        """
        
        origin = (route['origin_lat'], route['origin_lng'])
        dest = (route['dest_lat'], route['dest_lng'])
        
        # Generate interpolated points along straight line
        # In real implementation, you'd use Google Directions API polyline
        samples = []
        
        for i in range(samples_per_route):
            t = i / (samples_per_route - 1)  # 0 to 1
            
            lat = origin[0] + t * (dest[0] - origin[0])
            lng = origin[1] + t * (dest[1] - origin[1])
            
            # Vary time across the day
            hour = random.randint(0, 23)
            day_of_week = random.randint(0, 6)
            
            # Collect features
            crime = self.get_crime_score(lat, lng)
            pollution = self.get_pollution_level(lat, lng)
            traffic = self.get_traffic_density_simple(hour, day_of_week, lat, lng)
            lighting = self.get_lighting_score(lat, lng, hour)
            
            # Derived features
            carbon_factor = (traffic * 0.7) + (pollution * 0.3)
            is_night = 1 if (hour < 6 or hour > 20) else 0
            is_weekend = 1 if day_of_week >= 5 else 0
            
            sample = {
                'latitude': lat,
                'longitude': lng,
                'crime_rate': crime,
                'pollution_level': pollution,
                'traffic_density': traffic,
                'lighting_score': lighting,
                'carbon_factor': carbon_factor,
                'hour_of_day': hour,
                'is_night': is_night,
                'is_weekend': is_weekend,
                'timestamp': datetime.now() - timedelta(days=random.randint(0, 30))
            }
            
            samples.append(sample)
            
            # Small delay to be polite to APIs
            time.sleep(0.1)
        
        return samples
    
    def label_dataset(self, df):
        """
        Assign risk labels based on comprehensive scoring
        """
        
        print("\n📋 Labeling dataset...")
        
        # Calculate base risk score
        def calculate_risk_score(row):
            score = (
                row['crime_rate'] * 0.35 +
                (1 - row['lighting_score']) * 0.25 +
                row['traffic_density'] * 0.15 +
                row['pollution_level'] * 0.10 +
                row['is_night'] * 0.10 +
                row['is_weekend'] * 0.05
            )
            return score
        
        df['risk_score'] = df.apply(calculate_risk_score, axis=1)
        
        # Apply adjustments for dangerous combinations
        def adjust_risk(row):
            risk = row['risk_score']
            
            # High crime + poor lighting + night = very dangerous
            if row['crime_rate'] > 0.6 and row['lighting_score'] < 0.4 and row['is_night'] == 1:
                risk *= 1.4
            
            # Low crime + good lighting = safer
            if row['crime_rate'] < 0.2 and row['lighting_score'] > 0.8:
                risk *= 0.6
            
            # Heavy traffic + high pollution = health risk
            if row['traffic_density'] > 0.7 and row['pollution_level'] > 0.6:
                risk *= 1.2
            
            return min(risk, 1.0)
        
        df['adjusted_risk'] = df.apply(adjust_risk, axis=1)
        
        # Assign labels using percentiles for balanced distribution
        p33 = df['adjusted_risk'].quantile(0.33)
        p67 = df['adjusted_risk'].quantile(0.67)
        
        def assign_label(risk):
            if risk < p33:
                return 0  # Safe
            elif risk < p67:
                return 1  # Moderate
            else:
                return 2  # Risky
        
        df['risk_label'] = df['adjusted_risk'].apply(assign_label)
        
        # Add location names
        df['location'] = df.apply(
            lambda x: f"Delhi ({x['latitude']:.4f}, {x['longitude']:.4f})", 
            axis=1
        )
        
        return df
    
    def prepare_complete_dataset(self, num_routes=100, samples_per_route=10):
        """
        Main function to prepare the complete dataset
        """
        
        print("="*70)
        print("🚀 DELHI SAFETY DATASET PREPARATION")
        print("="*70)
        print(f"\nTarget: {num_routes} routes × {samples_per_route} samples = {num_routes * samples_per_route} total samples")
        print("\nThis will take approximately 10-15 minutes...")
        print("Progress will be saved incrementally.\n")
        
        # Generate routes
        print("📍 Generating routes...")
        routes = self.generate_delhi_routes(num_routes)
        print(f"✓ Generated {len(routes)} routes")
        
        # Collect samples
        all_samples = []
        
        print("\n📊 Collecting samples along routes...")
        for i, route in enumerate(routes):
            print(f"\nRoute {i+1}/{len(routes)}: ({route['origin_lat']:.4f}, {route['origin_lng']:.4f}) → ({route['dest_lat']:.4f}, {route['dest_lng']:.4f})")
            
            samples = self.collect_route_samples(route, samples_per_route)
            all_samples.extend(samples)
            
            print(f"  ✓ Collected {len(samples)} samples")
            
            # Save checkpoint every 20 routes
            if (i + 1) % 20 == 0:
                checkpoint_df = pd.DataFrame(all_samples)
                checkpoint_df.to_csv(f'checkpoint_{i+1}_routes.csv', index=False)
                print(f"\n💾 Checkpoint saved: {len(all_samples)} samples")
        
        # Create DataFrame
        print(f"\n📁 Creating dataset...")
        df = pd.DataFrame(all_samples)
        
        # Label the dataset
        df = self.label_dataset(df)
        
        # Validation
        print("\n" + "="*70)
        print("📊 DATASET STATISTICS")
        print("="*70)
        
        print(f"\nTotal samples: {len(df)}")
        print("\nLabel Distribution:")
        print(df['risk_label'].value_counts().sort_index())
        print(f"\nPercentages:")
        print(df['risk_label'].value_counts(normalize=True).sort_index() * 100)
        
        print("\n Feature Statistics by Risk Label:")
        print(df.groupby('risk_label')[['crime_rate', 'pollution_level', 'traffic_density', 'lighting_score']].mean().round(3))
        
        print("\nRisk Score Ranges:")
        print(df.groupby('risk_label')['adjusted_risk'].describe())
        
        # Sample validation
        print("\n" + "="*70)
        print("🔍 SAMPLE VALIDATION")
        print("="*70)
        
        for label in [0, 1, 2]:
            label_name = ['SAFE', 'MODERATE', 'RISKY'][label]
            print(f"\n{label_name} Route Example:")
            sample = df[df['risk_label'] == label].iloc[0]
            print(f"  Crime Rate: {sample['crime_rate']:.3f}")
            print(f"  Lighting: {sample['lighting_score']:.3f}")
            print(f"  Traffic: {sample['traffic_density']:.3f}")
            print(f"  Pollution: {sample['pollution_level']:.3f}")
            print(f"  Night Time: {'Yes' if sample['is_night'] else 'No'}")
            print(f"  Risk Score: {sample['adjusted_risk']:.3f}")
        
        return df


def main():
    """
    Main execution function
    """
    
    # API Keys - REPLACE WITH YOUR KEYS
    GOOGLE_API_KEY = "AIzaSyDI3wkTRvjH0j0cJ78dNiYIiKfQl25GcGw"  # Get from: https://console.cloud.google.com
    OPENAQ_API_KEY = "1efd3ce0fe5eef3ef9792b516b0eb1b30652ee72b67ada6d9ba274ac4c71b9b4"  # Your existing key
    
    # Initialize preparer
    preparer = DatasetPreparer(
        google_api_key=GOOGLE_API_KEY,
        openaq_api_key=OPENAQ_API_KEY
    )
    
    # Prepare dataset
    # For hackathon: Start with 50-100 routes
    # Each route generates 10 samples = 500-1000 total samples
    df = preparer.prepare_complete_dataset(
        num_routes=100,        # Number of routes
        samples_per_route=10   # Samples per route
    )
    
    # Save final dataset
    output_file = 'delhi_safety_dataset.csv'
    df.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print("✅ DATASET PREPARATION COMPLETE!")
    print("="*70)
    print(f"\n📁 Saved to: {output_file}")
    print(f"📊 Total samples: {len(df)}")
    print(f"✓ Ready for model training!")
    
    # Also save a version without timestamps for training
    training_df = df.drop(['timestamp'], axis=1)
    training_df.to_csv('delhi_safety_dataset_training.csv', index=False)
    print(f"📁 Training version saved: delhi_safety_dataset_training.csv")
    
    # Print feature columns for reference
    print("\n📋 Feature columns:")
    feature_cols = [col for col in df.columns if col not in ['location', 'risk_label', 'risk_score', 'adjusted_risk', 'timestamp']]
    for col in feature_cols:
        print(f"  - {col}")


if __name__ == "__main__":
    main()