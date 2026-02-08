import random
import pandas as pd

# Delhi Locations with approximate coordinates
locations = [
    ("Seelampur", 28.6692, 77.2637),
    ("Nangloi", 28.6814, 77.0686),
    ("Rohini", 28.7041, 77.1025),
    ("Dwarka", 28.5921, 77.0460),
    ("ConnaughtPlace", 28.6315, 77.2167),
    ("LajpatNagar", 28.5677, 77.2432),
    ("KarolBagh", 28.6519, 77.1909),
    ("VasantKunj", 28.5245, 77.1555),
    ("Saket", 28.5244, 77.2066),
    ("Janakpuri", 28.6219, 77.0929),
    ("Okhla", 28.5355, 77.2721),
    ("ChandniChowk", 28.6562, 77.2303),
    ("Pitampura", 28.6967, 77.1325),
    ("GreaterKailash", 28.5484, 77.2381),
    ("Najafgarh", 28.6090, 76.9798),
]

# Function to assign risk label
def calculate_risk(crime, pollution, traffic, lighting):
    risk_score = (0.4 * crime) + (0.2 * pollution) + (0.2 * traffic) + (0.2 * (1 - lighting))

    if risk_score < 0.45:
        return 0
    elif risk_score < 0.65:
        return 1
    else:
        return 2

# Generate dataset
data = []

num_rows = 200   # 🔥 Change this number for bigger dataset

for _ in range(num_rows):
    loc = random.choice(locations)

    crime = round(random.uniform(0.3, 0.9), 2)
    pollution = round(random.uniform(0.4, 0.85), 2)
    traffic = round(random.uniform(0.3, 0.9), 2)
    lighting = round(random.uniform(0.3, 0.85), 2)
    carbon = round(random.uniform(0.3, 0.8), 2)

    risk = calculate_risk(crime, pollution, traffic, lighting)

    data.append([
        loc[0], loc[1], loc[2],
        crime, pollution, traffic,
        lighting, carbon, risk
    ])

# Convert to dataframe
df = pd.DataFrame(data, columns=[
    "location", "latitude", "longitude",
    "crime_rate", "pollution_level", "traffic_density",
    "lighting_score", "carbon_factor", "risk_label"
])

# Save CSV
df.to_csv("delhi_safety_dataset.csv", index=False)

print("Dataset Generated Successfully!")

