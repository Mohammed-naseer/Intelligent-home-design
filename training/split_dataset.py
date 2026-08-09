"""
split_dataset.py — Train / Validation / Test Dataset Splitter
==============================================================
Reads the canonical processed dataset and produces reproducible,
stratified train / validation / test splits (70 / 15 / 15).

Stratification is performed on the number of floors and number of bedrooms
so each split has a balanced representation of house configurations.

Usage
-----
  python training/split_dataset.py
  python training/split_dataset.py --ratio 0.70 0.15 0.15 --seed 42

Outputs
-------
  datasets/train/train.json
  datasets/validation/validation.json
  datasets/test/test.json
  datasets/metadata/split_manifest.json
"""

import argparse
import json
import logging
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ── Path Setup ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("split_dataset")

# ── Constants ─────────────────────────────────────────────────────────────────
PROCESSED_DIR  = BASE_DIR / "datasets" / "processed"
TRAIN_DIR      = BASE_DIR / "datasets" / "train"
VAL_DIR        = BASE_DIR / "datasets" / "validation"
TEST_DIR       = BASE_DIR / "datasets" / "test"
METADATA_DIR   = BASE_DIR / "datasets" / "metadata"

CANONICAL_FILE = "canonical_dataset.json"
FALLBACK_FILE  = "floorplan_dataset.json"

DEFAULT_SEED       = 42
DEFAULT_TRAIN_RATIO = 0.70
DEFAULT_VAL_RATIO   = 0.15
DEFAULT_TEST_RATIO  = 0.15


# ── Stratification ────────────────────────────────────────────────────────────

def _stratification_key(sample: Dict[str, Any]) -> str:
    """
    Generates a stratification key from sample properties.
    Groups samples by (floors, bedroom_count) to ensure balanced splits.
    """
    floors = int(sample.get("floors", sample.get("requirements", {}).get("floors", 1)))
    reqs = sample.get("requirements", {})
    beds = int(reqs.get("bedrooms", 3))
    # Bucket bedrooms into 3 groups: 1-2, 3-4, 5+
    bed_group = "low" if beds <= 2 else ("mid" if beds <= 4 else "high")
    return f"f{floors}_{bed_group}"


