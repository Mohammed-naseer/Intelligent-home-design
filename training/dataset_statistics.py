"""
dataset_statistics.py — Architectural Dataset Statistics Report
===============================================================
Reads the processed canonical dataset and computes detailed statistics
across all samples. Generates both a console report and a JSON file
at datasets/metadata/statistics_report.json.

Usage
-----
  python training/dataset_statistics.py
  python training/dataset_statistics.py --dataset datasets/processed/canonical_dataset.json

Report Includes
---------------
  - Total / train / validation / test counts
  - Room type distribution (counts + percentages)
  - Average rooms per house
  - Average room dimensions per type
  - Average number of floors
  - Average / min / max plot dimensions
  - Room adjacency edge frequencies
  - Space utilization statistics (if metrics present)
"""

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Path Setup ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from datasets.room_vocabulary import ROOM_VOCABULARY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("dataset_statistics")

PROCESSED_DIR = BASE_DIR / "datasets" / "processed"
METADATA_DIR  = BASE_DIR / "datasets" / "metadata"


# ── Loader ────────────────────────────────────────────────────────────────────

def _load(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _try_load_split(split_name: str) -> List[Dict[str, Any]]:
    """Attempts to load a named split JSON if it exists."""
    mapping = {
        "train":      BASE_DIR / "datasets" / "train"       / "train.json",
        "validation": BASE_DIR / "datasets" / "validation"  / "validation.json",
        "test":       BASE_DIR / "datasets" / "test"        / "test.json",
    }
    return _load(mapping.get(split_name, Path("_nonexistent_")))


# ── Statistics Computation ────────────────────────────────────────────────────

def _safe_mean(values: List[float]) -> Optional[float]:
    return round(sum(values) / len(values), 2) if values else None

def _safe_min(values: List[float]) -> Optional[float]:
    return round(min(values), 2) if values else None

def _safe_max(values: List[float]) -> Optional[float]:
    return round(max(values), 2) if values else None


def compute_statistics(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes aggregate statistics over a list of canonical samples.

    Returns a structured dictionary suitable for JSON serialization.
    """
    if not samples:
        return {"count": 0, "error": "No samples to analyze"}

    n = len(samples)

    # Per-sample room counts
    room_counts: List[int] = []
    floor_counts: List[int] = []
    plot_widths:  List[float] = []
    plot_lengths: List[float] = []
    plot_areas:   List[float] = []

    # Room type counters
    room_type_counts: Dict[str, int] = defaultdict(int)

    # Per-type dimension accumulators
    type_widths:  Dict[str, List[float]] = defaultdict(list)
    type_heights: Dict[str, List[float]] = defaultdict(list)
    type_areas:   Dict[str, List[float]] = defaultdict(list)

    # Adjacency frequency
    adjacency_freq: Dict[str, int] = defaultdict(int)

    # Quality metrics
    overall_scores: List[float] = []
    space_utils:    List[float] = []

    for s in samples:
        plot = s.get("plot", {})
        w = float(plot.get("width",  s.get("requirements", {}).get("plot_width", 0)))
        l_ = float(plot.get("length", s.get("requirements", {}).get("plot_length", 0)))
        fl = int(s.get("floors", s.get("requirements", {}).get("floors", 1)))
        rooms = s.get("rooms", [])

        room_counts.append(len(rooms))
        floor_counts.append(fl)
        if w > 0:
            plot_widths.append(w)
        if l_ > 0:
            plot_lengths.append(l_)
        if w > 0 and l_ > 0:
            plot_areas.append(w * l_)

        for room in rooms:
            rt = room.get("type", "living_room")
            rw = float(room.get("width", 0))
            rh = float(room.get("height", 0))
            room_type_counts[rt] += 1
            if rw > 0:
                type_widths[rt].append(rw)
            if rh > 0:
                type_heights[rt].append(rh)
            if rw > 0 and rh > 0:
                type_areas[rt].append(rw * rh)

        for conn in s.get("connections", []):
            edge = tuple(sorted([conn.get("from", ""), conn.get("to", "")]))
            adjacency_freq[f"{edge[0]}__{edge[1]}"] += 1

        metrics = s.get("metrics", {})
        if "overall_score" in metrics:
            overall_scores.append(float(metrics["overall_score"]))
        if "space_utilization" in metrics:
            space_utils.append(float(metrics["space_utilization"]))

    # Build room type breakdown
    total_rooms = sum(room_type_counts.values())
    room_type_stats: Dict[str, Any] = {}
    for rt in ROOM_VOCABULARY:
        cnt = room_type_counts.get(rt, 0)
        room_type_stats[rt] = {
            "count":       cnt,
            "pct":         round(cnt / max(1, total_rooms) * 100, 1),
            "avg_width":   _safe_mean(type_widths.get(rt, [])),
            "avg_height":  _safe_mean(type_heights.get(rt, [])),
            "avg_area":    _safe_mean(type_areas.get(rt, [])),
            "min_width":   _safe_min(type_widths.get(rt, [])),
            "max_width":   _safe_max(type_widths.get(rt, [])),
        }

    # Top adjacency pairs
    top_adjacencies = sorted(
        adjacency_freq.items(), key=lambda x: x[1], reverse=True
    )[:15]

    return {
        "count": n,
        "total_rooms": total_rooms,
        "rooms_per_house": {
            "mean": _safe_mean(room_counts),
            "min":  _safe_min(room_counts),
            "max":  _safe_max(room_counts),
        },
        "floors": {
            "mean": _safe_mean(floor_counts),
            "dist": dict(sorted({str(f): floor_counts.count(f)
                                 for f in set(floor_counts)}.items())),
        },
        "plot_dimensions": {
            "width_mean":   _safe_mean(plot_widths),
            "width_min":    _safe_min(plot_widths),
            "width_max":    _safe_max(plot_widths),
            "length_mean":  _safe_mean(plot_lengths),
            "length_min":   _safe_min(plot_lengths),
            "length_max":   _safe_max(plot_lengths),
            "area_mean":    _safe_mean(plot_areas),
        },
        "room_type_distribution": room_type_stats,
        "top_adjacency_pairs": [
            {"pair": k.replace("__", " -- "), "count": v}
            for k, v in top_adjacencies
        ],
        "quality_metrics": {
            "overall_score_mean": _safe_mean(overall_scores),
            "overall_score_min":  _safe_min(overall_scores),
            "overall_score_max":  _safe_max(overall_scores),
            "space_util_mean":    _safe_mean(space_utils),
        } if overall_scores else None,
    }


# ── Report Printer ────────────────────────────────────────────────────────────

def print_report(stats: Dict[str, Any], split_label: str = "All") -> None:
    """Prints a human-readable statistics report to stdout."""
    print(f"\n{'='*60}")
    print(f"  Dataset Statistics — {split_label}")
    print(f"{'='*60}")
    print(f"  Samples:                {stats['count']}")
    print(f"  Total rooms:            {stats['total_rooms']}")
    rooms_ph = stats['rooms_per_house']
    print(f"  Avg rooms / house:      {rooms_ph['mean']}  (min {rooms_ph['min']}, max {rooms_ph['max']})")
    fl = stats['floors']
    print(f"  Avg floors:             {fl['mean']}  distribution: {fl['dist']}")
    pd = stats['plot_dimensions']
    print(f"  Avg plot width:         {pd['width_mean']} ft  ({pd['width_min']}–{pd['width_max']})")
    print(f"  Avg plot length:        {pd['length_mean']} ft  ({pd['length_min']}–{pd['length_max']})")
    print(f"  Avg plot area:          {pd['area_mean']} sqft")

    print(f"\n  Room Type Distribution:")
    print(f"  {'Type':<22} {'Count':>6}  {'%':>6}  {'AvgW':>7}  {'AvgH':>7}  {'AvgArea':>9}")
    print(f"  {'-'*68}")
    dist = stats['room_type_distribution']
    for rt in ROOM_VOCABULARY:
        d = dist.get(rt, {})
        cnt = d.get('count', 0)
        if cnt == 0:
            continue
        print(f"  {rt:<22} {cnt:>6}  {d.get('pct', 0):>5.1f}%  "
              f"{str(d.get('avg_width','—')):>7}  {str(d.get('avg_height','—')):>7}  "
              f"{str(d.get('avg_area','—')):>9}")

    print(f"\n  Top Room Adjacency Pairs:")
    for entry in stats.get('top_adjacency_pairs', [])[:10]:
        print(f"    {entry['pair']:<40} {entry['count']}")

    if stats.get('quality_metrics'):
        qm = stats['quality_metrics']
        print(f"\n  Quality Metrics:")
        print(f"    Overall score: mean={qm['overall_score_mean']}  "
              f"min={qm['overall_score_min']}  max={qm['overall_score_max']}")
        if qm.get('space_util_mean'):
            print(f"    Space util:    mean={qm['space_util_mean']}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def run_statistics(dataset_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes statistics for the full dataset and any available splits.

    Returns a combined report dictionary.
    """
    logger.info("=" * 60)
    logger.info("AI House Architect — Dataset Statistics")
    logger.info("=" * 60)

    # Determine dataset path
    if dataset_path:
        source = Path(dataset_path)
    else:
        source = PROCESSED_DIR / "canonical_dataset.json"
        if not source.exists():
            source = PROCESSED_DIR / "floorplan_dataset.json"

    if not source.exists():
        logger.error("Dataset not found: %s. Run preprocess_dataset.py first.", source)
        sys.exit(1)

    logger.info("Loading dataset: %s", source)
    all_samples = _load(source)
    logger.info("Loaded %d samples", len(all_samples))

    # Overall statistics
    overall_stats = compute_statistics(all_samples)
    print_report(overall_stats, "Full Dataset")

    # Split statistics (if splits exist)
    split_stats: Dict[str, Any] = {}
    for split_name in ("train", "validation", "test"):
        split_samples = _try_load_split(split_name)
        if split_samples:
            ss = compute_statistics(split_samples)
            split_stats[split_name] = ss
            print_report(ss, f"{split_name.title()} Split")
        else:
            logger.info("No %s split found (run split_dataset.py)", split_name)

    # Save report
    report = {
        "overall":    overall_stats,
        "splits":     split_stats,
        "source":     str(source),
    }

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    report_path = METADATA_DIR / "statistics_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info("Statistics report saved: %s", report_path)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="AI House Architect — Dataset Statistics")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Path to canonical JSON dataset")
    args = parser.parse_args()
    run_statistics(args.dataset)


if __name__ == "__main__":
    main()
