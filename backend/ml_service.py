import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import random

class MLService:
    def __init__(self):
        # Mock training data for demonstration
        # Features: [device_density, time_of_day (hour), dist_to_exit, terrain_difficulty (0-1)]
        X_train = np.array([
            [10, 14, 50, 0.1],  # Low risk
            [50, 20, 100, 0.2], # Medium risk
            [90, 21, 200, 0.8], # High risk
            [20, 12, 20, 0.1],  # Low risk
            [80, 22, 150, 0.7]  # High risk
        ])
        # Labels: 0=Low, 1=Medium, 2=High
        y_train = np.array([0, 1, 2, 0, 2])

        self.model = RandomForestClassifier(n_estimators=10)
        self.model.fit(X_train, y_train)

    def predict_crowd_risk(self, density: int, hour: int, dist_exit: int, terrain: float) -> str:
        """
        Predicts crowd risk level based on input features.
        """
        features = np.array([[density, hour, dist_exit, terrain]])
        prediction = self.model.predict(features)[0]
        risk_map = {0: "Low", 1: "Medium", 2: "High"}
        return risk_map.get(prediction, "Unknown")

    def generate_heatmap_data(self):
        """
        Generates mock heatmap data for the frontend.
        Returns a list of points with lat, lng, and intensity.
        """
        # ACL Festival Area (Zilker Park) approx coordinates
        base_lat = 30.2672
        base_lng = -97.7731

        heatmap_data = []
        for _ in range(50):
            lat_offset = random.uniform(-0.005, 0.005)
            lng_offset = random.uniform(-0.005, 0.005)
            intensity = random.uniform(0.1, 1.0) # 1.0 is highest density
            heatmap_data.append({
                "lat": base_lat + lat_offset,
                "lng": base_lng + lng_offset,
                "weight": intensity
            })
        return heatmap_data

    def get_safe_route(self, start_lat, start_lng, end_lat, end_lng):
        """
        Mock safe route generation.
        In a real app, this would use graph algorithms avoiding high-risk zones.
        Here we just return a direct line with a "safe waypoint".
        """
        mid_lat = (start_lat + end_lat) / 2 + 0.001 # Slight detour
        mid_lng = (start_lng + end_lng) / 2 + 0.001

        return [
            {"lat": start_lat, "lng": start_lng},
            {"lat": mid_lat, "lng": mid_lng}, # Safe waypoint
            {"lat": end_lat, "lng": end_lng}
        ]
