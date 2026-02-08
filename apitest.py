import requests
import pandas as pd
from datetime import datetime

def get_live_pollution_v3(api_key):
    """Fetch most recent PM2.5 data for Delhi"""
    
    url = "https://api.openaq.org/v3/locations"
    headers = {"X-API-Key": api_key}
    
    params = {
        "coordinates": "28.6139,77.2090",
        "radius": 25000,
        "limit": 20,
        "order_by": "id",
        "parameters_id": 2
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            most_recent_value = None
            most_recent_date = None
            best_location = None
            
            for location in data.get('results', []):
                location_id = location.get('id')
                location_name = location.get('name', 'Unknown')
                
                measurements_url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
                
                try:
                    meas_response = requests.get(measurements_url, headers=headers)
                    
                    if meas_response.status_code == 200:
                        meas_data = meas_response.json()
                        
                        if 'results' in meas_data and len(meas_data['results']) > 0:
                            for result in meas_data['results']:
                                if 'value' in result and 'datetime' in result:
                                    current_date = result['datetime']['utc']
                                    current_value = result['value']
                                    
                                    if most_recent_date is None or current_date > most_recent_date:
                                        most_recent_date = current_date
                                        most_recent_value = current_value
                                        best_location = location_name
                                        
                except Exception as e:
                    continue
            
            if most_recent_value is not None:
                print(f"✓ PM2.5: {most_recent_value} µg/m³ from {best_location}")
                normalized = min(most_recent_value / 500.0, 1.0)
                return normalized
                        
    except Exception as e:
        print(f"Pollution API Error: {e}")
    
    return 0.5


def get_live_traffic(lat, lng, google_api_key):
    """
    Fetch real-time traffic density using Google Maps Distance Matrix API
    Returns a normalized traffic score (0-1)
    """
    
    # We'll check traffic on a typical route (e.g., 5km radius)
    origin = f"{lat},{lng}"
    # Check traffic to a point 5km away
    dest_lat = lat + 0.045  # ~5km north
    dest_lng = lng + 0.045  # ~5km east
    destination = f"{dest_lat},{dest_lng}"
    
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    params = {
        "origins": origin,
        "destinations": destination,
        "departure_time": "now",  # Get current traffic
        "traffic_model": "best_guess",
        "key": google_api_key
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'OK':
                element = data['rows'][0]['elements'][0]
                
                if element['status'] == 'OK':
                    # Get duration in traffic vs normal duration
                    duration_in_traffic = element.get('duration_in_traffic', {}).get('value', 0)
                    normal_duration = element.get('duration', {}).get('value', 1)
                    
                    if normal_duration > 0:
                        # Calculate traffic ratio (1.0 = no traffic, 2.0 = double time)
                        traffic_ratio = duration_in_traffic / normal_duration
                        
                        # Normalize to 0-1 scale
                        # 1.0 ratio = 0 traffic, 2.0+ ratio = max traffic
                        traffic_density = min((traffic_ratio - 1.0), 1.0)
                        
                        print(f"✓ Traffic: {traffic_ratio:.2f}x normal time (density: {traffic_density:.2f})")
                        return traffic_density
            else:
                print(f"Google Maps API error: {data.get('error_message', 'Unknown error')}")
                
    except Exception as e:
        print(f"Traffic API Error: {e}")
    
    print("Using default traffic density: 0.6")
    return 0.6


def create_real_data_row(lat, lng, crime_stat, light_val, google_api_key=None):
    """Create a data row with real-time pollution and traffic data"""
    
    # Get real pollution data
    pollution = get_live_pollution_v3("1efd3ce0fe5eef3ef9792b516b0eb1b30652ee72b67ada6d9ba274ac4c71b9b4")
    
    # Get real traffic data (if API key provided)
    if google_api_key:
        traffic_density = get_live_traffic(lat, lng, google_api_key)
    else:
        traffic_density = 0.6
        print("ℹ️  No Google API key - using default traffic: 0.6")
    
    # Calculate carbon factor
    carbon_factor = (traffic_density * 0.7) + (pollution * 0.3)
    
    return {
        "latitude": lat,
        "longitude": lng,
        "crime_rate": crime_stat,
        "pollution_level": pollution,
        "traffic_density": traffic_density,
        "lighting_score": light_val,
        "carbon_factor": carbon_factor,
        "timestamp": datetime.now()
    }


# ============================================================
# USAGE
# ============================================================

# Without Google API (uses default traffic)
print("=" * 60)
print("OPTION 1: Without Google Maps API")
print("=" * 60)
new_row = create_real_data_row(28.6139, 77.2090, 0.3, 0.9)
print("\nResult:")
for key, value in new_row.items():
    print(f"  {key}: {value}")

print("\n" + "=" * 60)
print("OPTION 2: With Google Maps API (for real traffic)")
print("=" * 60)

GOOGLE_API_KEY = "AIzaSyDI3wkTRvjH0j0cJ78dNiYIiKfQl25GcGw"
new_row = create_real_data_row(28.6139, 77.2090, 0.3, 0.9, GOOGLE_API_KEY)
print("Add your Google Maps API key to enable real-time traffic!")
print("Get one at: https://console.cloud.google.com/apis/credentials")


