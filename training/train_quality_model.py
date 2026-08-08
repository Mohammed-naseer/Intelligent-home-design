"""
Train Quality Model Script - AI House Architect
Trains the Scikit-Learn QualityPredictorModel on generated architectural metrics.
Saves regressor model to models/quality_model/quality_regressor.pkl.
"""

import os
import json
import numpy as np
from datasets.synthetic_generator import generate_dataset
from models.quality_model import QualityPredictorModel


def prepare_quality_data(dataset_path: str):
    """Prepares feature matrix X (layout attributes) and target matrix Y (quality metrics)."""
    with open(dataset_path, "r") as f:
        data = json.load(f)

    X_list = []
    Y_list = []

    for item in data:
        req = item["requirements"]
        rooms = item["rooms"]
        metrics = item["metrics"]

        plot_area = req["plot_width"] * req["plot_length"] * req["floors"]
        room_count = len(rooms)
        total_room_area = sum(r["width"] * r["height"] for r in rooms)
        util_ratio = total_room_area / max(1.0, plot_area)

        # Feature vector: [util_ratio, room_count, plot_width, plot_length, floors, bedrooms, bathrooms]
        x_feat = [
            util_ratio,
            room_count,
            req["plot_width"],
            req["plot_length"],
            req["floors"],
            req["bedrooms"],
            req["bathrooms"],
        ]

        # Target metrics
        y_metrics = [
            metrics["space_utilization"],
            metrics["connectivity"],
            metrics["circulation"],
            metrics["natural_light"],
            metrics["furniture_fit"],
            metrics["privacy"],
            metrics["requirement_match"],
            metrics["overall_score"],
        ]

        X_list.append(x_feat)
        Y_list.append(y_metrics)

    return np.array(X_list, dtype=np.float32), np.array(Y_list, dtype=np.float32)


def train_quality_model():
    """Trains scikit-learn random forest quality regressor."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, "datasets", "processed")
    dataset_path = os.path.join(dataset_dir, "floorplan_dataset.json")

    if not os.path.exists(dataset_path):
        dataset_path = generate_dataset(dataset_dir, num_samples=400)

    X, Y = prepare_quality_data(dataset_path)
    print(f"Loaded quality dataset tensors: X shape {X.shape}, Y shape {Y.shape}")

    model_dir = os.path.join(base_dir, "models", "quality_model")
    save_path = os.path.join(model_dir, "quality_regressor.pkl")

    predictor = QualityPredictorModel()
    predictor.fit_and_save(X, Y, save_path)
    print(f"Successfully trained and saved quality predictor to: {save_path}")
    return save_path


if __name__ == "__main__":
    train_quality_model()
