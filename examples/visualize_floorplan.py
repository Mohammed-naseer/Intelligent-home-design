"""
visualize_floorplan.py — Matplotlib 2D Floor Plan Visualizer
=============================================================
Development visualization tool for validating AI-generated floor plans.

This is NOT the final production frontend.
It is used for debugging and verifying that the model generates sensible layouts.

Features
--------
  - Plot boundary drawn as a thick border
  - Each room rendered as a colored rectangle with label
  - Room type, dimensions, and floor number displayed
  - Multi-floor layouts shown as separate subplots
  - Overlapping rooms highlighted in red
  - Plot + room area statistics printed below the figure
  - Constraint violations annotated if provided
  - Saves to output/debug_floorplan.png

Usage
-----
  from examples.visualize_floorplan import visualize_floorplan, save_floorplan

  rooms = [...]    # list of room dicts
  reqs  = {...}    # requirements dict
  result = constraint_engine.validate(rooms, reqs)
  save_floorplan(rooms, reqs, result, "output/my_plan.png")
"""

import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

logger = logging.getLogger(__name__)

# ── Color Palette ─────────────────────────────────────────────────────────────

try:
    from datasets.room_vocabulary import get_room_color, normalize_room_type
    _vocab = True
except ImportError:
    _vocab = False
    def get_room_color(rt: str) -> str:
        return "#D0E8FF"
    def normalize_room_type(rt: str) -> str:
        return rt.strip().lower().replace(" ", "_")

VIOLATION_COLOR  = "#FF4444"
VIOLATION_BORDER = "#CC0000"
PLOT_BORDER_COLOR = "#1A1A2E"
GRID_COLOR        = "#E8E8E8"
TITLE_COLOR       = "#1A1A2E"
SUBTITLE_COLOR    = "#666666"


# ── Core Drawing Function ─────────────────────────────────────────────────────

def _detect_overlaps(rooms: List[Dict[str, Any]]) -> set:
    """
    Returns a set of room IDs that overlap with at least one other room
    on the same floor.
    """
    try:
        from shapely.geometry import box as shp_box
    except ImportError:
        return set()

    overlapping: set = set()
    floor_groups: Dict[int, List] = {}
    for r in rooms:
        fl = int(r.get("floor", 1))
        floor_groups.setdefault(fl, []).append(r)

    for fl, group in floor_groups.items():
        for i in range(len(group)):
            r1 = group[i]
            w1, h1 = float(r1.get("width", 0)), float(r1.get("height", 0))
            if w1 <= 0 or h1 <= 0:
                continue
            p1 = shp_box(r1["x"], r1["y"], r1["x"] + w1, r1["y"] + h1)
            for j in range(i + 1, len(group)):
                r2 = group[j]
                w2, h2 = float(r2.get("width", 0)), float(r2.get("height", 0))
                if w2 <= 0 or h2 <= 0:
                    continue
                p2 = shp_box(r2["x"], r2["y"], r2["x"] + w2, r2["y"] + h2)
                if p1.intersection(p2).area > 0.5:
                    rid1 = r1.get("id", id(r1))
                    rid2 = r2.get("id", id(r2))
                    overlapping.add(rid1)
                    overlapping.add(rid2)

    return overlapping


