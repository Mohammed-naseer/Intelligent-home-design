"""
data_format.py — Canonical Internal Data Format for AI House Architect
=======================================================================
Defines the standard representation used throughout the training pipeline.
All raw data (synthetic or from public datasets) MUST be converted to this
format before training. All model outputs are expected in this format.

Canonical Sample Structure
--------------------------
{
  "sample_id": "sample_0001",
  "plot": {
    "width": 60.0,          # feet, absolute
    "length": 50.0          # feet, absolute
  },
  "floors": 2,
  "requirements": {         # user-facing design requirements
    "bedrooms": 3,
    "bathrooms": 2,
    "kitchen": 1,
    "living_room": 1,
    "parking": 1,
    "style": "modern"
  },
  "rooms": [
    {
      "id": 1,
      "type": "living_room",   # canonical room type
      "type_idx": 0,           # integer encoding (matches room_vocabulary.py)
      "floor": 1,
      "x": 2.0,               # left edge, feet (absolute)
      "y": 2.0,               # bottom edge, feet (absolute)
      "width": 18.0,          # feet (absolute)
      "height": 14.0,         # feet (absolute)
      "norm_x": 0.033,        # x / plot_width
      "norm_y": 0.040,        # y / plot_length
      "norm_width": 0.300,    # width / plot_width
      "norm_height": 0.280,   # height / plot_length
      "norm_floor": 0.5,      # floor / total_floors
      "area_sqft": 252.0,
      "doors": [],            # optional
      "windows": []           # optional
    }
  ],
  "connections": [            # room adjacency edges
    {"from": "living_room", "to": "kitchen"},
    {"from": "living_room", "to": "corridor"}
  ],
  "adjacency_matrix": [       # NxN matrix, N = len(rooms)
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0]
  ],
  "metrics": {                # optional ground truth quality metrics
    "space_utilization": 87.3,
    "overall_score": 88.5
  }
}
"""

from typing import Any, Dict, List, Optional, Tuple
import logging

from datasets.room_vocabulary import (
    normalize_room_type,
    encode_room_type,
    NUM_ROOM_TYPES,
)

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
CANONICAL_VERSION: str = "1.0"

# Minimum valid plot dimensions
MIN_PLOT_WIDTH: float = 15.0   # feet
MIN_PLOT_LENGTH: float = 15.0  # feet
MAX_PLOT_WIDTH: float = 300.0  # feet
MAX_PLOT_LENGTH: float = 300.0 # feet

# Maximum rooms per sample for model tensor sizing
MAX_ROOMS_PER_SAMPLE: int = 20


# ── Canonical Sample Validation ───────────────────────────────────────────────

def _extract_plot(sample: Dict[str, Any]) -> Tuple[float, float]:
    """
    Extract plot width and length from various source formats.
    Supports both ``requirements.plot_width`` and ``plot.width`` formats.
    """
    # Format A: {"requirements": {"plot_width": ..., "plot_length": ...}}
    reqs = sample.get("requirements", {})
    if "plot_width" in reqs and "plot_length" in reqs:
        return float(reqs["plot_width"]), float(reqs["plot_length"])

    # Format B: {"plot": {"width": ..., "length": ...}}
    plot = sample.get("plot", {})
    if "width" in plot and "length" in plot:
        return float(plot["width"]), float(plot["length"])

    # Format C: top-level keys
    if "plot_width" in sample and "plot_length" in sample:
        return float(sample["plot_width"]), float(sample["plot_length"])

    return 0.0, 0.0


def _extract_requirements(sample: Dict[str, Any]) -> Dict[str, Any]:
    """Extract user requirements from various source formats."""
    reqs = sample.get("requirements", {})
    return {
        "bedrooms":   int(reqs.get("bedrooms", 3)),
        "bathrooms":  int(reqs.get("bathrooms", 2)),
        "kitchen":    int(reqs.get("kitchen", 1)),
        "living_room":int(reqs.get("living_room", 1)),
        "parking":    int(reqs.get("parking", reqs.get("garage", 0))),
        "style":      str(reqs.get("style", reqs.get("architectural_style", "modern"))),
        "floors":     int(reqs.get("floors", sample.get("floors", 1))),
    }


