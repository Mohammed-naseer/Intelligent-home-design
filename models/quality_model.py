"""
Layout Quality Prediction Model - AI House Architect
Scikit-Learn Machine Learning Quality Evaluator.
Predicts space utilization, connectivity, circulation, room size suitability, natural light, furniture fit, privacy, and overall design score.
"""

import os
import pickle
import numpy as np
from typing import Dict, Any, List


class QualityPredictorModel:
    """Scikit-Learn regression model predicting layout quality metrics."""

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.regressor = None

    def fit_and_save(self, X: np.ndarray, Y: np.ndarray, save_path: str):
        """Trains multi-output regressor on layout feature vectors."""
        from sklearn.ensemble import RandomForestRegressor

        self.regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.regressor.fit(X, Y)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            pickle.dump(self.regressor, f)
        self.model_path = save_path

    def load(self, model_path: str):
        """Loads trained regressor weights."""
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                self.regressor = pickle.load(f)
            self.model_path = model_path

    def predict(self, feature_vector: np.ndarray) -> Dict[str, float]:
        """Returns predicted quality breakdown and overall design score %."""
        if self.regressor is None and self.model_path and os.path.exists(self.model_path):
            self.load(self.model_path)

        if self.regressor is None:
            # Fallback heuristic calculation if model uninitialized
            return self._heuristic_prediction(feature_vector)

        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)

        preds = self.regressor.predict(feature_vector)[0]
        return {
            "space_utilization": round(float(preds[0]), 1),
            "connectivity": round(float(preds[1]), 1),
            "circulation": round(float(preds[2]), 1),
            "natural_light": round(float(preds[3]), 1),
            "furniture_fit": round(float(preds[4]), 1),
            "privacy": round(float(preds[5]), 1),
            "requirement_match": round(float(preds[6]), 1),
            "overall_score": round(float(preds[7]), 1),
        }

    def _heuristic_prediction(self, feat: np.ndarray) -> Dict[str, float]:
        """Calculates deterministic heuristic fallback scores."""
        vals = feat.flatten()
        ratio = vals[0] if len(vals) > 0 else 0.7
        space_util = min(96.0, max(70.0, ratio * 100.0))
        connectivity = round(85.0 + (ratio * 10.0), 1)
        circulation = round(88.0 + (ratio * 8.0), 1)
        natural_light = round(82.0 + (ratio * 12.0), 1)
        furniture_fit = round(87.0 + (ratio * 10.0), 1)
        privacy = round(84.0 + (ratio * 9.0), 1)
        requirement_match = round(90.0 + (ratio * 8.0), 1)
        overall = round(
            0.2 * space_util +
            0.15 * connectivity +
            0.15 * circulation +
            0.15 * natural_light +
            0.15 * furniture_fit +
            0.1 * privacy +
            0.1 * requirement_match,
            1
        )
        return {
            "space_utilization": round(space_util, 1),
            "connectivity": connectivity,
            "circulation": circulation,
            "natural_light": natural_light,
            "furniture_fit": furniture_fit,
            "privacy": privacy,
            "requirement_match": requirement_match,
            "overall_score": overall,
        }
