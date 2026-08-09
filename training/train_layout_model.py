"""
train_layout_model.py — PyTorch Layout Model Training Script
=============================================================
Trains the FloorPlanGeneratorNet using canonical architectural dataset.
Implements a production-quality training loop with:

  - Train / validation split evaluation
  - Early stopping with configurable patience
  - ReduceLROnPlateau learning-rate scheduler
  - Reproducible random seeds
  - Structured Python logging (not just print)
  - Best-model checkpoint saving (lowest val loss)
  - Latest-model checkpoint saving (every epoch)
  - Training metadata JSON (config, final metrics, timestamp)
  - Room-type classification loss alongside spatial MSE loss

Checkpoints saved under:
  models/layout_model/best_model.pt
  models/layout_model/latest_model.pt
  models/layout_model/metadata.json

Usage
-----
  python training/train_layout_model.py
  python training/train_layout_model.py --epochs 50 --batch-size 32
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau

# ── Path Setup ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from datasets.room_vocabulary import NUM_ROOM_TYPES
from models.layout_model import (
    FloorPlanGeneratorNet,
    encode_requirements,
    MAX_ROOMS,
    SPATIAL_FEATURES,
    ROOM_FEATURES,
    NUM_ROOM_TYPES as MODEL_NUM_ROOM_TYPES,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("train_layout_model")

# ── Paths ─────────────────────────────────────────────────────────────────────
PROCESSED_DIR   = BASE_DIR / "datasets" / "processed"
TRAIN_DIR       = BASE_DIR / "datasets" / "train"
VAL_DIR         = BASE_DIR / "datasets" / "validation"
MODEL_SAVE_DIR  = BASE_DIR / "models" / "layout_model"

BEST_MODEL_FILE   = "best_model.pt"
LATEST_MODEL_FILE = "latest_model.pt"
LEGACY_MODEL_FILE = "pytorch_layout_model.pt"   # Keep for backward compat
METADATA_FILE     = "metadata.json"


# ── Reproducibility ───────────────────────────────────────────────────────────

def set_seed(seed: int) -> None:
    """Sets all random seeds for reproducibility."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ── Dataset Loading ───────────────────────────────────────────────────────────

def _load_json(path: Path) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _find_dataset() -> Tuple[List[Dict], List[Dict]]:
    """
    Locates training and validation data.

    Priority:
      1. Canonical split files (train.json / validation.json)
      2. Full canonical dataset split 80/20 in memory
      3. Legacy synthetic dataset split 80/20 in memory
      4. Generate synthetic data on-the-fly
    """
    # Check for pre-split files
    train_path = TRAIN_DIR / "train.json"
    val_path   = VAL_DIR   / "validation.json"

    if train_path.exists() and val_path.exists():
        logger.info("Loading pre-split train / validation datasets")
        return _load_json(train_path), _load_json(val_path)

    # Fall back to canonical full dataset
    canonical_path = PROCESSED_DIR / "canonical_dataset.json"
    legacy_path    = PROCESSED_DIR / "floorplan_dataset.json"

    if canonical_path.exists():
        logger.info("No split files found. Splitting canonical_dataset.json 80/20 in memory.")
        data = _load_json(canonical_path)
    elif legacy_path.exists():
        logger.info("No split files found. Splitting floorplan_dataset.json 80/20 in memory.")
        data = _load_json(legacy_path)
    else:
        logger.info("No dataset found. Generating 500 synthetic samples.")
        from datasets.synthetic_generator import generate_synthetic_layout
        data = [generate_synthetic_layout(i) for i in range(1, 501)]

    # In-memory 80/20 split
    rng = np.random.RandomState(42)
    indices = rng.permutation(len(data))
    n_train = int(len(data) * 0.80)
    train_data = [data[i] for i in indices[:n_train]]
    val_data   = [data[i] for i in indices[n_train:]]
    return train_data, val_data