def _build_adjacency_matrix(rooms: List[Dict[str, Any]]) -> List[List[int]]:
    """
    Builds a binary adjacency matrix from explicit connections or
    from spatial proximity (rooms sharing a wall edge within a tolerance).
    """
    n = len(rooms)
    matrix = [[0] * n for _ in range(n)]

    # Spatial proximity: two rooms are "adjacent" if they share an edge
    # (their bounding boxes are within 1.5 ft of each other on the same floor)
    ADJACENCY_TOLERANCE = 1.5

    for i in range(n):
        for j in range(i + 1, n):
            ri, rj = rooms[i], rooms[j]
            # Only check rooms on the same floor
            if ri.get("floor", 1) != rj.get("floor", 1):
                continue

            xi1, yi1 = ri["x"], ri["y"]
            xi2, yi2 = xi1 + ri["width"], yi1 + ri["height"]
            xj1, yj1 = rj["x"], rj["y"]
            xj2, yj2 = xj1 + rj["width"], yj1 + rj["height"]

            # Check horizontal adjacency: rooms share a vertical edge
            h_adj = (abs(xi2 - xj1) < ADJACENCY_TOLERANCE or
                     abs(xj2 - xi1) < ADJACENCY_TOLERANCE)
            # Y ranges overlap
            y_overlap = not (yi2 <= yj1 or yj2 <= yi1)

            # Check vertical adjacency: rooms share a horizontal edge
            v_adj = (abs(yi2 - yj1) < ADJACENCY_TOLERANCE or
                     abs(yj2 - yi1) < ADJACENCY_TOLERANCE)
            # X ranges overlap
            x_overlap = not (xi2 <= xj1 or xj2 <= xi1)

            if (h_adj and y_overlap) or (v_adj and x_overlap):
                matrix[i][j] = 1
                matrix[j][i] = 1

    return matrix


def _build_connections(rooms: List[Dict[str, Any]],
                       adjacency_matrix: List[List[int]]) -> List[Dict[str, str]]:
    """Derives room connections list from adjacency matrix."""
    connections = []
    n = len(rooms)
    for i in range(n):
        for j in range(i + 1, n):
            if adjacency_matrix[i][j] == 1:
                connections.append({
                    "from": rooms[i]["type"],
                    "to":   rooms[j]["type"],
                })
    return connections


