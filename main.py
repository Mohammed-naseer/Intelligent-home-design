"""
AI House Architect — Application Entry Point
Local-ML powered adaptive 3D residential design & visualization system.

Endpoints:
  REST API  →  /api/...
  Swagger   →  /docs
  ReDoc     →  /redoc
  Frontend  →  http://localhost:8080/ (served from Vite dev server in development)
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ai-house-architect")

# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI House Architect",
    description=(
        "Adaptive 3D Residential Design & Visualization System.\n\n"
        "**No external AI APIs** — intelligence is powered entirely by:\n"
        "- Local **PyTorch** neural network (layout prediction)\n"
        "- Local **Scikit-Learn** random forest (quality scoring)\n"
        "- **Shapely** geometry constraint engine (overlap & boundary validation)\n"
        "- **Pareto optimization** (multi-objective design selection)\n\n"
        "Generates ranked floor-plan candidates with 3D specs, cost estimates & cultural alignment."
    ),
    version="2.0.0",
    contact={"name": "AI House Architect"},
    license_info={"name": "MIT"},
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ─────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")

# ── Serve built frontend (production) ──────────────────────────────────────────
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def _startup() -> None:
    base_dir = Path(__file__).parent

    # Auto-train if models are missing
    layout_pt  = base_dir / "models" / "layout_model" / "pytorch_layout_model.pt"
    quality_pkl = base_dir / "models" / "quality_model" / "quality_regressor.pkl"

    if not layout_pt.exists() or not quality_pkl.exists():
        logger.info("Pre-trained models not found — running training bootstrap...")
        try:
            from datasets.synthetic_generator import generate_dataset
            dataset_dir = base_dir / "datasets" / "processed"
            generate_dataset(str(dataset_dir), num_samples=400)

            from training.train_layout_model import train_layout_model
            train_layout_model(epochs=20)

            from training.train_quality_model import train_quality_model
            train_quality_model()

            logger.info("Auto-training complete.")
        except Exception as exc:
            logger.warning("Auto-training failed (%s). Using procedural fallback.", exc)
    else:
        logger.info("Pre-trained models found — skipping auto-training.")

    logger.info("=" * 60)
    logger.info("AI House Architect v2.0 — Ready")
    logger.info("  API Docs : http://localhost:8080/docs")
    logger.info("  ReDoc    : http://localhost:8080/redoc")
    logger.info("  Frontend : http://localhost:5173/ (Vite dev server)")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def _shutdown() -> None:
    logger.info("AI House Architect shutting down.")


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )
