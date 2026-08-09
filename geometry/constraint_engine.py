"""
constraint_engine.py — Architectural Layout Constraint Validator
================================================================
Uses Shapely geometric algorithms for strict deterministic floor-plan
validation. Returns a structured result including a composite validity
score, enabling downstream systems to compare and rank competing layouts.

Checks
------
  ✓ Room inside plot boundary
  ✓ No room overlap on same floor (tolerance 0.5 sq ft)
  ✓ Minimum room dimensions per room type
  ✓ Maximum aspect ratio
  ✓ Required rooms exist (bedrooms, bathrooms)
  ✓ Valid floor assignment
  ✓ Floor consistency (rooms on floor N require floor N-1)
  ✓ Multi-floor staircase presence
  ✓ Minimum area per room type

Output Format
-------------
  {
    "valid": True,
    "violations": [],
    "score": 0.94,
    "details": { ... }
  }

  or:

  {
    "valid": False,
    "violations": [
      "Bedroom 2 overlaps Bathroom on Floor 1 (12.4 sq ft)",
      "Kitchen exceeds plot boundary [0,0,50,60]"
    ],
    "score": 0.61,
    "details": { ... }
  }
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from shapely.geometry import box

logger = logging.getLogger(__name__)

# ── Minimum Room Dimensions ───────────────────────────────────────────────────
# Loaded from vocabulary when available; hardcoded fallback for robustness.
try:
    from datasets.room_vocabulary import ROOM_MIN_DIMENSIONS, normalize_room_type
    _vocab_available = True
except ImportError:
    _vocab_available = False
    ROOM_MIN_DIMENSIONS = {}

    def normalize_room_type(t: str) -> str:  # type: ignore[misc]
        return t.strip().lower().replace(" ", "_")


_FALLBACK_MIN_DIM = 5.0   # feet — absolute minimum width/height for any room
_MAX_ASPECT_RATIO = 3.5   # length/width ratio limit


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_min_dim(room_type: str) -> float:
    """Returns the minimum allowed dimension (width AND height) for a room type."""
    if _vocab_available:
        dims = ROOM_MIN_DIMENSIONS.get(normalize_room_type(room_type))
        if dims:
            return dims[0]  # min_width (same constraint applied to height)
    return _FALLBACK_MIN_DIM


def _get_min_area(room_type: str) -> float:
    """Returns the minimum allowed area (sq ft) for a room type."""
    if _vocab_available:
        dims = ROOM_MIN_DIMENSIONS.get(normalize_room_type(room_type))
        if dims:
            min_w, _, min_h, _ = dims
            return min_w * min_h
    return _FALLBACK_MIN_DIM ** 2


def _room_label(room: Dict[str, Any]) -> str:
    """Returns a display label for a room."""
    return room.get("name", room.get("id", room.get("type", "Room")))


# ── Main Validator ────────────────────────────────────────────────────────────

class ConstraintEngine:
    """
    Shapely-powered deterministic layout validator with composite scoring.

    Each check contributes to the validity score. Weights are designed so that
    a layout with only minor issues can still achieve a score > 0 while
    a layout that fails hard constraints scores near 0.
    """

    def __init__(self) -> None:
        self.min_room_dim:    float = _FALLBACK_MIN_DIM
        self.max_aspect_ratio: float = _MAX_ASPECT_RATIO

    # ── Public API ────────────────────────────────────────────────────────────

    def validate(
        self,
        layout_rooms: List[Dict[str, Any]],
        requirements: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validates layout geometry and requirement satisfaction.

        Args:
            layout_rooms:  List of room dictionaries.
            requirements:  User requirement dictionary.

        Returns:
            {
                "valid":      bool,
                "violations": List[str],
                "score":      float,     # 0.0 (terrible) – 1.0 (perfect)
                "details":    Dict,      # per-check results
            }
        """
        violations: List[str] = []
        details: Dict[str, Any] = {}

        # Parse plot
        plot = requirements.get("plot", {})
        plot_w = float(
            requirements.get("plot_width",  plot.get("width",  50.0))
        )
        plot_l = float(
            requirements.get("plot_length", plot.get("length", 60.0))
        )
        floors = int(requirements.get("floors", 1))
        plot_poly = box(0, 0, plot_w, plot_l)

        # ── Check 1: Plot Containment & Minimum Dimensions ───────────────────
        containment_violations: List[str] = []
        dimension_violations:   List[str] = []

        for room in layout_rooms:
            label = _room_label(room)
            rt    = normalize_room_type(room.get("type", "living_room"))
            x     = float(room.get("x", 0))
            y     = float(room.get("y", 0))
            w     = float(room.get("width", 0))
            h     = float(room.get("height", 0))
            fl    = int(room.get("floor", 1))

            # Dimension check
            min_dim  = _get_min_dim(rt)
            min_area = _get_min_area(rt)

            if w < min_dim or h < min_dim:
                dimension_violations.append(
                    f"{label} (Floor {fl}) is too small: {w:.1f}×{h:.1f} ft "
                    f"(min {min_dim:.0f} ft per side)"
                )

            if w * h < min_area * 0.9:     # 10% tolerance on area
                dimension_violations.append(
                    f"{label} (Floor {fl}) area too small: {w*h:.0f} sq ft "
                    f"(min ~{min_area:.0f} sq ft for {rt})"
                )

            if w > 0 and h > 0:
                aspect = max(w / h, h / w)
                if aspect > self.max_aspect_ratio:
                    dimension_violations.append(
                        f"{label} (Floor {fl}) has invalid aspect ratio: "
                        f"{w:.1f}×{h:.1f} (max ratio {self.max_aspect_ratio})"
                    )

            # Containment check using Shapely
            if w > 0 and h > 0:
                room_poly = box(x, y, x + w, y + h)
                if not plot_poly.buffer(0.5).contains(room_poly):
                    containment_violations.append(
                        f"{label} (Floor {fl}) exceeds plot bounds "
                        f"[0,0,{plot_w:.0f},{plot_l:.0f}]: "
                        f"room at ({x:.1f},{y:.1f}) size {w:.1f}×{h:.1f}"
                    )

        violations.extend(containment_violations)
        violations.extend(dimension_violations)
        details["containment_violations"] = len(containment_violations)
        details["dimension_violations"]   = len(dimension_violations)

        # ── Check 2: Non-Overlap per Floor ───────────────────────────────────
        overlap_violations: List[str] = []
        for fl in range(1, floors + 1):
            floor_rooms = [r for r in layout_rooms if int(r.get("floor", 1)) == fl]
            for i in range(len(floor_rooms)):
                r1 = floor_rooms[i]
                w1, h1 = float(r1.get("width", 0)), float(r1.get("height", 0))
                if w1 <= 0 or h1 <= 0:
                    continue
                p1 = box(r1["x"], r1["y"], r1["x"] + w1, r1["y"] + h1)
                for j in range(i + 1, len(floor_rooms)):
                    r2 = floor_rooms[j]
                    w2, h2 = float(r2.get("width", 0)), float(r2.get("height", 0))
                    if w2 <= 0 or h2 <= 0:
                        continue
                    p2 = box(r2["x"], r2["y"], r2["x"] + w2, r2["y"] + h2)
                    overlap_area = p1.intersection(p2).area
                    if overlap_area > 0.5:
                        overlap_violations.append(
                            f"Room overlap on Floor {fl}: "
                            f"{_room_label(r1)} and {_room_label(r2)} "
                            f"({overlap_area:.1f} sq ft)"
                        )

        violations.extend(overlap_violations)
        details["overlap_violations"] = len(overlap_violations)

        # ── Check 3: Required Rooms ───────────────────────────────────────────
        requirement_violations: List[str] = []
        rooms_dict = requirements.get("rooms", {})
        if isinstance(rooms_dict, dict):
            req_beds  = int(rooms_dict.get("bedrooms",  requirements.get("bedrooms",  0)))
            req_baths = int(rooms_dict.get("bathrooms", requirements.get("bathrooms", 0)))
        else:
            req_beds  = int(requirements.get("bedrooms",  0))
            req_baths = int(requirements.get("bathrooms", 0))

        actual_types = [normalize_room_type(r.get("type", "")) for r in layout_rooms]
        actual_beds  = sum(1 for t in actual_types if "bedroom" in t)
        actual_baths = sum(1 for t in actual_types if "bathroom" in t)

        if req_beds > 0 and actual_beds < req_beds:
            requirement_violations.append(
                f"Missing bedrooms: required {req_beds}, found {actual_beds}"
            )
        if req_baths > 0 and actual_baths < req_baths:
            requirement_violations.append(
                f"Missing bathrooms: required {req_baths}, found {actual_baths}"
            )

        violations.extend(requirement_violations)
        details["requirement_violations"] = len(requirement_violations)
        details["rooms_found"] = {
            "bedrooms":  actual_beds,
            "bathrooms": actual_baths,
        }

        # ── Check 4: Floor Validity ───────────────────────────────────────────
        floor_violations: List[str] = []
        active_floors = sorted(set(int(r.get("floor", 1)) for r in layout_rooms))

        for r in layout_rooms:
            fl = int(r.get("floor", 1))
            if fl < 1 or fl > floors:
                floor_violations.append(
                    f"{_room_label(r)} is on floor {fl} "
                    f"(valid floors: 1–{floors})"
                )

        # Floor consistency: if floor N exists, floor N-1 must exist
        for fl in active_floors:
            if fl > 1 and (fl - 1) not in active_floors:
                floor_violations.append(
                    f"Floor {fl} has rooms but floor {fl-1} is empty "
                    f"(floor continuity violation)"
                )

        violations.extend(floor_violations)
        details["floor_violations"] = len(floor_violations)

        # ── Check 5: Multi-floor Staircase ────────────────────────────────────
        stair_violations: List[str] = []
        if floors > 1:
            has_stairs = any("stair" in str(r.get("type", "")).lower() for r in layout_rooms)
            if not has_stairs:
                stair_violations.append(
                    "Multi-floor building requires at least one staircase"
                )
        violations.extend(stair_violations)
        details["stair_violations"] = len(stair_violations)

        # ── Composite Score ───────────────────────────────────────────────────
        # Each penalty category reduces the score proportionally.
        n_rooms = max(1, len(layout_rooms))
        score = 1.0

        # Containment: -0.15 per violation, max deduction 0.45
        score -= min(0.45, len(containment_violations) * 0.15)
        # Overlap: -0.10 per pair, max 0.40
        score -= min(0.40, len(overlap_violations) * 0.10)
        # Dimension: -0.05 per violation, max 0.20
        score -= min(0.20, len(dimension_violations) * 0.05)
        # Requirements: -0.10 per missing room type
        score -= min(0.20, len(requirement_violations) * 0.10)
        # Floor: -0.05 per violation
        score -= min(0.15, len(floor_violations) * 0.05)
        # Staircase: -0.05 if missing
        score -= 0.05 * len(stair_violations)

        score = round(max(0.0, min(1.0, score)), 3)

        is_valid = (
            len(containment_violations) == 0 and
            len(overlap_violations) == 0 and
            len(requirement_violations) == 0 and
            len(floor_violations) == 0 and
            len(stair_violations) == 0
        )

        return {
            "valid":      is_valid,
            "violations": violations,
            "score":      score,
            "details":    details,
        }

    def validate_layout(
        self,
        layout_rooms: List[Dict[str, Any]],
        requirements: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Backward-compatible interface returning (is_valid, violations).

        Existing callers that use:
            is_valid, violations = constraint_engine.validate_layout(...)
        continue to work unchanged.
        """
        result = self.validate(layout_rooms, requirements)
        return result["valid"], result["violations"]


# ── Module-level singleton ────────────────────────────────────────────────────
constraint_engine = ConstraintEngine()


if __name__ == "__main__":
    # Quick smoke test
    test_rooms = [
        {"id": "r1", "type": "living_room",    "x":  2, "y":  2, "width": 18, "height": 14, "floor": 1},
        {"id": "r2", "type": "kitchen",        "x": 22, "y":  2, "width": 12, "height": 10, "floor": 1},
        {"id": "r3", "type": "master_bedroom", "x":  2, "y":  2, "width": 16, "height": 14, "floor": 2},
        {"id": "r4", "type": "bedroom",        "x": 20, "y":  2, "width": 13, "height": 12, "floor": 2},
        {"id": "r5", "type": "bathroom",       "x": 35, "y":  2, "width":  7, "height":  6, "floor": 1},
        {"id": "r6", "type": "staircase",      "x": 35, "y": 10, "width":  8, "height": 10, "floor": 1},
    ]
    test_req = {
        "plot_width": 50, "plot_length": 60,
        "floors": 2, "bedrooms": 2, "bathrooms": 1,
    }

    import json
    result = constraint_engine.validate(test_rooms, test_req)
    print(json.dumps(result, indent=2))
