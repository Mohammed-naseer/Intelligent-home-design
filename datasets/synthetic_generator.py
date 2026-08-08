"""
Synthetic Floor-Plan Dataset Generator - AI House Architect
Generates structured training samples for residential floor plan generation and quality scoring.
Enables offline training of Deep Learning spatial layout models and ML quality regressors.
"""

import os
import json
import random
from typing import List, Dict, Any


ROOM_TYPES = [
    "living_room",
    "master_bedroom",
    "bedroom_2",
    "bedroom_3",
    "kitchen",
    "dining_room",
    "bathroom_1",
    "bathroom_2",
    "foyer",
    "corridor",
    "staircase",
    "balcony",
    "garage_parking",
    "home_office",
]

MIN_MAX_DIMENSIONS = {
    "living_room": (14.0, 24.0, 12.0, 20.0),
    "master_bedroom": (12.0, 18.0, 12.0, 16.0),
    "bedroom_2": (10.0, 14.0, 10.0, 14.0),
    "bedroom_3": (10.0, 14.0, 10.0, 14.0),
    "kitchen": (9.0, 14.0, 8.0, 12.0),
    "dining_room": (10.0, 16.0, 10.0, 14.0),
    "bathroom_1": (6.0, 9.0, 5.0, 8.0),
    "bathroom_2": (5.0, 8.0, 5.0, 7.0),
    "foyer": (6.0, 10.0, 6.0, 10.0),
    "corridor": (4.0, 6.0, 8.0, 20.0),
    "staircase": (7.0, 12.0, 6.0, 10.0),
    "balcony": (4.0, 8.0, 8.0, 16.0),
    "garage_parking": (12.0, 20.0, 16.0, 22.0),
    "home_office": (10.0, 14.0, 9.0, 13.0),
}


def generate_synthetic_layout(sample_id: int) -> Dict[str, Any]:
    """Generates a single realistic residential layout dataset entry."""
    plot_width = float(random.choice([30, 40, 45, 50, 60, 70, 80, 100]))
    plot_length = float(random.choice([40, 50, 60, 70, 80, 90, 100]))
    floors = random.choice([1, 2, 3])
    bedrooms = random.choice([2, 3, 4, 5])
    bathrooms = random.choice([2, 3, 4])
    style = random.choice(["modern", "contemporary", "traditional", "minimalist"])

    # Required rooms setup
    rooms = []
    current_x = 2.0
    current_y = 2.0
    current_floor = 1

    room_specs = [
        ("living_room", 1),
        ("kitchen", 1),
        ("dining_room", 1),
        ("master_bedroom", 1 if floors == 1 else 2),
        ("bathroom_1", 1),
        ("garage_parking", 1),
    ]

    for b in range(2, bedrooms + 1):
        fl = 1 if b == 2 and floors == 1 else random.choice(range(1, floors + 1))
        room_specs.append((f"bedroom_{b}", fl))

    for bt in range(2, bathrooms + 1):
        fl = random.choice(range(1, floors + 1))
        room_specs.append((f"bathroom_{bt}", fl))

    if floors > 1:
        room_specs.append(("staircase", 1))

    # Grid placement simulation per floor
    floor_bounds = {f: {"x": 2.0, "y": 2.0, "max_h": 0.0} for f in range(1, floors + 1)}

    for r_type, fl in room_specs:
        min_w, max_w, min_h, max_h = MIN_MAX_DIMENSIONS.get(r_type, (10.0, 14.0, 10.0, 14.0))
        w = round(random.uniform(min_w, max_w), 1)
        h = round(random.uniform(min_h, max_h), 1)

        f_state = floor_bounds[fl]
        if f_state["x"] + w > plot_width - 2.0:
            f_state["x"] = 2.0
            f_state["y"] += f_state["max_h"] + 2.0
            f_state["max_h"] = 0.0

        if f_state["y"] + h > plot_length - 2.0:
            # Wrap or clamp inside plot
            f_state["y"] = max(2.0, plot_length - h - 2.0)

        x = round(f_state["x"], 1)
        y = round(f_state["y"], 1)

        f_state["x"] += w + 1.0
        f_state["max_h"] = max(f_state["max_h"], h)

        rooms.append({
            "name": r_type.replace("_", " ").title(),
            "type": r_type,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "floor": fl,
            "doors": [{"connects_to": "corridor", "wall": "south"}],
            "windows": [{"wall": "north", "width": 4.0}],
        })

    # Calculate metrics for ground truth label
    total_room_area = sum(r["width"] * r["height"] for r in rooms)
    total_plot_area = plot_width * plot_length * floors
    space_utilization = min(98.0, round((total_room_area / total_plot_area) * 100.0 + random.uniform(10, 30), 1))
    connectivity = round(random.uniform(80.0, 96.0), 1)
    circulation = round(random.uniform(82.0, 97.0), 1)
    natural_light = round(random.uniform(78.0, 95.0), 1)
    furniture_fit = round(random.uniform(85.0, 98.0), 1)
    privacy = round(random.uniform(80.0, 95.0), 1)
    requirement_match = round(random.uniform(88.0, 99.0), 1)

    overall_score = round(
        0.20 * space_utilization +
        0.15 * connectivity +
        0.15 * circulation +
        0.15 * natural_light +
        0.15 * furniture_fit +
        0.10 * privacy +
        0.10 * requirement_match,
        1
    )

    return {
        "sample_id": f"sample_{sample_id:04d}",
        "requirements": {
            "plot_width": plot_width,
            "plot_length": plot_length,
            "floors": floors,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "style": style,
        },
        "rooms": rooms,
        "metrics": {
            "space_utilization": space_utilization,
            "connectivity": connectivity,
            "circulation": circulation,
            "natural_light": natural_light,
            "furniture_fit": furniture_fit,
            "privacy": privacy,
            "requirement_match": requirement_match,
            "overall_score": overall_score,
        }
    }


def generate_dataset(output_dir: str, num_samples: int = 500) -> str:
    """Generates synthetic dataset JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    dataset_file = os.path.join(output_dir, "floorplan_dataset.json")

    samples = [generate_synthetic_layout(i) for i in range(1, num_samples + 1)]
    with open(dataset_file, "w") as f:
        json.dump(samples, f, indent=2)

    return dataset_file


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "processed")
    file_path = generate_dataset(out_path, 300)
    print(f"Generated synthetic dataset with 300 samples at {file_path}")
