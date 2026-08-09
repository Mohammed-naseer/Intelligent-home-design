"""
Layout Generator Inference Module - AI House Architect
Uses the trained PyTorch FloorPlanGeneratorNet model to predict room coordinates, bounding boxes, and floor distributions.
"""

import os
import torch
import numpy as np
from typing import Dict, Any, List
from models.layout_model import FloorPlanGeneratorNet, encode_requirements, MAX_ROOMS, ROOM_FEATURES


class LayoutGenerator:
    """Inference engine loading PyTorch layout neural network."""

    def __init__(self, model_path: str = None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "layout_model", "pytorch_layout_model.pt")

        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        """Loads PyTorch state dict if present."""
        if os.path.exists(self.model_path):
            try:
                self.model = FloorPlanGeneratorNet(in_features=9, max_rooms=MAX_ROOMS)
                self.model.load_state_dict(torch.load(self.model_path, weights_only=True))
                self.model.eval()
            except Exception as e:
                print(f"Warning: Could not load PyTorch weights ({e}). Running in algorithmic fallback mode.")
                self.model = None

    def generate(self, requirements: Dict[str, Any], candidate_seed: int = 0) -> List[Dict[str, Any]]:
        """Generates raw candidate room bounding boxes."""
        plot_w = float(requirements.get("plot_width", requirements.get("plot", {}).get("width", 50.0)))
        plot_l = float(requirements.get("plot_length", requirements.get("plot", {}).get("length", 50.0)))
        floors = int(requirements.get("floors", 1))

        if self.model is not None:
            try:
                x_tensor = encode_requirements(requirements)
                torch.manual_seed(candidate_seed + 42)
                with torch.no_grad():
                    out = self.model(x_tensor)
                    if isinstance(out, tuple):
                        spatial_preds, type_logits = out
                        spatial_preds = spatial_preds.squeeze(0)  # (MAX_ROOMS, 6)
                        type_indices = type_logits.squeeze(0).argmax(dim=-1).numpy()  # (MAX_ROOMS,)
                    else:
                        spatial_preds = out.squeeze(0)
                        type_indices = np.zeros(MAX_ROOMS, dtype=int)

                from datasets.room_vocabulary import decode_room_type, get_room_color

                raw_rooms = []
                for idx in range(MAX_ROOMS):
                    row = spatial_preds[idx].numpy()
                    norm_x, norm_y, norm_w, norm_h, norm_fl, active = row
                    if active > 0.4:
                        x = round(float(norm_x * (plot_w - 10.0)), 1)
                        y = round(float(norm_y * (plot_l - 10.0)), 1)
                        w = max(6.0, round(float(norm_w * (plot_w * 0.4)), 1))
                        h = max(6.0, round(float(norm_h * (plot_l * 0.4)), 1))
                        fl = max(1, min(floors, int(round(norm_fl * floors + 0.5))))

                        room_type = decode_room_type(int(type_indices[idx])) if type_indices is not None else "room"
                        room_name = room_type.replace("_", " ").title()

                        raw_rooms.append({
                            "id": f"room_{idx+1}",
                            "type": room_type,
                            "name": room_name,
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "floor": fl,
                            "color": get_room_color(room_type),
                            "doors": [{"wall": "south", "connects_to": "corridor"}],
                            "windows": [{"wall": "north", "width": 4.0}],
                        })

                if raw_rooms:
                    return raw_rooms
            except Exception as e:
                print(f"Inference error: {e}. Falling back to deterministic procedural generation.")

        # Algorithmic fallback if model weights missing
        return self._procedural_generation(requirements, candidate_seed)

    def _procedural_generation(self, req: Dict[str, Any], seed: int) -> List[Dict[str, Any]]:
        """Deterministic architectural layout synthesis as baseline fallback."""
        np.random.seed(seed + 100)
        plot_w = float(req.get("plot_width", req.get("plot", {}).get("width", 50.0)))
        plot_l = float(req.get("plot_length", req.get("plot", {}).get("length", 50.0)))
        floors = int(req.get("floors", 1))

        rooms_req = req.get("rooms", {})
        if isinstance(rooms_req, dict):
            bedrooms = rooms_req.get("bedrooms", 3)
            bathrooms = rooms_req.get("bathrooms", 2)
            kitchen = rooms_req.get("kitchen", 1)
            parking = rooms_req.get("parking", 1)
        else:
            bedrooms = req.get("bedrooms", 3)
            bathrooms = req.get("bathrooms", 2)
            kitchen = req.get("kitchen", 1)
            parking = req.get("parking", 1)

        # Core room configuration
        room_list = [
            {"type": "living_room", "name": "Living Room", "w": 18.0, "h": 16.0, "floor": 1},
            {"type": "kitchen", "name": "Kitchen", "w": 12.0, "h": 10.0, "floor": 1},
            {"type": "dining_room", "name": "Dining Room", "w": 14.0, "h": 12.0, "floor": 1},
            {"type": "foyer", "name": "Foyer & Entry", "w": 8.0, "h": 8.0, "floor": 1},
        ]

        if parking > 0:
            room_list.append({"type": "garage_parking", "name": "Parking Garage", "w": 16.0, "h": 18.0, "floor": 1})

        if floors > 1:
            room_list.append({"type": "staircase", "name": "Staircase Tower", "w": 8.0, "h": 12.0, "floor": 1})

        for b in range(1, bedrooms + 1):
            fl = 1 if b == 1 and floors == 1 else (2 if floors > 1 and b > 1 else 1)
            rname = "Master Bedroom" if b == 1 else f"Bedroom {b}"
            w = 16.0 if b == 1 else 13.0
            h = 14.0 if b == 1 else 12.0
            room_list.append({"type": f"bedroom_{b}", "name": rname, "w": w, "h": h, "floor": fl})

        for bt in range(1, bathrooms + 1):
            fl = 1 if bt == 1 else (2 if floors > 1 else 1)
            room_list.append({"type": f"bathroom_{bt}", "name": f"Bathroom {bt}", "w": 7.0, "h": 6.0, "floor": fl})

        # Pack rooms onto plot grid per floor
        output_rooms = []
        for fl in range(1, floors + 1):
            floor_rooms = [r for r in room_list if r["floor"] == fl]
            cur_x = 2.0 + (seed % 3) * 1.5
            cur_y = 2.0 + ((seed * 2) % 3) * 1.5
            row_max_h = 0.0

            for idx, r in enumerate(floor_rooms):
                w = min(r["w"], plot_w - 4.0)
                h = min(r["h"], plot_l - 4.0)

                if cur_x + w > plot_w - 2.0:
                    cur_x = 2.0
                    cur_y += row_max_h + 1.5
                    row_max_h = 0.0

                if cur_y + h > plot_l - 2.0:
                    cur_y = max(2.0, plot_l - h - 2.0)

                output_rooms.append({
                    "id": f"{r['type']}_f{fl}_{idx}",
                    "name": r["name"],
                    "type": r["type"],
                    "x": round(cur_x, 1),
                    "y": round(cur_y, 1),
                    "width": round(w, 1),
                    "height": round(h, 1),
                    "floor": fl,
                    "doors": [{"wall": "south", "connects_to": "corridor"}],
                    "windows": [{"wall": "north", "width": 4.0}],
                })

                cur_x += w + 1.5
                row_max_h = max(row_max_h, h)

        return output_rooms


layout_generator = LayoutGenerator()
