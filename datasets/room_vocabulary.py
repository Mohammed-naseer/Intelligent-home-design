"""
room_vocabulary.py — Canonical Room Vocabulary for AI House Architect
======================================================================
Central source of truth for all room type definitions, aliases, and
minimum dimensional constraints. All preprocessing, training, inference,
and validation modules import from this file — never define room types
locally in individual scripts.

To add a new room type:
  1. Add the canonical name to ROOM_VOCABULARY.
  2. Add its minimum dimensions to ROOM_MIN_DIMENSIONS.
  3. Optionally add aliases to VOCAB_ALIASES.
"""

from typing import Dict, List, Optional, Tuple

# ── Canonical Room Vocabulary ─────────────────────────────────────────────────
# Ordered list of canonical room type identifiers.
# The index in this list is used as the integer encoding during training.
ROOM_VOCABULARY: List[str] = [
    "living_room",       # 0
    "bedroom",           # 1
    "master_bedroom",    # 2
    "bathroom",          # 3
    "kitchen",           # 4
    "dining_room",       # 5
    "corridor",          # 6
    "entrance",          # 7
    "staircase",         # 8
    "balcony",           # 9
    "parking",           # 10
    "storage",           # 11
    "study",             # 12
    "utility",           # 13
    "garden",            # 14
]

NUM_ROOM_TYPES: int = len(ROOM_VOCABULARY)

# ── Integer Encoding Lookup ───────────────────────────────────────────────────
ROOM_TYPE_TO_IDX: Dict[str, int] = {rt: i for i, rt in enumerate(ROOM_VOCABULARY)}
IDX_TO_ROOM_TYPE: Dict[int, str] = {i: rt for i, rt in enumerate(ROOM_VOCABULARY)}

# ── Vocabulary Alias Map ──────────────────────────────────────────────────────
# Maps non-canonical strings to their canonical equivalents.
# Used when ingesting external datasets with varying naming conventions.
VOCAB_ALIASES: Dict[str, str] = {
    # Bedroom variants
    "bedroom_1": "master_bedroom",
    "bedroom_2": "bedroom",
    "bedroom_3": "bedroom",
    "bedroom_4": "bedroom",
    "bedroom_5": "bedroom",
    "master_bed": "master_bedroom",
    "master bed": "master_bedroom",
    "bed room": "bedroom",
    # Bathroom variants
    "bathroom_1": "bathroom",
    "bathroom_2": "bathroom",
    "bathroom_3": "bathroom",
    "bath": "bathroom",
    "toilet": "bathroom",
    "wc": "bathroom",
    "powder_room": "bathroom",
    # Entrance / foyer
    "foyer": "entrance",
    "entry": "entrance",
    "lobby": "entrance",
    "porch": "entrance",
    "verandah": "entrance",
    # Parking
    "garage_parking": "parking",
    "garage": "parking",
    "carport": "parking",
    # Study / office
    "home_office": "study",
    "office": "study",
    "library": "study",
    # Kitchen
    "kitchen_dining": "kitchen",
    # Dining
    "dining": "dining_room",
    # Living
    "living": "living_room",
    "family_room": "living_room",
    "lounge": "living_room",
    "drawing_room": "living_room",
    # Utility / laundry
    "laundry": "utility",
    "laundry_room": "utility",
    "mud_room": "utility",
    # Storage
    "closet": "storage",
    "pantry": "storage",
    "store": "storage",
    "storeroom": "storage",
    # Corridor / hallway
    "hallway": "corridor",
    "hall": "corridor",
    "passage": "corridor",
    # Balcony / terrace
    "terrace": "balcony",
    "deck": "balcony",
    "patio": "balcony",
}

# ── Minimum / Maximum Room Dimensions (feet) ──────────────────────────────────
# Format: (min_width, max_width, min_height, max_height)
ROOM_MIN_DIMENSIONS: Dict[str, Tuple[float, float, float, float]] = {
    "living_room":    (12.0, 28.0, 10.0, 24.0),
    "bedroom":        ( 9.0, 16.0,  9.0, 15.0),
    "master_bedroom": (11.0, 20.0, 11.0, 18.0),
    "bathroom":       ( 5.0, 10.0,  4.5,  9.0),
    "kitchen":        ( 8.0, 16.0,  7.0, 14.0),
    "dining_room":    ( 9.0, 18.0,  8.0, 15.0),
    "corridor":       ( 3.5,  7.0,  6.0, 24.0),
    "entrance":       ( 5.0, 12.0,  5.0, 12.0),
    "staircase":      ( 6.0, 12.0,  5.0, 12.0),
    "balcony":        ( 4.0, 10.0,  6.0, 18.0),
    "parking":        (10.0, 22.0, 14.0, 24.0),
    "storage":        ( 4.0,  8.0,  4.0,  8.0),
    "study":          ( 8.0, 14.0,  8.0, 14.0),
    "utility":        ( 5.0,  9.0,  5.0,  9.0),
    "garden":         (10.0, 50.0, 10.0, 50.0),
}

# Default dimensions for any room type not in the dictionary above
DEFAULT_MIN_DIMENSIONS: Tuple[float, float, float, float] = (8.0, 14.0, 8.0, 14.0)

