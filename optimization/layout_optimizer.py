"""
Optimization Engine Module - AI House Architect
Multi-candidate floor-plan synthesis, constraint filtering, ML quality evaluation, and goal-directed optimization.
"""

from typing import List, Dict, Any
from inference.layout_generator import layout_generator
from inference.quality_predictor import quality_predictor
from geometry.constraint_engine import constraint_engine


class LayoutOptimizer:
    """Multi-candidate design generator and Pareto optimizer."""

    def __init__(self):
        pass

    def generate_and_optimize(
        self,
        requirements: Dict[str, Any],
        num_candidates: int = 15,
        priority: str = "balanced"
    ) -> List[Dict[str, Any]]:
        """
        Generates candidate batch, validates constraints, predicts ML quality scores,
        optimizes according to priority, and returns top 3 candidate designs.
        """
        candidates = []

        for seed in range(num_candidates):
            raw_rooms = layout_generator.generate(requirements, candidate_seed=seed)

            # Fix up coordinates to guarantee valid bounds if slightly off
            cleaned_rooms = self._clean_room_geometry(raw_rooms, requirements)

            is_valid, violations = constraint_engine.validate_layout(cleaned_rooms, requirements)

            layout_obj = {
                "candidate_id": f"candidate_{seed+1}",
                "rooms": cleaned_rooms,
                "is_valid": is_valid,
                "violations": violations,
            }

            metrics = quality_predictor.predict(layout_obj, requirements)
            layout_obj["metrics"] = metrics

            # Priority weighted score
            weighted_score = self._compute_weighted_score(metrics, priority)
            layout_obj["weighted_score"] = weighted_score

            candidates.append(layout_obj)

        # Separate valid candidates; fallback to best invalid if none valid
        valid_candidates = [c for c in candidates if c["is_valid"]]
        if not valid_candidates:
            valid_candidates = candidates

        # Sort descending by weighted score
        valid_candidates.sort(key=lambda c: c["weighted_score"], reverse=True)

        # Select top 3 distinct candidate designs
        top_candidates = valid_candidates[:3]

        # Format returned designs with labels (Design A, Design B ⭐, Design C)
        formatted_designs = []
        labels = ["Design A - Balanced Concept", "Design B - Premium Efficiency ⭐", "Design C - Spacious Layout"]
        for idx, cand in enumerate(top_candidates):
            label = labels[idx] if idx < len(labels) else f"Design {chr(65+idx)}"
            formatted_designs.append({
                "id": f"design_{idx+1}",
                "label": label,
                "is_recommended": idx == 1 or idx == 0,
                "rooms": cand["rooms"],
                "metrics": cand["metrics"],
                "weighted_score": cand["weighted_score"],
                "is_valid": cand["is_valid"],
                "violations": cand["violations"],
            })

        return formatted_designs

    def _clean_room_geometry(self, rooms: List[Dict[str, Any]], req: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ensures all room bounds stay strictly within plot limits."""
        plot_w = float(req.get("plot_width", req.get("plot", {}).get("width", 50.0)))
        plot_l = float(req.get("plot_length", req.get("plot", {}).get("length", 50.0)))

        cleaned = []
        for r in rooms:
            w = max(6.0, min(r.get("width", 10.0), plot_w - 4.0))
            h = max(6.0, min(r.get("height", 10.0), plot_l - 4.0))
            x = max(2.0, min(r.get("x", 2.0), plot_w - w - 2.0))
            y = max(2.0, min(r.get("y", 2.0), plot_l - h - 2.0))

            room_copy = dict(r)
            room_copy["x"] = round(x, 1)
            room_copy["y"] = round(y, 1)
            room_copy["width"] = round(w, 1)
            room_copy["height"] = round(h, 1)
            cleaned.append(room_copy)
        return cleaned

    def _compute_weighted_score(self, metrics: Dict[str, float], priority: str) -> float:
        """Applies objective weighting depending on user priority."""
        if priority == "max_space":
            w = {"space_utilization": 0.4, "requirement_match": 0.3, "overall_score": 0.3}
        elif priority == "natural_light":
            w = {"natural_light": 0.4, "circulation": 0.3, "overall_score": 0.3}
        elif priority == "privacy":
            w = {"privacy": 0.4, "connectivity": 0.3, "overall_score": 0.3}
        elif priority == "lowest_cost":
            w = {"space_utilization": 0.3, "furniture_fit": 0.3, "overall_score": 0.4}
        else:  # balanced / default
            return metrics.get("overall_score", 90.0)

        score = sum(metrics.get(k, 85.0) * weight for k, weight in w.items())
        return round(score, 1)


layout_optimizer = LayoutOptimizer()
