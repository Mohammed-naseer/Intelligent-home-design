"""
AI House Architect — FastAPI Routes

All intelligence is local (no external AI APIs):
  POST /api/v2/generate-designs      — Full pipeline: analyze → layout → optimize → score
  POST /api/v2/analyze-requirements  — Parse raw user input into normalized spec
  POST /api/v2/whatif-redesign       — Apply What-If change and re-optimize
  POST /api/v2/cost-estimate         — Construction cost breakdown
  POST /api/v2/cultural-evaluation   — Cultural / Vastu alignment score
  POST /api/v2/feedback              — Log user design feedback for adaptive retraining
  POST /api/v2/trigger-retrain       — Trigger background model retraining
  GET  /api/v2/analytics             — Usage and model performance analytics
  GET  /api/v2/evaluation-metrics    — Benchmark: Baseline vs ML vs Optimized
  GET  /api/health                   — Health check
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ai.requirement_analyzer import requirement_analyzer
from ai.cultural_engine import cultural_engine
from ai.cost_engine import cost_engine
from ai.whatif_engine import whatif_engine
from ai.adaptive_pipeline import adaptive_pipeline
from optimization.layout_optimizer import layout_optimizer
from training.evaluate_model import run_benchmark_evaluation

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Health ─────────────────────────────────────────────────────────────────────

@router.get("/health", tags=["System"])
async def health() -> dict:
    """Basic health check — confirms backend is alive."""
    from pathlib import Path
    base = Path(__file__).parent.parent
    layout_ready  = (base / "models" / "layout_model" / "pytorch_layout_model.pt").exists()
    quality_ready = (base / "models" / "quality_model" / "quality_regressor.pkl").exists()
    return {
        "status":        "healthy",
        "layout_model":  "loaded" if layout_ready  else "fallback (procedural)",
        "quality_model": "loaded" if quality_ready else "fallback (heuristic)",
        "engine":        "Local PyTorch + Scikit-Learn + Shapely",
    }


# ── Core Design Pipeline ───────────────────────────────────────────────────────

@router.post("/v2/analyze-requirements", tags=["Design"])
async def analyze_requirements(raw_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses and normalizes raw user architectural requirements into a structured spec.
    Returns room counts, validated plot dimensions, style preferences, and inferred constraints.
    """
    try:
        spec = requirement_analyzer.analyze(raw_input)
        return {"status": "success", "specification": spec.model_dump()}
    except Exception as exc:
        logger.exception("Requirement analysis failed")
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/v2/generate-designs", tags=["Design"])
async def generate_designs(raw_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full AI pipeline:
    1. Analyze and normalize requirements
    2. Generate 15 candidate floor plan layouts (PyTorch-guided)
    3. Validate each candidate with Shapely geometry constraints
    4. Score each with Scikit-Learn quality predictor
    5. Pareto-optimize for space efficiency, flow, light, and privacy
    6. Return top-3 designs with cost estimates and cultural alignment scores
    """
    try:
        spec = requirement_analyzer.analyze(raw_input)
        req_dict = spec.model_dump()
        priority = raw_input.get("priority", "balanced")

        top_designs = layout_optimizer.generate_and_optimize(
            req_dict, num_candidates=15, priority=priority
        )

        for design in top_designs:
            design["cost_estimate"]        = cost_engine.estimate_cost(req_dict, design["rooms"])
            design["cultural_evaluation"]  = cultural_engine.evaluate(design["rooms"], spec.cultural_preference)

        return {
            "status":       "success",
            "requirements": req_dict,
            "designs":      top_designs,
        }
    except Exception as exc:
        logger.exception("Design generation failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/v2/whatif-redesign", tags=["Design"])
async def whatif_redesign(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies a structured What-If redesign command (e.g., 'Make master bedroom larger',
    'Add another bathroom on floor 2') and re-runs Pareto optimization on updated layout.
    """
    try:
        reqs    = payload.get("current_requirements", {})
        rooms   = payload.get("current_rooms", [])
        command = payload.get("action_command", "Make master bedroom larger")
        result  = whatif_engine.apply_redesign(reqs, rooms, command)
        return {"status": "success", "result": result}
    except Exception as exc:
        logger.exception("What-If redesign failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ── Supporting Endpoints ───────────────────────────────────────────────────────

@router.post("/v2/cost-estimate", tags=["Analysis"])
async def get_cost_estimate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns local construction cost estimate with per-category breakdown.
    Based on sq-footage, budget tier, architectural style, and regional rates.
    """
    try:
        reqs     = payload.get("requirements", {})
        rooms    = payload.get("rooms", [])
        estimate = cost_engine.estimate_cost(reqs, rooms)
        return {"status": "success", "cost_estimate": estimate}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/v2/cultural-evaluation", tags=["Analysis"])
async def get_cultural_evaluation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates cultural/traditional design alignment (Vastu Shastra, Feng Shui, etc.)
    Returns per-room compliance scores and overall cultural alignment percentage.
    """
    try:
        rooms      = payload.get("rooms", [])
        preference = payload.get("cultural_preference", "vastu")
        result     = cultural_engine.evaluate(rooms, preference)
        return {"status": "success", "cultural_evaluation": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Adaptive Learning ──────────────────────────────────────────────────────────

@router.post("/v2/feedback", tags=["Adaptive Learning"])
async def submit_feedback(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Logs user design selection feedback into the adaptive training dataset.
    This data is used to fine-tune the local ML models on the next retrain cycle.
    """
    try:
        result = adaptive_pipeline.log_feedback(
            requirements    = payload.get("requirements", {}),
            selected_design = payload.get("selected_design", {}),
            rejected_designs= payload.get("rejected_designs", []),
            user_rating     = payload.get("user_rating", 5),
            comments        = payload.get("comments", ""),
        )
        return {"status": "success", "result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/v2/trigger-retrain", tags=["Adaptive Learning"])
async def trigger_retrain() -> Dict[str, Any]:
    """
    Triggers a background retraining cycle using accumulated feedback data.
    Retrains PyTorch layout model and Scikit-Learn quality predictor.
    """
    try:
        result = adaptive_pipeline.trigger_retrain()
        return {"status": "success", "retrain_result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/v2/analytics", tags=["Analytics"])
async def get_analytics() -> Dict[str, Any]:
    """Returns application usage telemetry, space efficiency trends, and model version history."""
    try:
        data = adaptive_pipeline.get_analytics()
        return {"status": "success", "analytics": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/v2/evaluation-metrics", tags=["Analytics"])
async def get_evaluation_metrics() -> Dict[str, Any]:
    """
    Runs empirical benchmark comparing three approaches:
    - Baseline (random layout)
    - ML-guided (PyTorch layout model)
    - Optimized (ML + Pareto + Shapely constraints)
    Returns mean quality scores, constraint satisfaction rates, and improvement deltas.
    """
    try:
        bench = run_benchmark_evaluation(num_trials=12)
        return {"status": "success", "evaluation": bench}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
