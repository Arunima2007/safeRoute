import googlemaps
import polyline
from datetime import datetime

class MapsHelper:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)
    
    def get_route_alternatives(self, origin, destination):
        """
        Get multiple route alternatives from Google Maps
        Returns: List of routes with polylines, distance, duration
        """
        
        try:
            # Request directions with alternatives
            directions = self.gmaps.directions(
                origin=origin,
                destination=destination,
                mode="driving",
                alternatives=True,  # Get multiple routes
                departure_time=datetime.now(),
                traffic_model="best_guess"
            )
            
            routes = []
            for idx, route in enumerate(directions):
                route_data = {
                    'route_id': idx,
                    'summary': route['summary'],
                    'distance_meters': route['legs'][0]['distance']['value'],
                    'distance_text': route['legs'][0]['distance']['text'],
                    'duration_seconds': route['legs'][0]['duration']['value'],
                    'duration_text': route['legs'][0]['duration']['text'],
                    'polyline': route['overview_polyline']['points'],
                    'start_address': route['legs'][0]['start_address'],
                    'end_address': route['legs'][0]['end_address']
                }
                routes.append(route_data)
            
            return routes
        
        except Exception as e:
            print(f"Error getting routes: {e}")
            return []
    
    def decode_polyline_to_points(self, encoded_polyline, sample_interval=500):
        """
        Decode polyline and sample points at regular intervals
        sample_interval: distance in meters between sample points
        Returns: List of (lat, lng) tuples
        """
        
        # Decode polyline to coordinates
        coordinates = polyline.decode(encoded_polyline)
        
        # Sample points at regular intervals
        sampled_points = []
        sampled_points.append(coordinates[0])  # Always include start
        
        cumulative_distance = 0
        last_sampled_idx = 0
        
        for i in range(1, len(coordinates)):
            # Calculate distance from last sampled point
            dist = self._haversine_distance(
                coordinates[last_sampled_idx][0], 
                coordinates[last_sampled_idx][1],
                coordinates[i][0], 
                coordinates[i][1]
            )
            
            cumulative_distance += dist
            
            # Sample if we've traveled sample_interval meters
            if cumulative_distance >= sample_interval:
                sampled_points.append(coordinates[i])
                last_sampled_idx = i
                cumulative_distance = 0
        
        # Always include end point
        if sampled_points[-1] != coordinates[-1]:
            sampled_points.append(coordinates[-1])
        
        return sampled_points
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in meters"""
        from math import radians, cos, sin, asin, sqrt
        
        R = 6371000  # Earth radius in meters
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return R * c