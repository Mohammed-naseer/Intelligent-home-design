"""
Floor-Plan Generator Model - AI House Architect
PyTorch Spatial Neural Network (Encoder-Decoder Architecture)
Generates structured 2D room bounding boxes (x, y, width, height, floor) from design requirements.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, List


MAX_ROOMS = 12
ROOM_FEATURES = 6  # norm_x, norm_y, norm_w, norm_h, floor, exists_prob


class FloorPlanGeneratorNet(nn.Module):
    """
    Encoder-Decoder Spatial Neural Network for Residential Layout Generation.
    Input: [plot_w_norm, plot_l_norm, floors_norm, bedrooms_norm, bathrooms_norm, style_onehot(4)]
    Output: Tensor of shape (batch, MAX_ROOMS, ROOM_FEATURES)
    """

    def __init__(self, in_features: int = 9, max_rooms: int = MAX_ROOMS):
        super().__init__()
        self.max_rooms = max_rooms

        # Requirement Encoder
        self.encoder = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
        )

        # Room Bounding Box Decoder
        self.decoder = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, max_rooms * ROOM_FEATURES),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        latent = self.encoder(x)
        out = self.decoder(latent)
        out = out.view(batch_size, self.max_rooms, ROOM_FEATURES)
        # Apply Sigmoid to coordinates and existence probability to keep within [0, 1] range
        coords = torch.sigmoid(out[:, :, :4])
        floors = torch.sigmoid(out[:, :, 4:5])
        active = torch.sigmoid(out[:, :, 5:6])
        return torch.cat([coords, floors, active], dim=-1)


def encode_requirements(req: Dict[str, Any]) -> torch.Tensor:
    """Encodes raw requirement dictionary into normalized tensor input."""
    plot_w = req.get("plot_width", req.get("plot", {}).get("width", 50.0)) / 150.0
    plot_l = req.get("plot_length", req.get("plot", {}).get("length", 50.0)) / 150.0
    floors = req.get("floors", 1) / 4.0

    rooms = req.get("rooms", {})
    if isinstance(rooms, dict):
        beds = rooms.get("bedrooms", 3) / 10.0
        baths = rooms.get("bathrooms", 2) / 10.0
    else:
        beds = req.get("bedrooms", 3) / 10.0
        baths = req.get("bathrooms", 2) / 10.0

    style = req.get("architectural_style", req.get("style", "modern"))
    styles = ["modern", "contemporary", "traditional", "minimalist"]
    onehot_style = [1.0 if style == s else 0.0 for s in styles]

    vec = [plot_w, plot_l, floors, beds, baths] + onehot_style
    return torch.tensor([vec], dtype=torch.float32)
