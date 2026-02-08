from route_service import MapsHelper

# Your Google Maps API key
API_KEY = "AIzaSyDI3wkTRvjH0j0cJ78dNiYIiKfQl25GcGw"

maps = MapsHelper(API_KEY)

# Test with Delhi locations
origin = "Connaught Place, Delhi"
destination = "India Gate, Delhi"

print(f"Finding routes from {origin} to {destination}...\n")

routes = maps.get_route_alternatives(origin, destination)

print(f"Found {len(routes)} route alternatives:\n")

for route in routes:
    print(f"Route {route['route_id'] + 1}: {route['summary']}")
    print(f"  Distance: {route['distance_text']}")
    print(f"  Duration: {route['duration_text']}")
    
    # Sample points along the route
    points = maps.decode_polyline_to_points(route['polyline'], sample_interval=500)
    print(f"  Sample Points: {len(points)}")
    print(f"  First Point: {points[0]}")
    print(f"  Last Point: {points[-1]}\n")