def visualize_floorplan(
    rooms: List[Dict[str, Any]],
    requirements: Dict[str, Any],
    constraint_result: Optional[Dict[str, Any]] = None,
    title: str = "AI-Generated Floor Plan",
    figsize_per_floor: Tuple[float, float] = (10.0, 8.0),
) -> Any:
    """
    Renders a 2D floor plan visualization using Matplotlib.

    Args:
        rooms:              List of room dicts from the generator.
        requirements:       User requirement dictionary.
        constraint_result:  Output from ConstraintEngine.validate() (optional).
        title:              Figure title.
        figsize_per_floor:  (width, height) per floor subplot in inches.

    Returns:
        matplotlib.figure.Figure object.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch
    except ImportError:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install it with: pip install matplotlib"
        )

    # ── Plot Dimensions ───────────────────────────────────────────────────────
    plot = requirements.get("plot", {})
    plot_w = float(requirements.get("plot_width",  plot.get("width",  50.0)))
    plot_l = float(requirements.get("plot_length", plot.get("length", 60.0)))
    floors = int(requirements.get("floors", 1))

    # Group rooms by floor
    floor_rooms: Dict[int, List] = {fl: [] for fl in range(1, floors + 1)}
    for r in rooms:
        fl = int(r.get("floor", 1))
        if 1 <= fl <= floors:
            floor_rooms[fl].append(r)
        else:
            floor_rooms.setdefault(fl, []).append(r)

    active_floors = sorted(floor_rooms.keys())
    n_floors = len(active_floors)

    # Detect overlaps for highlighting
    overlapping_ids = _detect_overlaps(rooms)

    # ── Figure Layout ─────────────────────────────────────────────────────────
    fig_w = figsize_per_floor[0] * n_floors
    fig_h = figsize_per_floor[1] + 2.0   # extra space for header / footer
    fig = plt.figure(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor("#F8F9FA")

    # Title + subtitle
    score_str = ""
    validity_str = ""
    if constraint_result:
        score = constraint_result.get("score", None)
        is_valid = constraint_result.get("valid", None)
        if score is not None:
            score_str = f"  |  Constraint Score: {score:.2f}"
        if is_valid is not None:
            validity_str = "  ✓ VALID" if is_valid else "  ✗ VIOLATIONS FOUND"

    fig.suptitle(
        f"{title}{validity_str}{score_str}",
        fontsize=14, fontweight="bold", color=TITLE_COLOR,
        y=0.97
    )

    reqs_text = (
        f"Plot: {plot_w:.0f}×{plot_l:.0f} ft  |  "
        f"Floors: {floors}  |  "
        f"Rooms: {len(rooms)}"
    )
    rooms_dict = requirements.get("rooms", {})
    if isinstance(rooms_dict, dict):
        beds  = rooms_dict.get("bedrooms",  requirements.get("bedrooms",  "—"))
        baths = rooms_dict.get("bathrooms", requirements.get("bathrooms", "—"))
    else:
        beds  = requirements.get("bedrooms",  "—")
        baths = requirements.get("bathrooms", "—")
    reqs_text += f"  |  {beds} BR / {baths} BA"
    fig.text(0.5, 0.93, reqs_text, ha="center", fontsize=10, color=SUBTITLE_COLOR)

    # ── Per-Floor Subplots ────────────────────────────────────────────────────
    for subplot_idx, fl in enumerate(active_floors):
        ax = fig.add_subplot(1, n_floors, subplot_idx + 1)
        ax.set_facecolor("#FAFAFA")

        # Plot boundary
        plot_rect = mpatches.Rectangle(
            (0, 0), plot_w, plot_l,
            linewidth=2.5, edgecolor=PLOT_BORDER_COLOR,
            facecolor="#F0F0F0", zorder=0
        )
        ax.add_patch(plot_rect)

        # Grid
        ax.set_xticks(range(0, int(plot_w) + 1, 10))
        ax.set_yticks(range(0, int(plot_l) + 1, 10))
        ax.grid(True, color=GRID_COLOR, linewidth=0.5, zorder=1)

        # Rooms
        total_room_area = 0.0
        for room in floor_rooms.get(fl, []):
            x   = float(room.get("x", 0))
            y   = float(room.get("y", 0))
            w   = float(room.get("width", 0))
            h   = float(room.get("height", 0))
            rt  = normalize_room_type(room.get("type", "living_room"))
            rid = room.get("id", id(room))

            if w <= 0 or h <= 0:
                continue
            total_room_area += w * h

            # Is this room overlapping?
            is_overlapping = rid in overlapping_ids

            face_color  = VIOLATION_COLOR if is_overlapping else get_room_color(rt)
            edge_color  = VIOLATION_BORDER if is_overlapping else "#333333"
            edge_width  = 2.0 if is_overlapping else 1.0
            alpha       = 0.85

            room_rect = mpatches.FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0.2",
                linewidth=edge_width, edgecolor=edge_color,
                facecolor=face_color, alpha=alpha, zorder=2
            )
            ax.add_patch(room_rect)

            # Room label
            label_lines = [
                rt.replace("_", "\n"),
                f"{w:.0f}×{h:.0f} ft",
            ]
            label_text = "\n".join(label_lines)

            font_size = 7 if w < 12 else 8
            ax.text(
                x + w / 2, y + h / 2,
                label_text,
                ha="center", va="center",
                fontsize=font_size,
                fontweight="semibold",
                color="#1A1A2E",
                wrap=True,
                zorder=3
            )

        # Subplot formatting
        util = total_room_area / max(1.0, plot_w * plot_l)
        ax.set_xlim(-2, plot_w + 2)
        ax.set_ylim(-2, plot_l + 2)
        ax.set_aspect("equal")
        ax.set_xlabel("Width (ft)", fontsize=9, color=SUBTITLE_COLOR)
        ax.set_ylabel("Length (ft)", fontsize=9, color=SUBTITLE_COLOR)
        ax.set_title(
            f"Floor {fl}  —  {len(floor_rooms.get(fl, []))} rooms  "
            f"(util: {util*100:.0f}%)",
            fontsize=11, fontweight="bold", color=TITLE_COLOR, pad=10
        )
        ax.tick_params(labelsize=8)
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            spine.set_edgecolor("#AAAAAA")

    # ── Violations Footer ─────────────────────────────────────────────────────
    if constraint_result and constraint_result.get("violations"):
        viols = constraint_result["violations"]
        viol_text = "⚠ Violations:\n" + "\n".join(f"  • {v}" for v in viols[:6])
        if len(viols) > 6:
            viol_text += f"\n  ... and {len(viols) - 6} more"
        fig.text(
            0.02, 0.02, viol_text,
            fontsize=8, color=VIOLATION_BORDER,
            va="bottom", ha="left",
            fontfamily="monospace"
        )

    plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    return fig


def save_floorplan(
    rooms: List[Dict[str, Any]],
    requirements: Dict[str, Any],
    constraint_result: Optional[Dict[str, Any]] = None,
    output_path: str = "output/debug_floorplan.png",
    title: str = "AI-Generated Floor Plan",
    dpi: int = 150,
) -> str:
    """
    Generates and saves a 2D floor plan visualization.

    Args:
        rooms:             List of room dicts.
        requirements:      User requirement dictionary.
        constraint_result: Output from ConstraintEngine.validate() (optional).
        output_path:       File path for the output PNG.
        title:             Figure title.
        dpi:               Image resolution.

    Returns:
        Absolute path to the saved PNG file.
    """
    import matplotlib
    matplotlib.use("Agg")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig = visualize_floorplan(rooms, requirements, constraint_result, title)
    fig.savefig(str(output_path), dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    fig.clf()

    import matplotlib.pyplot as plt
    plt.close("all")

    logger.info("Floor plan saved: %s", output_path)
    return str(output_path.resolve())


if __name__ == "__main__":
    # Quick smoke test
    sys.path.insert(0, str(BASE_DIR))
    from training.baseline_generator import BaselineLayoutGenerator
    from geometry.constraint_engine import ConstraintEngine

    reqs = {
        "plot_width": 50, "plot_length": 60,
        "floors": 2, "bedrooms": 3, "bathrooms": 2,
        "kitchen": 1, "parking": 1,
    }

    gen = BaselineLayoutGenerator()
    rooms = gen.generate(reqs)

    engine = ConstraintEngine()
    result = engine.validate(rooms, reqs)

    output = save_floorplan(rooms, reqs, result,
                            "output/debug_floorplan_baseline.png",
                            title="Baseline Floor Plan")
    print(f"Saved: {output}")
    print(f"Valid: {result['valid']}  Score: {result['score']}")
