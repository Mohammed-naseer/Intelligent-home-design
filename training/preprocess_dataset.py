"""
preprocess_dataset.py — Architectural Dataset Preprocessing Pipeline
=====================================================================
Reads raw architectural data (from datasets/raw/ or synthetic fallback),
validates each record, normalizes coordinates and dimensions, encodes
room types, builds adjacency matrices, and writes processed samples to
datasets/processed/canonical_dataset.json.

Usage
-----
  python training/preprocess_dataset.py
  python training/preprocess_dataset.py --input datasets/raw/my_dataset.json
  python training/preprocess_dataset.py --samples 1000 --force-synthetic

Pipeline Steps
--------------
  1. Discover raw data sources (raw/ directory or synthetic fallback)
  2. Load all raw samples
  3. Validate each record (geometry + schema)
  4. Canonicalize to standard internal format
  5. Remove corrupted / invalid samples
  6. Normalize coordinates and dimensions
  7. Encode room types (integer indices)
  8. Build room adjacency matrices
  9. Generate training tensors specification
 10. Save processed canonical dataset
 11. Save preprocessing metadata
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Path Setup ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from datasets.room_vocabulary import (
    ROOM_VOCABULARY,
    NUM_ROOM_TYPES,
    normalize_room_type,
)
from datasets.data_format import (
    canonicalize_sample,
    CANONICAL_VERSION,
    MAX_ROOMS_PER_SAMPLE,
)
from training.validate_dataset import validate_sample, validate_dataset_records

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("preprocess_dataset")


# ── Constants ─────────────────────────────────────────────────────────────────
RAW_DIR       = BASE_DIR / "datasets" / "raw"
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"
METADATA_DIR  = BASE_DIR / "datasets" / "metadata"

OUTPUT_FILENAME  = "canonical_dataset.json"
METADATA_FILENAME = "preprocessing_metadata.json"


# ── Data Discovery ────────────────────────────────────────────────────────────

def discover_raw_sources(raw_dir: Path) -> List[Path]:
    """
    Scans the raw/ directory for supported data files.

    Returns a list of JSON file paths found. Returns an empty list if
    the directory is empty or does not exist.
    """
    if not raw_dir.exists():
        logger.info("Raw data directory not found: %s", raw_dir)
        return []

    sources: List[Path] = []
    for pattern in ("*.json", "**/*.json"):
        found = list(raw_dir.glob(pattern))
        sources.extend(f for f in found if f.name != "README.md")

    sources = sorted(set(sources))
    if sources:
        logger.info("Found %d raw data file(s) in %s", len(sources), raw_dir)
    else:
        logger.info("No JSON data files found in %s", raw_dir)
    return sources


def load_raw_json(file_path: Path) -> List[Dict[str, Any]]:
    """Loads raw samples from a JSON file (list or single dict)."""
    logger.info("Loading: %s (%.1f KB)", file_path.name, file_path.stat().st_size / 1024)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Support both {"samples": [...]} and {"data": [...]} wrappers
        for key in ("samples", "data", "records", "floor_plans"):
            if key in data and isinstance(data[key], list):
                return data[key]
        # Treat the dict itself as a single sample
        return [data]
    else:
        logger.warning("Unsupported JSON structure in %s", file_path)
        return []


# ── Preprocessing Pipeline ────────────────────────────────────────────────────

def preprocess_samples(
    raw_samples: List[Dict[str, Any]],
    source_label: str = "unknown",
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Runs the full preprocessing pipeline on a list of raw samples.

    Returns:
        (canonical_samples, stats_dict)
    """
    stats = {
        "total_input": len(raw_samples),
        "passed_schema_validation": 0,
        "passed_geometry_validation": 0,
        "canonicalized": 0,
        "rejected_schema": 0,
        "rejected_geometry": 0,
        "rejected_canonicalize": 0,
    }

    canonical_samples: List[Dict[str, Any]] = []

    for idx, raw in enumerate(raw_samples):
        sample_label = raw.get("sample_id", f"{source_label}_{idx:04d}")

        # Step 1: Schema + geometry validation
        is_valid, issues = validate_sample(raw)
        if not is_valid:
            stats["rejected_schema"] += 1
            logger.debug("REJECTED (schema) %s: %s", sample_label, "; ".join(issues))
            continue
        stats["passed_schema_validation"] += 1

        # Step 2: Canonicalize (normalizes coords, encodes types, builds adjacency)
        canonical = canonicalize_sample(raw, sample_id=sample_label)
        if canonical is None:
            stats["rejected_canonicalize"] += 1
            logger.debug("REJECTED (canonicalize) %s", sample_label)
            continue
        stats["canonicalized"] += 1
        stats["passed_geometry_validation"] += 1
        canonical_samples.append(canonical)

    return canonical_samples, stats


