# train_model.py

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE

# Load dataset
df = pd.read_csv("delhi_safety_dataset.csv")

print(f"Loaded {len(df)} samples")

# Features
feature_cols = ['crime_rate', 'pollution_level', 'traffic_density', 
                'lighting_score', 'carbon_factor', 'hour_of_day', 
                'is_night', 'is_weekend']

X = df[feature_cols]
y = df['risk_label']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# SMOTE
sm = SMOTE(random_state=42)
X_train, y_train = sm.fit_resample(X_train, y_train)

# Train
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

print("\nTraining model...")
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("\n" + "="*60)
print("MODEL EVALUATION")
print("="*60)
print(classification_report(y_test, y_pred, target_names=['Safe', 'Moderate', 'Risky']))

# Save
joblib.dump(model, "risk_model.pkl")
joblib.dump(feature_cols, "feature_columns.pkl")

print("\n✅ Model saved to model/risk_model.pkl")