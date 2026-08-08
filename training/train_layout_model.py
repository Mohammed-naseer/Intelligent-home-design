"""
Train Layout Model Script - AI House Architect
Trains the PyTorch FloorPlanGeneratorNet using synthetic/processed architectural floor plan dataset.
Saves model weights to models/layout_model/pytorch_layout_model.pt.
"""

import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from datasets.synthetic_generator import generate_dataset
from models.layout_model import FloorPlanGeneratorNet, encode_requirements, MAX_ROOMS, ROOM_FEATURES


def prepare_dataset_tensors(dataset_path: str):
    """Loads dataset and prepares input requirement tensors and target room coordinates."""
    with open(dataset_path, "r") as f:
        data = json.load(f)

    X_list = []
    Y_list = []

    for item in data:
        req = item["requirements"]
        rooms = item["rooms"]

        x_vec = encode_requirements(req).squeeze(0)

        # Target room tensor (MAX_ROOMS, ROOM_FEATURES)
        y_tensor = torch.zeros((MAX_ROOMS, ROOM_FEATURES), dtype=torch.float32)
        plot_w = req["plot_width"]
        plot_l = req["plot_length"]
        floors = req["floors"]

        for idx, room in enumerate(rooms[:MAX_ROOMS]):
            norm_x = min(1.0, max(0.0, room["x"] / plot_w))
            norm_y = min(1.0, max(0.0, room["y"] / plot_l))
            norm_w = min(1.0, max(0.0, room["width"] / plot_w))
            norm_h = min(1.0, max(0.0, room["height"] / plot_l))
            norm_fl = min(1.0, max(0.0, room["floor"] / max(1, floors)))
            exists = 1.0

            y_tensor[idx] = torch.tensor([norm_x, norm_y, norm_w, norm_h, norm_fl, exists])

        X_list.append(x_vec)
        Y_list.append(y_tensor)

    return torch.stack(X_list), torch.stack(Y_list)


def train_layout_model(epochs: int = 50, batch_size: int = 16):
    """Executes training loop and exports PyTorch layout model weights."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, "datasets", "processed")
    dataset_path = os.path.join(dataset_dir, "floorplan_dataset.json")

    if not os.path.exists(dataset_path):
        print("Dataset not found. Generating synthetic dataset...")
        dataset_path = generate_dataset(dataset_dir, num_samples=400)

    X, Y = prepare_dataset_tensors(dataset_path)
    print(f"Loaded training tensors: X shape {X.shape}, Y shape {Y.shape}")

    model = FloorPlanGeneratorNet(in_features=X.shape[1], max_rooms=MAX_ROOMS)
    optimizer = optim.Adam(model.parameters(), lr=0.003)
    criterion = nn.MSELoss()

    dataset_size = X.size(0)
    model.train()

    for epoch in range(1, epochs + 1):
        permutation = torch.randperm(dataset_size)
        epoch_loss = 0.0

        for i in range(0, dataset_size, batch_size):
            indices = permutation[i : i + batch_size]
            batch_x, batch_y = X[indices], Y[indices]

            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item() * batch_x.size(0)

        avg_loss = epoch_loss / dataset_size
        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch [{epoch}/{epochs}] - Loss: {avg_loss:.6f}")

    save_dir = os.path.join(base_dir, "models", "layout_model")
    os.makedirs(save_dir, exist_ok=True)
    model_save_path = os.path.join(save_dir, "pytorch_layout_model.pt")
    torch.save(model.state_dict(), model_save_path)
    print(f"Successfully trained and saved PyTorch layout model to: {model_save_path}")
    return model_save_path


if __name__ == "__main__":
    train_layout_model(epochs=30)