def prepare_tensors(
    data: List[Dict],
    in_features: int = 9,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Converts raw/canonical dataset records to training tensors.

    Returns:
        X:       (N, in_features)  — requirement input vectors
        Y_spatial: (N, MAX_ROOMS, SPATIAL_FEATURES)  — spatial targets
        Y_types:   (N, MAX_ROOMS)  — room type index targets (long)
    """
    X_list:        List[torch.Tensor] = []
    Y_spatial_list: List[torch.Tensor] = []
    Y_types_list:   List[torch.Tensor] = []

    for item in data:
        # Support both canonical and legacy formats
        req = item.get("requirements", item)
        rooms = item.get("rooms", [])
        if not rooms:
            continue

        # Extract plot dimensions for normalization
        plot = item.get("plot", {})
        plot_w = float(
            plot.get("width", req.get("plot_width", req.get("plot", {}).get("width", 50.0)))
        )
        plot_l = float(
            plot.get("length", req.get("plot_length", req.get("plot", {}).get("length", 50.0)))
        )
        floors = int(req.get("floors", item.get("floors", 1)))

        # Encode requirements
        x_vec = encode_requirements(req).squeeze(0)  # (in_features,)

        # Build spatial target (MAX_ROOMS × SPATIAL_FEATURES)
        y_spatial = torch.zeros((MAX_ROOMS, SPATIAL_FEATURES), dtype=torch.float32)
        # Build room type target (MAX_ROOMS,) with long indices
        y_types = torch.zeros((MAX_ROOMS,), dtype=torch.long)

        for slot_idx, room in enumerate(rooms[:MAX_ROOMS]):
            # Normalize spatial features
            # Support both canonical (norm_*) and raw (absolute) values
            if "norm_x" in room:
                nx = float(room["norm_x"])
                ny = float(room["norm_y"])
                nw = float(room["norm_width"])
                nh = float(room["norm_height"])
                nf = float(room.get("norm_floor", room.get("floor", 1) / max(1, floors)))
            else:
                x = float(room.get("x", 0.0))
                y = float(room.get("y", 0.0))
                w = float(room.get("width", room.get("w", 0.0)))
                h = float(room.get("height", room.get("h", 0.0)))
                fl = int(room.get("floor", 1))
                nx = min(1.0, max(0.0, x / max(1.0, plot_w)))
                ny = min(1.0, max(0.0, y / max(1.0, plot_l)))
                nw = min(1.0, max(0.0, w / max(1.0, plot_w)))
                nh = min(1.0, max(0.0, h / max(1.0, plot_l)))
                nf = min(1.0, max(0.0, fl / max(1, floors)))

            y_spatial[slot_idx] = torch.tensor(
                [nx, ny, nw, nh, nf, 1.0],  # exists = 1.0
                dtype=torch.float32
            )

            # Room type index
            type_idx = int(room.get("type_idx", 0))
            if type_idx < 0 or type_idx >= NUM_ROOM_TYPES:
                # Try to resolve from type string
                rt = room.get("type", "living_room")
                try:
                    from datasets.room_vocabulary import encode_room_type
                    type_idx = encode_room_type(rt)
                except Exception:
                    type_idx = 0
            y_types[slot_idx] = type_idx

        X_list.append(x_vec)
        Y_spatial_list.append(y_spatial)
        Y_types_list.append(y_types)

    if not X_list:
        raise RuntimeError("No valid samples found in dataset — cannot build tensors.")

    X         = torch.stack(X_list)
    Y_spatial = torch.stack(Y_spatial_list)
    Y_types   = torch.stack(Y_types_list)

    logger.info("Tensors: X=%s  Y_spatial=%s  Y_types=%s",
                tuple(X.shape), tuple(Y_spatial.shape), tuple(Y_types.shape))
    return X, Y_spatial, Y_types


# ── Loss Function ─────────────────────────────────────────────────────────────

def compute_loss(
    pred_spatial: torch.Tensor,
    pred_types:   torch.Tensor,
    tgt_spatial:  torch.Tensor,
    tgt_types:    torch.Tensor,
    spatial_weight: float = 1.0,
    type_weight:    float = 0.3,
) -> Tuple[torch.Tensor, float, float]:
    """
    Combined spatial MSE loss + room type cross-entropy loss.

    Spatial loss only penalizes active room slots (exists == 1).
    Type loss is masked to active slots.

    Returns:
        (combined_loss, spatial_loss_val, type_loss_val)
    """
    # Existence mask: which room slots are active in the target
    active_mask = tgt_spatial[:, :, 5] > 0.5  # (batch, MAX_ROOMS) bool

    # Spatial MSE — applied to all slots (model learns to predict 0 for inactive)
    spatial_loss = nn.functional.mse_loss(pred_spatial, tgt_spatial)

    # Cross-entropy for room types — only on active slots
    batch_size = pred_types.size(0)
    type_loss = torch.tensor(0.0)
    n_active = active_mask.sum().item()
    if n_active > 0:
        # Flatten to (N_active, num_types)
        pred_flat = pred_types[active_mask]           # (N_active, num_types)
        tgt_flat  = tgt_types[active_mask]            # (N_active,)
        type_loss = nn.functional.cross_entropy(pred_flat, tgt_flat)

    combined = spatial_weight * spatial_loss + type_weight * type_loss
    return combined, spatial_loss.item(), type_loss.item()


# ── Training Engine ───────────────────────────────────────────────────────────

class EarlyStopping:
    """Stops training when validation loss does not improve for `patience` epochs."""

    def __init__(self, patience: int = 10, min_delta: float = 1e-5) -> None:
        self.patience  = patience
        self.min_delta = min_delta
        self.counter   = 0
        self.best_loss: Optional[float] = None
        self.should_stop = False

    def step(self, val_loss: float) -> bool:
        """Returns True if training should stop."""
        if self.best_loss is None or val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop


def _run_epoch(
    model: nn.Module,
    X: torch.Tensor,
    Y_spatial: torch.Tensor,
    Y_types: torch.Tensor,
    batch_size: int,
    optimizer: Optional[optim.Optimizer] = None,
    device: torch.device = torch.device("cpu"),
) -> Tuple[float, float, float]:
    """
    Runs one training or evaluation epoch.

    If optimizer is provided → training mode (gradients enabled).
    If optimizer is None → evaluation mode (no gradients).

    Returns:
        (avg_combined_loss, avg_spatial_loss, avg_type_loss)
    """
    is_train = optimizer is not None
    model.train() if is_train else model.eval()

    n = X.size(0)
    perm = torch.randperm(n) if is_train else torch.arange(n)

    total_combined = 0.0
    total_spatial  = 0.0
    total_type     = 0.0

    ctx = torch.enable_grad() if is_train else torch.no_grad()
    with ctx:
        for start in range(0, n, batch_size):
            idx = perm[start: start + batch_size]
            bx = X[idx].to(device)
            by_s = Y_spatial[idx].to(device)
            by_t = Y_types[idx].to(device)

            pred_s, pred_t = model(bx)
            loss, sl, tl = compute_loss(pred_s, pred_t, by_s, by_t)

            if is_train:
                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()

            bs = bx.size(0)
            total_combined += loss.item() * bs
            total_spatial  += sl * bs
            total_type     += tl * bs

    return total_combined / n, total_spatial / n, total_type / n


# ── Main Training Function ────────────────────────────────────────────────────

def train_layout_model(
    epochs:     int   = 50,
    batch_size: int   = 32,
    lr:         float = 3e-3,
    seed:       int   = 42,
    patience:   int   = 12,
    device_str: str   = "cpu",
) -> str:
    """
    Executes the full training pipeline and saves checkpoints.

    Args:
        epochs:      Maximum training epochs.
        batch_size:  Mini-batch size.
        lr:          Initial learning rate.
        seed:        Random seed for reproducibility.
        patience:    Early stopping patience.
        device_str:  "cpu" or "cuda".

    Returns:
        Path to the best model checkpoint.
    """
    t_start = time.time()
    logger.info("=" * 60)
    logger.info("AI House Architect — Layout Model Training")
    logger.info("  Epochs: %d  Batch: %d  LR: %.4f  Seed: %d  Patience: %d",
                epochs, batch_size, lr, seed, patience)
    logger.info("=" * 60)

    # ── Setup ─────────────────────────────────────────────────────────────────
    set_seed(seed)
    device = torch.device(device_str if torch.cuda.is_available() else "cpu")
    logger.info("Device: %s", device)

    MODEL_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # ── Data ──────────────────────────────────────────────────────────────────
    train_data, val_data = _find_dataset()
    logger.info("Dataset: %d train, %d val", len(train_data), len(val_data))

    X_tr, Ys_tr, Yt_tr = prepare_tensors(train_data)
    X_vl, Ys_vl, Yt_vl = prepare_tensors(val_data)

    in_features = X_tr.size(1)

    # ── Model ─────────────────────────────────────────────────────────────────
    model = FloorPlanGeneratorNet(
        in_features=in_features,
        max_rooms=MAX_ROOMS,
        num_room_types=NUM_ROOM_TYPES,
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info("Model parameters: %s | in_features=%d | max_rooms=%d | room_types=%d",
                f"{total_params:,}", in_features, MAX_ROOMS, NUM_ROOM_TYPES)

    # ── Optimizer & Scheduler ─────────────────────────────────────────────────
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5, min_lr=1e-5
    )
    early_stop = EarlyStopping(patience=patience)

    # ── Training Loop ─────────────────────────────────────────────────────────
    best_val_loss = float("inf")
    best_epoch    = 0
    history: List[Dict[str, float]] = []

    for epoch in range(1, epochs + 1):
        t_ep = time.time()

        # Train
        tr_loss, tr_sl, tr_tl = _run_epoch(
            model, X_tr, Ys_tr, Yt_tr, batch_size, optimizer, device
        )

        # Validate
        vl_loss, vl_sl, vl_tl = _run_epoch(
            model, X_vl, Ys_vl, Yt_vl, batch_size, optimizer=None, device=device
        )

        current_lr = optimizer.param_groups[0]["lr"]
        scheduler.step(vl_loss)
        elapsed_ep = time.time() - t_ep

        # Log every epoch; verbose every 5
        log_fn = logger.info if epoch % 5 == 0 or epoch == 1 or epoch == epochs else logger.debug
        log_fn(
            "Epoch [%3d/%d] | train: %.5f (sp=%.5f ty=%.5f) | val: %.5f (sp=%.5f ty=%.5f) "
            "| lr=%.6f | %.1fs",
            epoch, epochs, tr_loss, tr_sl, tr_tl, vl_loss, vl_sl, vl_tl,
            current_lr, elapsed_ep
        )

        history.append({
            "epoch":    epoch,
            "train_loss": round(tr_loss, 6),
            "val_loss":   round(vl_loss, 6),
            "train_spatial_loss": round(tr_sl, 6),
            "val_spatial_loss":   round(vl_sl, 6),
            "train_type_loss":    round(tr_tl, 6),
            "val_type_loss":      round(vl_tl, 6),
            "lr":       round(current_lr, 8),
        })

        # Save latest
        latest_path = MODEL_SAVE_DIR / LATEST_MODEL_FILE
        torch.save(model.state_dict(), latest_path)

        # Save best
        if vl_loss < best_val_loss - 1e-6:
            best_val_loss = vl_loss
            best_epoch    = epoch
            best_path = MODEL_SAVE_DIR / BEST_MODEL_FILE
            torch.save(model.state_dict(), best_path)
            logger.info("  ↳ New best model saved (val_loss=%.6f)", best_val_loss)

        # Early stopping
        if early_stop.step(vl_loss):
            logger.info("Early stopping at epoch %d (patience=%d)", epoch, patience)
            break

    # ── Also save legacy filename for backward compat ─────────────────────────
    legacy_path = MODEL_SAVE_DIR / LEGACY_MODEL_FILE
    best_path   = MODEL_SAVE_DIR / BEST_MODEL_FILE
    if best_path.exists():
        import shutil
        shutil.copy2(best_path, legacy_path)
        logger.info("Copied best_model.pt → %s (backward compat)", LEGACY_MODEL_FILE)

    # ── Save Metadata ─────────────────────────────────────────────────────────
    elapsed_total = round(time.time() - t_start, 2)
    metadata = {
        "trained_at":       datetime.utcnow().isoformat() + "Z",
        "elapsed_seconds":  elapsed_total,
        "config": {
            "epochs_max":   epochs,
            "epochs_run":   len(history),
            "batch_size":   batch_size,
            "lr_initial":   lr,
            "seed":         seed,
            "patience":     patience,
            "device":       str(device),
        },
        "architecture": {
            "in_features":     in_features,
            "max_rooms":       MAX_ROOMS,
            "num_room_types":  NUM_ROOM_TYPES,
            "spatial_features": SPATIAL_FEATURES,
            "total_params":    total_params,
        },
        "dataset": {
            "train_samples": len(train_data),
            "val_samples":   len(val_data),
        },
        "final_metrics": {
            "best_epoch":          best_epoch,
            "best_val_loss":       round(best_val_loss, 6),
            "final_train_loss":    history[-1]["train_loss"] if history else None,
            "final_val_loss":      history[-1]["val_loss"]   if history else None,
        },
        "checkpoints": {
            "best":   str(MODEL_SAVE_DIR / BEST_MODEL_FILE),
            "latest": str(MODEL_SAVE_DIR / LATEST_MODEL_FILE),
            "legacy": str(legacy_path),
        },
        "history": history,
    }

    metadata_path = MODEL_SAVE_DIR / METADATA_FILE
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info("-" * 60)
    logger.info("Training complete in %.1f s", elapsed_total)
    logger.info("Best val loss: %.6f at epoch %d", best_val_loss, best_epoch)
    logger.info("Best model:    %s", best_path)
    logger.info("Metadata:      %s", metadata_path)
    logger.info("=" * 60)

    return str(best_path)


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="AI House Architect — Layout Model Training")
    parser.add_argument("--epochs",     type=int,   default=50)
    parser.add_argument("--batch-size", type=int,   default=32)
    parser.add_argument("--lr",         type=float, default=3e-3)
    parser.add_argument("--seed",       type=int,   default=42)
    parser.add_argument("--patience",   type=int,   default=12)
    parser.add_argument("--device",     type=str,   default="cpu",
                        help="cpu or cuda")
    args = parser.parse_args()

    train_layout_model(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        seed=args.seed,
        patience=args.patience,
        device_str=args.device,
    )


if __name__ == "__main__":
    main()