def generate_synthetic_fallback(num_samples: int) -> List[Dict[str, Any]]:
    """Generates synthetic samples when no real data is available."""
    logger.info("Generating %d synthetic samples as fallback...", num_samples)
    from datasets.synthetic_generator import generate_synthetic_layout
    return [generate_synthetic_layout(i) for i in range(1, num_samples + 1)]


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def run_preprocessing(
    raw_input: Optional[str] = None,
    num_synthetic_samples: int = 500,
    force_synthetic: bool = False,
    output_dir: Optional[str] = None,
) -> str:
    """
    Executes the full preprocessing pipeline.

    Args:
        raw_input:              Path to a specific raw JSON file, or None to scan raw/.
        num_synthetic_samples:  Number of synthetic samples if no real data found.
        force_synthetic:        If True, always use synthetic data.
        output_dir:             Override for the processed output directory.

    Returns:
        Path to the saved canonical dataset file.
    """
    t_start = time.time()
    logger.info("=" * 60)
    logger.info("AI House Architect — Dataset Preprocessing Pipeline")
    logger.info("=" * 60)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    out_dir = Path(output_dir) if output_dir else PROCESSED_DIR

    # ── Step 1: Discover raw data ─────────────────────────────────────────────
    all_raw: List[Dict[str, Any]] = []
    aggregate_stats: Dict[str, Any] = {
        "sources": [],
        "total_input": 0,
        "total_canonical": 0,
    }

    if force_synthetic:
        logger.info("Force-synthetic mode: skipping raw/ directory")
    elif raw_input:
        source_path = Path(raw_input)
        if source_path.exists():
            raw = load_raw_json(source_path)
            all_raw.extend(raw)
            aggregate_stats["sources"].append(str(source_path))
    else:
        sources = discover_raw_sources(RAW_DIR)
        for src in sources:
            raw = load_raw_json(src)
            all_raw.extend(raw)
            aggregate_stats["sources"].append(str(src))

    # ── Step 2: Synthetic fallback ────────────────────────────────────────────
    if not all_raw:
        # Check if a previously generated synthetic dataset exists
        existing = PROCESSED_DIR / "floorplan_dataset.json"
        if existing.exists() and not force_synthetic:
            logger.info("Loading existing synthetic dataset: %s", existing)
            all_raw = load_raw_json(existing)
        else:
            all_raw = generate_synthetic_fallback(num_synthetic_samples)

    aggregate_stats["total_input"] = len(all_raw)
    logger.info("Total raw samples loaded: %d", len(all_raw))

    # ── Step 3–9: Preprocess all samples ─────────────────────────────────────
    canonical_samples, proc_stats = preprocess_samples(all_raw, source_label="sample")

    aggregate_stats["total_canonical"] = len(canonical_samples)
    aggregate_stats["preprocessing"] = proc_stats

    logger.info("-" * 40)
    logger.info("Preprocessing complete:")
    logger.info("  Input samples:      %d", proc_stats["total_input"])
    logger.info("  Schema-valid:       %d", proc_stats["passed_schema_validation"])
    logger.info("  Canonical:          %d", proc_stats["canonicalized"])
    logger.info("  Rejected (schema):  %d", proc_stats["rejected_schema"])
    logger.info("  Rejected (other):   %d", proc_stats["rejected_canonicalize"])

    if not canonical_samples:
        logger.error("No valid samples after preprocessing. Aborting.")
        raise RuntimeError("Preprocessing produced zero valid samples.")

    # ── Step 10: Save canonical dataset ──────────────────────────────────────
    output_path = out_dir / OUTPUT_FILENAME
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(canonical_samples, f, indent=2)

    size_kb = output_path.stat().st_size / 1024
    logger.info("Saved canonical dataset: %s (%.1f KB, %d samples)",
                output_path, size_kb, len(canonical_samples))

    # ── Step 11: Save preprocessing metadata ─────────────────────────────────
    elapsed = round(time.time() - t_start, 2)
    aggregate_stats["elapsed_seconds"] = elapsed
    aggregate_stats["output_path"] = str(output_path)
    aggregate_stats["format_version"] = CANONICAL_VERSION
    aggregate_stats["room_vocabulary"] = ROOM_VOCABULARY
    aggregate_stats["num_room_types"] = NUM_ROOM_TYPES
    aggregate_stats["max_rooms_per_sample"] = MAX_ROOMS_PER_SAMPLE

    # Room type distribution
    type_counts: Dict[str, int] = {rt: 0 for rt in ROOM_VOCABULARY}
    for s in canonical_samples:
        for room in s.get("rooms", []):
            rt = room.get("type", "living_room")
            type_counts[rt] = type_counts.get(rt, 0) + 1
    aggregate_stats["room_type_distribution"] = type_counts

    metadata_path = METADATA_DIR / METADATA_FILENAME
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(aggregate_stats, f, indent=2)

    logger.info("Saved preprocessing metadata: %s", metadata_path)
    logger.info("Total time: %.2f s", elapsed)
    logger.info("=" * 60)

    return str(output_path)


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="AI House Architect — Dataset Preprocessing")
    parser.add_argument("--input",           type=str,  default=None, help="Path to raw JSON file")
    parser.add_argument("--samples",         type=int,  default=500,  help="Synthetic samples if no real data")
    parser.add_argument("--force-synthetic", action="store_true",     help="Always use synthetic data")
    parser.add_argument("--output-dir",      type=str,  default=None, help="Override output directory")
    args = parser.parse_args()

    run_preprocessing(
        raw_input=args.input,
        num_synthetic_samples=args.samples,
        force_synthetic=args.force_synthetic,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