# ── Room Color Palette (for visualization) ────────────────────────────────────
# Hex colors for Matplotlib 2D floor plan rendering
ROOM_COLORS: Dict[str, str] = {
    "living_room":    "#FFD580",   # warm amber
    "bedroom":        "#A8D8EA",   # soft blue
    "master_bedroom": "#7EC8E3",   # medium blue
    "bathroom":       "#B5EAD7",   # mint green
    "kitchen":        "#FFC8A2",   # peach
    "dining_room":    "#FFDAC1",   # light orange
    "corridor":       "#E8E8E8",   # neutral grey
    "entrance":       "#FFB7B2",   # soft red
    "staircase":      "#C7CEEA",   # lavender
    "balcony":        "#C7F2A4",   # light green
    "parking":        "#D4D4D4",   # medium grey
    "storage":        "#E2CFC4",   # light brown
    "study":          "#B5B9FF",   # periwinkle
    "utility":        "#FFFFBA",   # pale yellow
    "garden":         "#90EE90",   # green
}
DEFAULT_COLOR: str = "#F0F0F0"


# ── Utility Functions ─────────────────────────────────────────────────────────

def normalize_room_type(raw_type: str) -> str:
    """
    Maps any raw room type string to the canonical vocabulary.

    Resolution priority:
      1. Direct match in ROOM_VOCABULARY
      2. Alias lookup in VOCAB_ALIASES
      3. Substring heuristic fallback
      4. Default to 'living_room' (safest fallback)

    Args:
        raw_type: Raw room type string from any data source.

    Returns:
        Canonical room type string guaranteed to be in ROOM_VOCABULARY.
    """
    if not isinstance(raw_type, str):
        return "living_room"

    cleaned = raw_type.strip().lower().replace(" ", "_").replace("-", "_")

    # 1. Direct canonical match
    if cleaned in ROOM_TYPE_TO_IDX:
        return cleaned

    # 2. Alias lookup
    if cleaned in VOCAB_ALIASES:
        return VOCAB_ALIASES[cleaned]

    # 3. Substring heuristic
    if "master" in cleaned and "bed" in cleaned:
        return "master_bedroom"
    if "bed" in cleaned:
        return "bedroom"
    if "bath" in cleaned or "toilet" in cleaned or "wc" in cleaned:
        return "bathroom"
    if "park" in cleaned or "garage" in cleaned or "car" in cleaned:
        return "parking"
    if "office" in cleaned or "study" in cleaned or "library" in cleaned:
        return "study"
    if "stair" in cleaned:
        return "staircase"
    if "corridor" in cleaned or "hall" in cleaned or "passage" in cleaned:
        return "corridor"
    if "balcon" in cleaned or "terrace" in cleaned or "deck" in cleaned:
        return "balcony"
    if "kitchen" in cleaned:
        return "kitchen"
    if "dining" in cleaned:
        return "dining_room"
    if "living" in cleaned or "lounge" in cleaned or "drawing" in cleaned:
        return "living_room"
    if "storage" in cleaned or "store" in cleaned or "closet" in cleaned:
        return "storage"
    if "utility" in cleaned or "laundry" in cleaned:
        return "utility"
    if "garden" in cleaned or "yard" in cleaned:
        return "garden"
    if "entrance" in cleaned or "entry" in cleaned or "foyer" in cleaned:
        return "entrance"

    # 4. Default fallback
    return "living_room"


def encode_room_type(room_type: str) -> int:
    """Returns the integer index for a canonical room type."""
    canonical = normalize_room_type(room_type)
    return ROOM_TYPE_TO_IDX.get(canonical, 0)


def decode_room_type(idx: int) -> str:
    """Returns the canonical room type string for an integer index."""
    return IDX_TO_ROOM_TYPE.get(idx, "living_room")


def get_room_color(room_type: str) -> str:
    """Returns the hex color for a given room type (for visualization)."""
    canonical = normalize_room_type(room_type)
    return ROOM_COLORS.get(canonical, DEFAULT_COLOR)


def get_room_min_dimensions(room_type: str) -> Tuple[float, float, float, float]:
    """Returns (min_w, max_w, min_h, max_h) in feet for a given room type."""
    canonical = normalize_room_type(room_type)
    return ROOM_MIN_DIMENSIONS.get(canonical, DEFAULT_MIN_DIMENSIONS)


def is_valid_room_type(raw_type: str) -> bool:
    """Returns True if the raw type maps to a known canonical vocabulary entry."""
    canonical = normalize_room_type(raw_type)
    return canonical in ROOM_TYPE_TO_IDX


if __name__ == "__main__":
    print(f"Room vocabulary ({NUM_ROOM_TYPES} types):")
    for idx, rt in IDX_TO_ROOM_TYPE.items():
        dims = ROOM_MIN_DIMENSIONS.get(rt, DEFAULT_MIN_DIMENSIONS)
        print(f"  [{idx:2d}] {rt:<20} min: {dims[0]}x{dims[2]}ft  max: {dims[1]}x{dims[3]}ft")