def canonicalize_sample(
    raw_sample: Dict[str, Any],
    sample_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Converts any supported raw sample format to the canonical internal format.

    Supports:
      - Existing NeuroArchAI synthetic generator format
      - Any dict with ``plot_width`` / ``plot_length`` top-level keys
      - Any dict with ``plot.width`` / ``plot.length`` nested keys

    Args:
        raw_sample:  Raw sample dictionary from any source.
        sample_id:   Optional override for the sample identifier.

    Returns:
        Canonical sample dictionary, or None if the sample is invalid.
    """
    try:
        plot_width, plot_length = _extract_plot(raw_sample)

        if plot_width < MIN_PLOT_WIDTH or plot_length < MIN_PLOT_LENGTH:
            logger.debug("Sample rejected: plot too small (%.1f x %.1f)", plot_width, plot_length)
            return None
        if plot_width > MAX_PLOT_WIDTH or plot_length > MAX_PLOT_LENGTH:
            logger.debug("Sample rejected: plot too large (%.1f x %.1f)", plot_width, plot_length)
            return None

        floors = int(raw_sample.get("floors", raw_sample.get("requirements", {}).get("floors", 1)))
        if floors < 1 or floors > 6:
            logger.debug("Sample rejected: invalid floor count %d", floors)
            return None

        raw_rooms = raw_sample.get("rooms", [])
        if not raw_rooms:
            logger.debug("Sample rejected: no rooms")
            return None

        canonical_rooms: List[Dict[str, Any]] = []
        for idx, room in enumerate(raw_rooms[:MAX_ROOMS_PER_SAMPLE]):
            raw_type = room.get("type", room.get("room_type", "living_room"))
            canonical_type = normalize_room_type(raw_type)
            type_idx = encode_room_type(canonical_type)

            x = float(room.get("x", 0.0))
            y = float(room.get("y", 0.0))
            w = float(room.get("width", room.get("w", 0.0)))
            h = float(room.get("height", room.get("h", room.get("depth", 0.0))))
            fl = int(room.get("floor", 1))

            if w <= 0 or h <= 0:
                continue

            canonical_rooms.append({
                "id":          idx + 1,
                "type":        canonical_type,
                "type_idx":    type_idx,
                "floor":       fl,
                "x":           round(x, 2),
                "y":           round(y, 2),
                "width":       round(w, 2),
                "height":      round(h, 2),
                "norm_x":      round(x / plot_width, 4),
                "norm_y":      round(y / plot_length, 4),
                "norm_width":  round(w / plot_width, 4),
                "norm_height": round(h / plot_length, 4),
                "norm_floor":  round(fl / max(1, floors), 4),
                "area_sqft":   round(w * h, 1),
                "doors":       room.get("doors", []),
                "windows":     room.get("windows", []),
            })

        if not canonical_rooms:
            logger.debug("Sample rejected: no valid rooms after processing")
            return None

        adjacency_matrix = _build_adjacency_matrix(canonical_rooms)
        connections = _build_connections(canonical_rooms, adjacency_matrix)
        requirements = _extract_requirements(raw_sample)

        sid = sample_id or raw_sample.get("sample_id", f"sample_{idx:04d}")

        return {
            "sample_id":        sid,
            "format_version":   CANONICAL_VERSION,
            "plot": {
                "width":  plot_width,
                "length": plot_length,
            },
            "floors":           floors,
            "requirements":     requirements,
            "rooms":            canonical_rooms,
            "connections":      connections,
            "adjacency_matrix": adjacency_matrix,
            "metrics":          raw_sample.get("metrics", {}),
        }

    except Exception as exc:
        logger.warning("canonicalize_sample error: %s", exc)
        return None


def sample_to_feature_dict(sample: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts a flat feature dictionary from a canonical sample.
    Useful for statistical analysis and DataFrame construction.
    """
    plot = sample.get("plot", {})
    rooms = sample.get("rooms", [])
    reqs = sample.get("requirements", {})
    return {
        "sample_id":      sample["sample_id"],
        "plot_width":     plot.get("width", 0),
        "plot_length":    plot.get("length", 0),
        "plot_area":      plot.get("width", 0) * plot.get("length", 0),
        "floors":         sample.get("floors", 1),
        "room_count":     len(rooms),
        "total_room_area":sum(r["area_sqft"] for r in rooms),
        "bedrooms":       reqs.get("bedrooms", 0),
        "bathrooms":      reqs.get("bathrooms", 0),
        "overall_score":  sample.get("metrics", {}).get("overall_score", None),
    }


if __name__ == "__main__":
    # Quick smoke test with a synthetic sample
    test_raw = {
        "sample_id": "test_001",
        "requirements": {
            "plot_width": 50.0,
            "plot_length": 60.0,
            "floors": 2,
            "bedrooms": 3,
            "bathrooms": 2,
            "style": "modern",
        },
        "rooms": [
            {"type": "living_room",    "x": 2,  "y": 2,  "width": 18, "height": 14, "floor": 1},
            {"type": "kitchen",        "x": 22, "y": 2,  "width": 12, "height": 10, "floor": 1},
            {"type": "master_bedroom", "x": 2,  "y": 2,  "width": 16, "height": 14, "floor": 2},
            {"type": "bedroom",        "x": 20, "y": 2,  "width": 13, "height": 12, "floor": 2},
            {"type": "bathroom",       "x": 35, "y": 2,  "width":  7, "height":  6, "floor": 1},
            {"type": "staircase",      "x": 35, "y": 10, "width":  8, "height": 10, "floor": 1},
        ],
    }

    result = canonicalize_sample(test_raw)
    if result:
        import json
        print("Canonical sample (first 2 rooms):")
        result_preview = dict(result)
        result_preview["rooms"] = result["rooms"][:2]
        print(json.dumps(result_preview, indent=2))
        print(f"\nTotal rooms: {len(result['rooms'])}")
        print(f"Connections: {result['connections']}")
    else:
        print("ERROR: canonicalization failed")
