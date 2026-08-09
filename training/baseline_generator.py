"""
baseline_generator.py — Deterministic Rule-Based Architectural Layout Generator
================================================================================
Produces floor plans from user requirements using deterministic architectural
rules. Does NOT use the trained model. Used to:

  1. Provide a comparison baseline for evaluating the ML model
  2. Generate initial layouts for constraint-based post-processing
  3. Serve as a fallback when no trained model is available

Design Principles
-----------------
  - Fully deterministic for any given requirements (no randomness)
  - Architecturally informed room placement (zone-based: public/private/service)
  - Correct multi-floor assignment (ground floor = public, upper = private)
  - All dimensions respect minimum size constraints from the room vocabulary
  - Does NOT hard-code positions — uses a zone-packing algorithm

Room Zones
----------
  Public   (floor 1):  living_room, kitchen, dining_room, parking
  Service  (floor 1):  bathroom, utility, storage, entrance
  Private  (floor 2+): bedroom, master_bedroom, study, balcony
  Vertical (all):      staircase, corridor

Usage
-----
  from training.baseline_generator import BaselineLayoutGenerator

  gen = BaselineLayoutGenerator()
  rooms = gen.generate({
      "plot_width": 50, "plot_length": 60, "floors": 2,
      "bedrooms": 3, "bathrooms": 2, "kitchen": 1, "parking": 1
  })
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from datasets.room_vocabulary import (
    ROOM_MIN_DIMENSIONS,
    DEFAULT_MIN_DIMENSIONS,
    normalize_room_type,
    get_room_color,
)


# ── Room Template ─────────────────────────────────────────────────────────────

def _room_size(room_type: str, scale: float = 1.0) -> Tuple[float, float]:
    """
    Returns a representative (width, height) for a room type.
    Uses the midpoint of the allowed dimensional range.

    Args:
        room_type: Canonical room type string.
        scale:     Scaling factor to compress rooms on smaller plots.
    """
    dims = ROOM_MIN_DIMENSIONS.get(room_type, DEFAULT_MIN_DIMENSIONS)
    min_w, max_w, min_h, max_h = dims
    w = round((min_w + max_w) / 2.0 * scale, 1)
    h = round((min_h + max_h) / 2.0 * scale, 1)
    # Enforce minimum dimensions
    w = max(min_w, w)
    h = max(min_h, h)
    return w, h


# ── Packing Engine ────────────────────────────────────────────────────────────

class FloorPacker:
    """
    Simple shelf-based 2D bin packing for room placement within a floor.

    Rooms are placed left-to-right, top-to-bottom, with a margin around
    the plot boundary. A new shelf is started when the current row is full.
    """

    def __init__(self, plot_width: float, plot_length: float, margin: float = 2.0) -> None:
        self.plot_w  = plot_width
        self.plot_l  = plot_length
        self.margin  = margin
        self.cur_x   = margin
        self.cur_y   = margin
        self.row_h   = 0.0          # Height of the current shelf
        self.usable_w = plot_width - 2 * margin
        self.usable_l = plot_length - 2 * margin

    def pack(self, w: float, h: float) -> Optional[Tuple[float, float]]:
        """
        Attempts to place a room of size (w, h).

        Returns:
            (x, y) position if successful, None if room cannot fit.
        """
        # Enforce the room fits within usable area at all
        if w > self.usable_w or h > self.usable_l:
            w = min(w, self.usable_w)
            h = min(h, self.usable_l)

        # Start a new shelf if this room doesn't fit on current row
        if self.cur_x + w > self.plot_w - self.margin:
            self.cur_x = self.margin
            self.cur_y += self.row_h + 1.5
            self.row_h = 0.0

        # Check vertical bounds
        if self.cur_y + h > self.plot_l - self.margin:
            # Clamp to fit
            self.cur_y = max(self.margin, self.plot_l - h - self.margin)
            if self.cur_y < self.margin:
                return None     # Room truly cannot fit

        x = round(self.cur_x, 1)
        y = round(self.cur_y, 1)

        self.cur_x += w + 1.5
        self.row_h = max(self.row_h, h)

        return x, y


# ── Baseline Layout Generator ─────────────────────────────────────────────────

class BaselineLayoutGenerator:
    """
    Deterministic rule-based residential layout generator.

    Implements zone-based room placement:
      - Ground floor (1): all public and service rooms
      - Upper floors (2+): all private rooms (bedrooms, study, balcony)
      - Multi-floor houses include staircase and corridor elements

    This is the BASELINE for comparison against the trained ML model.
    Its output quality represents the lower bound that the ML model must surpass.

    Key differences from the ML model:
      - Fully rule-based, no learned spatial patterns
      - Cannot adapt from training data
      - Always produces similar layouts for similar inputs
    """

    def __init__(self) -> None:
        # Scale factor applied to room sizes on smaller plots
        self._min_plot = 20.0

    def _scale_factor(self, plot_w: float, plot_l: float) -> float:
        """Computes a scaling factor based on available plot area."""
        area = plot_w * plot_l
        if area < 1200:
            return 0.70
        elif area < 2000:
            return 0.80
        elif area < 3600:
            return 0.90
        return 1.00

    def _build_room_program(
        self,
        plot_w: float,
        plot_l: float,
        floors: int,
        requirements: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Builds the full ordered list of rooms to place, with floor assignments.

        Returns:
            List of room spec dicts with 'type', 'floor', 'w', 'h' keys.
        """
        scale = self._scale_factor(plot_w, plot_l)
        reqs = requirements

        # Extract counts from nested or flat requirements
        rooms_dict = reqs.get("rooms", {})
        if isinstance(rooms_dict, dict):
            n_beds    = int(rooms_dict.get("bedrooms",   3))
            n_baths   = int(rooms_dict.get("bathrooms",  2))
            n_kitchen = int(rooms_dict.get("kitchen",    1))
            n_parking = int(rooms_dict.get("parking",    1))
            n_balcony = int(rooms_dict.get("balcony",    1 if floors > 1 else 0))
            has_office= bool(rooms_dict.get("home_office", False))
        else:
            n_beds    = int(reqs.get("bedrooms",  3))
            n_baths   = int(reqs.get("bathrooms", 2))
            n_kitchen = int(reqs.get("kitchen",   1))
            n_parking = int(reqs.get("parking",   1))
            n_balcony = int(reqs.get("balcony",   1 if floors > 1 else 0))
            has_office= bool(reqs.get("home_office", False))

        program: List[Dict[str, Any]] = []

        # ── Ground floor: Public zone ──────────────────────────────────────────
        lw, lh = _room_size("living_room", scale)
        program.append({"type": "living_room", "floor": 1, "w": lw, "h": lh})

        for _ in range(n_kitchen):
            kw, kh = _room_size("kitchen", scale)
            program.append({"type": "kitchen", "floor": 1, "w": kw, "h": kh})

        dw, dh = _room_size("dining_room", scale)
        program.append({"type": "dining_room", "floor": 1, "w": dw, "h": dh})

        ew, eh = _room_size("entrance", scale)
        program.append({"type": "entrance", "floor": 1, "w": ew, "h": eh})

        # ── Ground floor: Service zone ─────────────────────────────────────────
        # First bathroom is always on ground floor
        bw, bh = _room_size("bathroom", scale)
        program.append({"type": "bathroom", "floor": 1, "w": bw, "h": bh})

        if n_parking > 0:
            pw, ph = _room_size("parking", scale)
            program.append({"type": "parking", "floor": 1, "w": pw, "h": ph})

        # Staircase and corridor for multi-floor
        if floors > 1:
            sw, sh = _room_size("staircase", scale)
            program.append({"type": "staircase", "floor": 1, "w": sw, "h": sh})

            cw, ch = _room_size("corridor", scale)
            ch = min(ch, 5.0)   # Keep corridors slim
            program.append({"type": "corridor", "floor": 1, "w": cw, "h": ch})

        # ── Upper floors (or ground floor if single-story): Private zone ──────
        # Master bedroom
        private_floor = 2 if floors > 1 else 1
        mw, mh = _room_size("master_bedroom", scale)
        program.append({"type": "master_bedroom", "floor": private_floor, "w": mw, "h": mh})

        # Additional bedrooms
        for b_idx in range(1, n_beds):    # already placed master, so b_idx starts at 1
            fl = private_floor if floors <= 2 else (2 if b_idx < 3 else min(floors, 3))
            bew, beh = _room_size("bedroom", scale)
            program.append({"type": "bedroom", "floor": fl, "w": bew, "h": beh})

        # Additional bathrooms
        for bt_idx in range(1, n_baths):
            fl = private_floor
            btw, bth = _room_size("bathroom", scale)
            program.append({"type": "bathroom", "floor": fl, "w": btw, "h": bth})

        # Balconies on upper floors
        for _ in range(min(n_balcony, 2)):
            baw, bah = _room_size("balcony", scale)
            bah = min(bah, 8.0)     # Keep balconies shallow
            program.append({"type": "balcony", "floor": private_floor, "w": baw, "h": bah})

        # Home office
        if has_office:
            ow, oh = _room_size("study", scale)
            program.append({"type": "study", "floor": private_floor, "w": ow, "h": oh})

        # Upper floor corridor (if multi-floor)
        if floors > 1:
            cw2, ch2 = _room_size("corridor", scale)
            ch2 = min(ch2, 5.0)
            program.append({"type": "corridor", "floor": private_floor, "w": cw2, "h": ch2})

        return program

    def generate(
        self,
        requirements: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generates a complete floor plan using deterministic architectural rules.

        Args:
            requirements: User requirement dictionary.

        Returns:
            List of room dictionaries in the standard output format:
            Each room has: id, type, name, floor, x, y, width, height,
                           norm_x, norm_y, norm_width, norm_height, color
        """
        # Parse plot dimensions
        plot = requirements.get("plot", {})
        plot_w = float(requirements.get("plot_width",  plot.get("width",  50.0)))
        plot_l = float(requirements.get("plot_length", plot.get("length", 60.0)))
        floors = int(requirements.get("floors", 1))

        # Build room program
        program = self._build_room_program(plot_w, plot_l, floors, requirements)

        # Initialize one FloorPacker per floor
        packers: Dict[int, FloorPacker] = {
            fl: FloorPacker(plot_w, plot_l) for fl in range(1, floors + 1)
        }

        output_rooms: List[Dict[str, Any]] = []
        room_id = 1

        for spec in program:
            rt     = spec["type"]
            fl     = min(spec["floor"], floors)
            w      = float(spec["w"])
            h      = float(spec["h"])
            packer = packers[fl]

            pos = packer.pack(w, h)
            if pos is None:
                # Cannot fit — skip this room
                continue

            x, y = pos
            canonical_type = normalize_room_type(rt)
            display_name   = canonical_type.replace("_", " ").title()

            output_rooms.append({
                "id":          room_id,
                "type":        canonical_type,
                "name":        display_name,
                "floor":       fl,
                "x":           x,
                "y":           y,
                "width":       round(w, 1),
                "height":      round(h, 1),
                "norm_x":      round(x / plot_w, 4),
                "norm_y":      round(y / plot_l, 4),
                "norm_width":  round(w / plot_w, 4),
                "norm_height": round(h / plot_l, 4),
                "area_sqft":   round(w * h, 1),
                "color":       get_room_color(canonical_type),
                "source":      "baseline",
                "doors":       [{"wall": "south", "connects_to": "corridor"}],
                "windows":     [{"wall": "north", "width": 4.0}],
            })
            room_id += 1

        return output_rooms


# ── Module-level singleton ────────────────────────────────────────────────────
baseline_generator = BaselineLayoutGenerator()


if __name__ == "__main__":
    import json

    reqs = {
        "plot_width": 50,
        "plot_length": 60,
        "floors": 2,
        "bedrooms": 3,
        "bathrooms": 2,
        "kitchen": 1,
        "parking": 1,
    }

    gen = BaselineLayoutGenerator()
    rooms = gen.generate(reqs)

    print(f"Baseline generated {len(rooms)} rooms:\n")
    print(f"  {'ID':<4} {'Type':<22} {'Floor':<6} {'X':>6} {'Y':>6} {'W':>6} {'H':>6} {'Area':>8}")
    print(f"  {'-'*72}")
    for r in rooms:
        print(f"  {r['id']:<4} {r['type']:<22} {r['floor']:<6} "
              f"{r['x']:>6.1f} {r['y']:>6.1f} {r['width']:>6.1f} {r['height']:>6.1f} "
              f"{r['area_sqft']:>8.1f}")
