"""
test_house_generation.py — End-to-End Pipeline Test
====================================================
Demonstrates the complete AI House Architect pipeline:

  Requirements
      ↓
  Baseline Generator (rule-based)
      ↓
  ML Model (trained PyTorch)
      ↓
  Constraint Validation
      ↓
  2D Floor Plan Visualization

This script is the final deliverable test for the dataset &
training foundation phase.

Usage
-----
  python examples/test_house_generation.py
  python examples/test_house_generation.py --plot-width 60 --floors 2 --bedrooms 3
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("test_house_generation")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_section(title: str) -> None:
    print(f"\n{'-'*60}")
    print(f"  {title}")
    print(f"{'-'*60}")


def _print_rooms(rooms, label: str) -> None:
    print(f"\n  {label}  ({len(rooms)} rooms generated)")
    print(f"  {'#':<4} {'Type':<22} {'Fl':<4} {'X':>6} {'Y':>6} {'W':>6} {'H':>6} {'Area':>8}")
    print(f"  {'-'*68}")
    for r in rooms:
        print(
            f"  {str(r.get('id','')):<4} {str(r.get('type','')):<22} "
            f"{r.get('floor',1):<4} {float(r.get('x',0)):>6.1f} {float(r.get('y',0)):>6.1f} "
            f"{float(r.get('width',0)):>6.1f} {float(r.get('height',0)):>6.1f} "
            f"{float(r.get('width',0))*float(r.get('height',0)):>8.1f}"
        )


def _print_constraint_result(result: dict, label: str) -> None:
    valid_sym = "VALID" if result["valid"] else "INVALID"
    print(f"\n  {label} -- {valid_sym}  |  Score: {result['score']:.3f}")
    if result["violations"]:
        print(f"  Violations ({len(result['violations'])}):")
        for v in result["violations"][:8]:
            print(f"    * {v}")
        if len(result["violations"]) > 8:
            print(f"    ... and {len(result['violations'])-8} more")
    else:
        print("  No violations -- layout is geometrically clean.")


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def run_test(
    plot_width: float  = 50.0,
    plot_length: float = 60.0,
    floors: int        = 2,
    bedrooms: int      = 3,
    bathrooms: int     = 2,
    kitchen: int       = 1,
    parking: int       = 1,
    style: str         = "modern",
    save_visuals: bool = True,
) -> None:
    """
    Runs the full end-to-end pipeline and prints a structured report.
    """
    requirements = {
        "plot_width":  plot_width,
        "plot_length": plot_length,
        "floors":      floors,
        "bedrooms":    bedrooms,
        "bathrooms":   bathrooms,
        "kitchen":     kitchen,
        "parking":     parking,
        "style":       style,
    }

    print("\n" + "=" * 60)
    print("  AI House Architect — End-to-End Pipeline Test")
    print("=" * 60)
    print(f"\n  Input Requirements:")
    print(f"    Plot:      {plot_width:.0f} × {plot_length:.0f} ft")
    print(f"    Floors:    {floors}")
    print(f"    Bedrooms:  {bedrooms}")
    print(f"    Bathrooms: {bathrooms}")
    print(f"    Kitchen:   {kitchen}")
    print(f"    Parking:   {parking}")
    print(f"    Style:     {style}")

    # ── Import Modules ────────────────────────────────────────────────────────
    from geometry.constraint_engine import ConstraintEngine
    engine = ConstraintEngine()

    # ── Step 1: Baseline Generator ────────────────────────────────────────────
    _print_section("STEP 1 — Baseline (Rule-Based) Generator")
    t0 = time.perf_counter()
    try:
        from training.baseline_generator import BaselineLayoutGenerator
        baseline_gen = BaselineLayoutGenerator()
        baseline_rooms = baseline_gen.generate(requirements)
        t_baseline = round((time.perf_counter() - t0) * 1000, 1)
        _print_rooms(baseline_rooms, "Baseline Layout")
        logger.info("Baseline generated %d rooms in %.1f ms", len(baseline_rooms), t_baseline)
    except Exception as e:
        logger.error("Baseline generator failed: %s", e)
        baseline_rooms = []
        t_baseline = 0.0

    # ── Step 2: Constraint Validation (Baseline) ──────────────────────────────
    _print_section("STEP 2 — Constraint Validation (Baseline)")
    if baseline_rooms:
        baseline_result = engine.validate(baseline_rooms, requirements)
        _print_constraint_result(baseline_result, "Baseline")
    else:
        baseline_result = {"valid": False, "violations": ["No rooms generated"], "score": 0.0}
        print("  ✗ No rooms to validate")

    # ── Step 3: ML Model Inference ────────────────────────────────────────────
    _print_section("STEP 3 — ML Model (Trained PyTorch) Inference")
    t0 = time.perf_counter()
    try:
        from inference.layout_generator import LayoutGenerator
        ml_gen = LayoutGenerator()
        ml_rooms = ml_gen.generate(requirements, candidate_seed=42)
        t_ml = round((time.perf_counter() - t0) * 1000, 1)
        ml_source = "pytorch" if ml_gen.model is not None else "procedural_fallback"
        print(f"\n  Source: {ml_source}")
        _print_rooms(ml_rooms, "ML Layout")
        logger.info("ML generated %d rooms in %.1f ms (source: %s)",
                    len(ml_rooms), t_ml, ml_source)
    except Exception as e:
        logger.error("ML model inference failed: %s", e)
        ml_rooms = []
        ml_source = "error"
        t_ml = 0.0

    # ── Step 4: Constraint Validation (ML) ───────────────────────────────────
    _print_section("STEP 4 — Constraint Validation (ML Model)")
    if ml_rooms:
        ml_result = engine.validate(ml_rooms, requirements)
        _print_constraint_result(ml_result, "ML Model")
    else:
        ml_result = {"valid": False, "violations": ["No rooms generated"], "score": 0.0}
        print("  ✗ No rooms to validate")

    # ── Step 5: Visualization ─────────────────────────────────────────────────
    _print_section("STEP 5 — 2D Floor Plan Visualization")
    if save_visuals:
        try:
            from examples.visualize_floorplan import save_floorplan

            output_dir = BASE_DIR / "output"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save baseline visualization
            if baseline_rooms:
                baseline_out = save_floorplan(
                    baseline_rooms, requirements, baseline_result,
                    output_path=str(output_dir / "debug_floorplan_baseline.png"),
                    title="Baseline Floor Plan (Rule-Based Generator)",
                )
                print(f"  Baseline:  {baseline_out}")

            # Save ML model visualization
            if ml_rooms:
                ml_out = save_floorplan(
                    ml_rooms, requirements, ml_result,
                    output_path=str(output_dir / "debug_floorplan_ml.png"),
                    title=f"ML Model Floor Plan ({ml_source})",
                )
                print(f"  ML Model:  {ml_out}")

        except ImportError as e:
            print(f"  Visualization skipped (matplotlib not installed): {e}")
        except Exception as e:
            logger.error("Visualization error: %s", e)
    else:
        print("  Visualization skipped (--no-visuals flag set)")

    # ── Summary ───────────────────────────────────────────────────────────────
    _print_section("SUMMARY")
    print(f"\n  {'Generator':<28} {'Rooms':>6}  {'Valid':>8}  {'Score':>7}  {'Time':>8}")
    print(f"  {'-'*62}")
    print(
        f"  {'Baseline (Rule-Based)':<28} {len(baseline_rooms):>6}  "
        f"{'Yes' if baseline_result['valid'] else 'No':>8}  "
        f"{baseline_result['score']:>7.3f}  {t_baseline:>6.1f} ms"
    )
    print(
        f"  {'ML Model (PyTorch)':<28} {len(ml_rooms):>6}  "
        f"{'Yes' if ml_result['valid'] else 'No':>8}  "
        f"{ml_result['score']:>7.3f}  {t_ml:>6.1f} ms"
    )

    print("\n" + "=" * 60)
    print("  Pipeline test complete.")
    if save_visuals:
        print(f"  Floor plans saved to: output/")
    print("=" * 60 + "\n")


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI House Architect — End-to-End Pipeline Test"
    )
    parser.add_argument("--plot-width",  type=float, default=50.0)
    parser.add_argument("--plot-length", type=float, default=60.0)
    parser.add_argument("--floors",      type=int,   default=2)
    parser.add_argument("--bedrooms",    type=int,   default=3)
    parser.add_argument("--bathrooms",   type=int,   default=2)
    parser.add_argument("--kitchen",     type=int,   default=1)
    parser.add_argument("--parking",     type=int,   default=1)
    parser.add_argument("--style",       type=str,   default="modern")
    parser.add_argument("--no-visuals",  action="store_true",
                        help="Skip matplotlib visualization")
    args = parser.parse_args()

    run_test(
        plot_width=args.plot_width,
        plot_length=args.plot_length,
        floors=args.floors,
        bedrooms=args.bedrooms,
        bathrooms=args.bathrooms,
        kitchen=args.kitchen,
        parking=args.parking,
        style=args.style,
        save_visuals=not args.no_visuals,
    )


if __name__ == "__main__":
    main()
