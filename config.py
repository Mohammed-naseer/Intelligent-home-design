"""
AI House Architect — Configuration
No external AI API keys required. All intelligence is local.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Application Settings ────────────────────────────────────────────────────────
APP_HOST: str  = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int  = int(os.getenv("APP_PORT", "8080"))
DEBUG: bool    = os.getenv("DEBUG", "true").lower() == "true"
OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Model Paths ─────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
LAYOUT_MODEL_PT = BASE_DIR / "models" / "layout_model" / "pytorch_layout_model.pt"
QUALITY_MODEL_PKL = BASE_DIR / "models" / "quality_model" / "quality_regressor.pkl"
DATASET_DIR     = BASE_DIR / "datasets" / "processed"

# ── Training Settings ───────────────────────────────────────────────────────────
TRAINING_EPOCHS:      int = int(os.getenv("TRAINING_EPOCHS", "25"))
TRAINING_BATCH_SIZE:  int = int(os.getenv("TRAINING_BATCH_SIZE", "32"))
TRAINING_SAMPLES:     int = int(os.getenv("TRAINING_SAMPLES", "400"))
ADAPTIVE_DATA_DIR:    Path = BASE_DIR / "datasets" / "adaptive_feedback"
ADAPTIVE_DATA_DIR.mkdir(parents=True, exist_ok=True)
