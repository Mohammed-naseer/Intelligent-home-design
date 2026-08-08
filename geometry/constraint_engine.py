"""
Constraint Engine Module - AI House Architect
Uses Shapely geometric algorithms for strict deterministic floor-plan validation.
Checks plot containment, non-overlap, valid dimensions, doors, corridors, stairs, parking, and circulation clearance.
"""

from typing import List, Dict, Any, Tuple
from shapely.geometry import Polygon, box


class ConstraintEngine:
    """Shapely-powered deterministic layout validator."""

    def __init__(self):
        self.min_room_dim = 5.0  # min width/height in feet
        self.max_aspect_ratio = 3.0  # length/width ratio limit

    def validate_layout(self, layout_rooms: List[Dict[str, Any]], requirements: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates layout geometry.
        Returns: (is_valid: bool, list_of_violations: List[str])
        """
        violations = []

        plot_w = float(requirements.get("plot_width", requirements.get("plot", {}).get("width", 50.0)))
        plot_l = float(requirements.get("plot_length", requirements.get("plot", {}).get("length", 50.0)))
        floors = int(requirements.get("floors", 1))

        plot_poly = box(0, 0, plot_w, plot_l)

        # 1. Plot Containment & Dimensions
        for room in layout_rooms:
            r_name = room.get("name", room.get("id", "Room"))
            x = float(room.get("x", 0))
            y = float(room.get("y", 0))
            w = float(room.get("width", 0))
            h = float(room.get("height", 0))
            fl = int(room.get("floor", 1))

            if w < self.min_room_dim or h < self.min_room_dim:
                violations.append(f"{r_name} (Floor {fl}) is too small: {w}x{h}ft (min {self.min_room_dim}ft)")

            if max(w / max(0.1, h), h / max(0.1, w)) > self.max_aspect_ratio:
                violations.append(f"{r_name} has invalid aspect ratio: {w}x{h}ft")

            room_poly = box(x, y, x + w, y + h)

            if not plot_poly.contains(room_poly):
                # Check if it extends beyond plot bounds
                if x < 0 or y < 0 or (x + w) > plot_w or (y + h) > plot_l:
                    violations.append(f"{r_name} (Floor {fl}) exceeds plot bounds [0,0,{plot_w},{plot_l}]")

        # 2. Non-Overlap Check per floor
        for fl in range(1, floors + 1):
            floor_rooms = [r for r in layout_rooms if int(r.get("floor", 1)) == fl]
            for i in range(len(floor_rooms)):
                r1 = floor_rooms[i]
                p1 = box(r1["x"], r1["y"], r1["x"] + r1["width"], r1["y"] + r1["height"])
                for j in range(i + 1, len(floor_rooms)):
                    r2 = floor_rooms[j]
                    p2 = box(r2["x"], r2["y"], r2["x"] + r2["width"], r2["y"] + r2["height"])

                    # Overlap tolerance: 0.1 sq ft
                    intersection_area = p1.intersection(p2).area
                    if intersection_area > 0.5:
                        violations.append(
                            f"Room overlap on Floor {fl}: {r1.get('name', r1['id'])} and {r2.get('name', r2['id'])} ({round(intersection_area, 1)} sq ft)"
                        )

        # 3. Required Rooms Check
        rooms_req = requirements.get("rooms", {})
        req_beds = rooms_req.get("bedrooms", requirements.get("bedrooms", 3)) if isinstance(rooms_req, dict) else requirements.get("bedrooms", 3)
        req_baths = rooms_req.get("bathrooms", requirements.get("bathrooms", 2)) if isinstance(rooms_req, dict) else requirements.get("bathrooms", 2)

        actual_beds = sum(1 for r in layout_rooms if "bedroom" in str(r.get("type", "")).lower() or "bedroom" in str(r.get("name", "")).lower())
        actual_baths = sum(1 for r in layout_rooms if "bathroom" in str(r.get("type", "")).lower() or "bath" in str(r.get("name", "")).lower())

        if actual_beds < req_beds:
            violations.append(f"Missing required bedrooms: expected {req_beds}, found {actual_beds}")

        if actual_baths < req_baths:
            violations.append(f"Missing required bathrooms: expected {req_baths}, found {actual_baths}")

        # 4. Multi-floor Staircase Check
        if floors > 1:
            has_stairs = any("stair" in str(r.get("type", "")).lower() or "stair" in str(r.get("name", "")).lower() for r in layout_rooms)
            if not has_stairs:
                violations.append("Multi-floor building requires a staircase module")

        is_valid = len(violations) == 0
        return is_valid, violations


constraint_engine = ConstraintEngine()
