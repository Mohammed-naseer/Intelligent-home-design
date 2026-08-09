"""
layout_model.py — PyTorch Floor-Plan Generator Network
=======================================================
Encoder → Latent Representation → Room Layout Decoder

Architecture
------------
  Input: structured requirement tensor (plot size, floors, room counts, style)
  Encoder: MLP → 256-dim latent vector
  Decoder: MLP → (MAX_ROOMS × SPATIAL_FEATURES) + room type classification head

Output per room slot:
  - norm_x, norm_y: position (normalized to [0, 1] w.r.t. plot dimensions)
  - norm_width, norm_height: dimensions (normalized)
  - norm_floor: floor assignment (normalized)
  - exists_prob: probability that this room slot is occupied
  - room_type_logits: NUM_ROOM_TYPES logits for room type classification

The model is designed to handle variable numbers of rooms by outputting
a fixed-size tensor of MAX_ROOMS room slots, with the existence head
indicating which slots are active.

Backward Compatibility
----------------------
  The standalone encode_requirements() function remains unchanged so that
  existing inference and API code continues to work.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Any, Dict, List, Optional, Tuple

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_ROOMS: int = 15         # Maximum room slots per sample
SPATIAL_FEATURES: int = 6   # norm_x, norm_y, norm_w, norm_h, norm_floor, exists_prob
ROOM_FEATURES: int = SPATIAL_FEATURES  # Alias kept for backward compat

# Architectural styles — must match encode_requirements() one-hot encoding
STYLE_VOCABULARY: List[str] = ["modern", "contemporary", "traditional", "minimalist"]

# Import NUM_ROOM_TYPES safely to avoid circular imports
try:
    from datasets.room_vocabulary import NUM_ROOM_TYPES as _NUM_ROOM_TYPES
    NUM_ROOM_TYPES: int = _NUM_ROOM_TYPES
except ImportError:
    NUM_ROOM_TYPES: int = 15  # fallback if vocabulary not installed


# ── Model Architecture ────────────────────────────────────────────────────────

class FloorPlanGeneratorNet(nn.Module):
    """
    Encoder-Decoder Spatial Neural Network for Residential Layout Generation.

    Input tensor shape: (batch, in_features)
    Output:
      - spatial_out:  (batch, MAX_ROOMS, SPATIAL_FEATURES)   ← spatial predictions
      - type_logits:  (batch, MAX_ROOMS, NUM_ROOM_TYPES)     ← room type classification

    The two outputs can be accessed as a tuple from forward(), or individually
    via predict_spatial() and predict_types() for inference.

    Args:
        in_features:     Size of the input requirement vector.
        max_rooms:       Maximum number of room slots to predict.
        num_room_types:  Number of canonical room type classes.
        latent_dim:      Size of the latent representation vector.
        dropout:         Dropout probability in the encoder (0 = disabled).
    """

    def __init__(
        self,
        in_features: int = 9,
        max_rooms: int = MAX_ROOMS,
        num_room_types: int = NUM_ROOM_TYPES,
        latent_dim: int = 256,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.max_rooms = max_rooms
        self.num_room_types = num_room_types
        self.spatial_features = SPATIAL_FEATURES

        # ── Requirement Encoder ──────────────────────────────────────────────
        self.encoder = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, latent_dim),
            nn.ReLU(),
        )

        # ── Spatial Decoder ──────────────────────────────────────────────────
        # Predicts (x, y, w, h, floor, exists) for each room slot
        self.spatial_decoder = nn.Sequential(
            nn.Linear(latent_dim, 512),
            nn.ReLU(),
            nn.Linear(512, max_rooms * SPATIAL_FEATURES),
        )

        # ── Room Type Classification Head ─────────────────────────────────────
        # Predicts room type logits for each room slot
        self.type_head = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Linear(256, max_rooms * num_room_types),
        )

    def forward(
        self, x: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.

        Args:
            x: Input tensor of shape (batch, in_features)

        Returns:
            spatial_out:  (batch, max_rooms, SPATIAL_FEATURES)
                          All values in [0, 1] via sigmoid.
            type_logits:  (batch, max_rooms, num_room_types)
                          Raw logits — apply softmax for probabilities.
        """
        batch_size = x.size(0)
        latent = self.encoder(x)  # (batch, latent_dim)

        # Spatial output
        spatial_raw = self.spatial_decoder(latent)                     # (batch, max_rooms*6)
        spatial_out = torch.sigmoid(spatial_raw.view(batch_size, self.max_rooms, SPATIAL_FEATURES))

        # Room type logits
        type_raw = self.type_head(latent)                              # (batch, max_rooms*num_types)
        type_logits = type_raw.view(batch_size, self.max_rooms, self.num_room_types)

        return spatial_out, type_logits

    def predict(
        self, x: torch.Tensor
    ) -> torch.Tensor:
        """
        Backward-compatible single-tensor output (spatial only).
        Used by existing inference code that expects a (batch, MAX_ROOMS, 6) tensor.
        """
        spatial_out, _ = self.forward(x)
        return spatial_out


