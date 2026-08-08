"""
Quality Predictor Inference Module - AI House Architect
Loads trained Scikit-Learn quality model to score candidate floor plans.
"""

import os
import numpy as np
from typing import Dict, Any, List
from models.quality_model import QualityPredictorModel


class QualityPredictor:
    """Inference wrapper for layout quality model."""

    def __init__(self, model_path: str = None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "quality_model", "quality_regressor.pkl")

        self.model_path = model_path
        self.predictor = QualityPredictorModel(model_path=model_path)

    def predict(self, layout: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, float]:
        """Calculates feature vector for layout and evaluates design quality metrics."""
        rooms = layout.get("rooms", [])
        plot_w = float(requirements.get("plot_width", requirements.get("plot", {}).get("width", 50.0)))
        plot_l = float(requirements.get("plot_length", requirements.get("plot", {}).get("length", 50.0)))
        floors = int(requirements.get("floors", 1))

        plot_area = plot_w * plot_l * floors
        total_room_area = sum(r.get("width", 0) * r.get("height", 0) for r in rooms)
        util_ratio = total_room_area / max(1.0, plot_area)

        beds = requirements.get("bedrooms", 3)
        baths = requirements.get("bathrooms", 2)

        x_feat = np.array([
            util_ratio,
            len(rooms),
            plot_w,
            plot_l,
            floors,
            beds,
            baths,
        ], dtype=np.float32)

        return self.predictor.predict(x_feat)


quality_predictor = QualityPredictor()
