def compute_overall_risk(df):

    df = df.copy()

    df["overall_risk_score"] = (
        df["crime_rate"] * 0.4 +
        df["pollution_level"] * 0.15 +
        df["traffic_density"] * 0.2 +
        (1 - df["lighting_score"]) * 0.15 +
        df["carbon_factor"] * 0.1
    )
    return df["overall_risk_score"]


