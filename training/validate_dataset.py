"""
validate_dataset.py — Architectural Dataset Validator
Validates raw and processed floor-plan samples against the standard schema & geometry rules.
"""

from typing import Dict, Any, List, Tuple

ROOM_VOCABULARY = [
    "living_room",
    "bedroom",
    "master_bedroom",
    "bathroom",
    "kitchen",
    "dining_room",
    "corridor",
    "entrance",
    "staircase",
    "balcony",
    "parking",
    "storage",
    "study",
    "utility",
    "garden",
]

# Vocabulary alias mappings for flexible data ingestion
VOCAB_ALIASES = {
    "bedroom_1": "master_bedroom",
    "bedroom_2": "bedroom",
    "bedroom_3": "bedroom",
    "bedroom_4": "bedroom",
    "bathroom_1": "bathroom",
    "bathroom_2": "bathroom",
    "bathroom_3": "bathroom",
    "foyer": "entrance",
    "garage_parking": "parking",
    "garage": "parking",
    "home_office": "study",
}


def normalize_room_type(raw_type: str) -> str:
    """Maps a raw room type string to the standard room vocabulary."""
    cleaned = str(raw_type).strip().lower().replace(" ", "_")
    if cleaned in ROOM_VOCABULARY:
        return cleaned
    if cleaned in VOCAB_ALIASES:
        return VOCAB_ALIASES[cleaned]
    # Default fallback mapping
    if "bed" in cleaned:
        return "bedroom"
    if "bath" in cleaned or "toilet" in cleaned:
        return "bathroom"
    if "park" in cleaned or "garage" in cleaned:
        return "parking"
    if "office" in cleaned or "study" in cleaned:
        return "study"
    return "living_room"


def validate_sample(sample: Dict[str, Any], tolerance: float = 1.0) -> Tuple[bool, List[str]]:
    """
    Validates a single floor-plan record.
    Returns (is_valid, list_of_issues).
    """
    issues = []

    if not isinstance(sample, dict):
        return False, ["Sample must be a dictionary."]

    # Validate plot geometry & requirements
    reqs = sample.get("requirements", sample.get("plot", {}))
    plot_width = float(reqs.get("plot_width", reqs.get("width", 0.0)))
    plot_length = float(reqs.get("plot_length", reqs.get("length", 0.0)))
    floors = int(reqs.get("floors", 1))

    if plot_width <= 0:
        issues.append(f"Invalid plot width: {plot_width}")
    if plot_length <= 0:
        issues.append(f"Invalid plot length: {plot_length}")
    if floors < 1:
        issues.append(f"Invalid floor count: {floors}")

    rooms = sample.get("rooms", [])
    if not isinstance(rooms, list) or len(rooms) == 0:
        issues.append("Sample contains no room layout entries.")
        return False, issues

    # Validate individual room geometry
    for idx, room in enumerate(rooms):
        r_name = room.get("name", room.get("type", f"room_{idx}"))
        r_type = room.get("type", "bedroom")
        norm_type = normalize_room_type(r_type)

        x = float(room.get("x", 0.0))
        y = float(room.get("y", 0.0))
        w = float(room.get("width", 0.0))
        h = float(room.get("height", 0.0))
        fl = int(room.get("floor", 1))

        if w <= 0 or h <= 0:
            issues.append(f"Room '{r_name}' has non-positive dimensions ({w} x {h}).")
        if x < 0 or y < 0:
            issues.append(f"Room '{r_name}' has negative coordinates ({x}, {y}).")

        # Containment check
        if plot_width > 0 and (x + w) > (plot_width + tolerance):
            issues.append(f"Room '{r_name}' extends beyond plot width ({x + w:.1f} > {plot_width}).")
        if plot_length > 0 and (y + h) > (plot_length + tolerance):
            issues.append(f"Room '{r_name}' extends beyond plot length ({y + h:.1f} > {plot_length}).")

        if fl < 1 or fl > floors:
            issues.append(f"Room '{r_name}' assigned to invalid floor {fl} (total floors: {floors}).")

    is_valid = len(issues) == 0
    return is_valid, issues


def validate_dataset_records(dataset: List[Dict[str, Any]]) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Validates a list of floor-plan samples.
    Returns (valid_count, invalid_count, valid_samples).
    """
    valid_samples = []
    invalid_count = 0

    for sample in dataset:
        is_valid, _ = validate_sample(sample)
        if is_valid:
            valid_samples.append(sample)
        else:
            invalid_count += 1

    return len(valid_samples), invalid_count, valid_samples


if __name__ == "__main__":
    test_sample = {
        "requirements": {"plot_width": 50, "plot_length": 60, "floors": 2},
        "rooms": [
            {"type": "living_room", "x": 2, "y": 2, "width": 16, "height": 14, "floor": 1},
            {"type": "master_bedroom", "x": 20, "y": 2, "width": 14, "height": 12, "floor": 2},
        ]
    }
    valid, errs = validate_sample(test_sample)
    print(f"Validation Result: Valid={valid}, Errors={errs}")