# ── Requirement Encoder ───────────────────────────────────────────────────────

def encode_requirements(req: Dict[str, Any]) -> torch.Tensor:
    """
    Encodes a raw requirement dictionary into a normalized input tensor.

    This function is the primary interface between user requirements and
    the model. It must remain backward-compatible with existing API callers.

    Input formats supported:
      - {"plot_width": 50, "plot_length": 60, "floors": 2, "bedrooms": 3, ...}
      - {"plot": {"width": 50, "length": 60}, "floors": 2, "rooms": {...}, ...}

    Returns:
        torch.Tensor of shape (1, 9) — ready for model inference.
    """
    # Plot dimensions
    plot = req.get("plot", {})
    plot_w = float(req.get("plot_width",  plot.get("width",  50.0))) / 150.0
    plot_l = float(req.get("plot_length", plot.get("length", 50.0))) / 150.0

    # Floor count
    floors = float(req.get("floors", 1)) / 4.0

    # Room counts (support both flat and nested formats)
    rooms_dict = req.get("rooms", {})
    if isinstance(rooms_dict, dict):
        beds  = float(rooms_dict.get("bedrooms",  3)) / 10.0
        baths = float(rooms_dict.get("bathrooms", 2)) / 10.0
    else:
        beds  = float(req.get("bedrooms",  3)) / 10.0
        baths = float(req.get("bathrooms", 2)) / 10.0

    # Architectural style (one-hot encoding)
    style = str(req.get("architectural_style", req.get("style", "modern"))).lower()
    onehot_style = [1.0 if style == s else 0.0 for s in STYLE_VOCABULARY]

    vec = [plot_w, plot_l, floors, beds, baths] + onehot_style
    return torch.tensor([vec], dtype=torch.float32)


def encode_requirements_extended(req: Dict[str, Any]) -> torch.Tensor:
    """
    Extended requirement encoder with additional features.
    Used by the improved training script for richer representations.

    Returns:
        torch.Tensor of shape (1, 13) including kitchen, parking, living_room counts.
    """
    base = encode_requirements(req).squeeze(0).tolist()  # 9 features

    rooms_dict = req.get("rooms", {})
    if isinstance(rooms_dict, dict):
        kitchen  = float(rooms_dict.get("kitchen",     1)) / 3.0
        parking  = float(rooms_dict.get("parking",     1)) / 5.0
        balcony  = float(rooms_dict.get("balcony",     0)) / 5.0
        home_off = float(rooms_dict.get("home_office", 0))
    else:
        kitchen  = float(req.get("kitchen",  1)) / 3.0
        parking  = float(req.get("parking",  1)) / 5.0
        balcony  = float(req.get("balcony",  0)) / 5.0
        home_off = float(req.get("home_office", 0))

    vec = base + [kitchen, parking, balcony, home_off]
    return torch.tensor([vec], dtype=torch.float32)