def stratified_split(
    samples: List[Dict[str, Any]],
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
    seed: int,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Produces stratified train/val/test splits.

    Within each stratum, samples are shuffled with the given seed before
    being proportionally assigned to each split. This ensures both:
      - Reproducibility: same seed → same split
      - Balance: each stratum is represented in proportion across splits
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Split ratios must sum to 1.0"

    # Group samples by strata
    strata: Dict[str, List[Dict]] = defaultdict(list)
    for s in samples:
        strata[_stratification_key(s)].append(s)

    train_set: List[Dict] = []
    val_set:   List[Dict] = []
    test_set:  List[Dict] = []

    for key, group in strata.items():
        rng = random.Random(seed)
        rng.shuffle(group)
        n = len(group)
        n_train = max(1, round(n * train_ratio))
        n_val   = max(1, round(n * val_ratio))
        # Ensure we don't exceed group size
        n_train = min(n_train, n)
        n_val   = min(n_val, n - n_train)
        n_test  = n - n_train - n_val

        train_set.extend(group[:n_train])
        val_set.extend(group[n_train:n_train + n_val])
        test_set.extend(group[n_train + n_val:])

        logger.debug("Stratum '%s': total=%d  train=%d  val=%d  test=%d",
                     key, n, n_train, n_val, n_test)

    # Final shuffle within each split for good measure
    for split in (train_set, val_set, test_set):
        rng = random.Random(seed + 1)
        rng.shuffle(split)

    return train_set, val_set, test_set


# ── IO Helpers ────────────────────────────────────────────────────────────────

def _load_canonical(processed_dir: Path) -> List[Dict[str, Any]]:
    """Loads the canonical dataset, falling back to the legacy filename."""
    canonical_path = processed_dir / CANONICAL_FILE
    fallback_path  = processed_dir / FALLBACK_FILE

    if canonical_path.exists():
        logger.info("Loading canonical dataset: %s", canonical_path)
        with open(canonical_path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif fallback_path.exists():
        logger.info("Canonical dataset not found; loading fallback: %s", fallback_path)
        logger.warning("Consider running preprocess_dataset.py first.")
        with open(fallback_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(
            f"No dataset found in {processed_dir}. "
            "Run training/preprocess_dataset.py first."
        )


def _save_split(samples: List[Dict], path: Path, name: str) -> None:
    """Saves a split to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2)
    logger.info("Saved %s split: %d samples → %s (%.1f KB)",
                name, len(samples), path, path.stat().st_size / 1024)


def _split_stats(samples: List[Dict]) -> Dict[str, Any]:
    """Computes per-split statistics for the manifest."""
    if not samples:
        return {"count": 0}
    floors_dist: Dict[int, int] = defaultdict(int)
    beds_dist:   Dict[int, int] = defaultdict(int)
    for s in samples:
        fl = int(s.get("floors", s.get("requirements", {}).get("floors", 1)))
        floors_dist[fl] += 1
        beds = int(s.get("requirements", {}).get("bedrooms", 0))
        beds_dist[beds] += 1
    return {
        "count": len(samples),
        "floors_distribution": dict(sorted(floors_dist.items())),
        "bedrooms_distribution": dict(sorted(beds_dist.items())),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def run_split(
    train_ratio: float = DEFAULT_TRAIN_RATIO,
    val_ratio:   float = DEFAULT_VAL_RATIO,
    test_ratio:  float = DEFAULT_TEST_RATIO,
    seed:        int   = DEFAULT_SEED,
    processed_dir: Path = PROCESSED_DIR,
) -> Dict[str, Any]:
    """
    Runs the full split pipeline.

    Returns:
        Dictionary with paths and statistics for the three splits.
    """
    t_start = time.time()
    logger.info("=" * 60)
    logger.info("AI House Architect — Dataset Split")
    logger.info("  Ratios: train=%.0f%%  val=%.0f%%  test=%.0f%%  seed=%d",
                train_ratio * 100, val_ratio * 100, test_ratio * 100, seed)
    logger.info("=" * 60)

    # Load
    samples = _load_canonical(processed_dir)
    logger.info("Loaded %d samples for splitting", len(samples))

    # Split
    train_set, val_set, test_set = stratified_split(
        samples, train_ratio, val_ratio, test_ratio, seed
    )

    logger.info("-" * 40)
    logger.info("Split results:")
    logger.info("  Train:      %d samples", len(train_set))
    logger.info("  Validation: %d samples", len(val_set))
    logger.info("  Test:       %d samples", len(test_set))

    # Save
    train_path = TRAIN_DIR / "train.json"
    val_path   = VAL_DIR   / "validation.json"
    test_path  = TEST_DIR  / "test.json"

    _save_split(train_set, train_path, "train")
    _save_split(val_set,   val_path,   "validation")
    _save_split(test_set,  test_path,  "test")

    # Save manifest
    elapsed = round(time.time() - t_start, 2)
    manifest = {
        "seed":        seed,
        "ratios":      {"train": train_ratio, "validation": val_ratio, "test": test_ratio},
        "total":       len(samples),
        "train":       _split_stats(train_set),
        "validation":  _split_stats(val_set),
        "test":        _split_stats(test_set),
        "paths": {
            "train":      str(train_path),
            "validation": str(val_path),
            "test":       str(test_path),
        },
        "elapsed_seconds": elapsed,
    }

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = METADATA_DIR / "split_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Saved split manifest: %s", manifest_path)
    logger.info("Total time: %.2f s", elapsed)

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="AI House Architect — Dataset Split")
    parser.add_argument("--ratio",  type=float, nargs=3,
                        default=[DEFAULT_TRAIN_RATIO, DEFAULT_VAL_RATIO, DEFAULT_TEST_RATIO],
                        metavar=("TRAIN", "VAL", "TEST"),
                        help="Split ratios (must sum to 1.0)")
    parser.add_argument("--seed",   type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    train_r, val_r, test_r = args.ratio
    total = train_r + val_r + test_r
    if abs(total - 1.0) > 1e-4:
        parser.error(f"Ratios must sum to 1.0 (got {total:.4f})")

    run_split(train_r, val_r, test_r, args.seed)


if __name__ == "__main__":
    main()
