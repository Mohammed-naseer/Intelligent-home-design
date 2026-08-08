"""
Local Cost Intelligence Engine - AI House Architect
Provides granular itemized construction cost estimation based on area, floors, material tier, region, and MEP specs.
Outputs conceptual cost breakdowns and total budget projections.
"""

from typing import Dict, Any, List


COST_PER_SQFT_BASE = {
    "economy": 1600.0,
    "standard": 2200.0,
    "premium": 3200.0,
    "luxury": 4500.0,
}


class CostEngine:
    """Calculates granular residential construction cost estimates."""

    def estimate_cost(self, requirements: Dict[str, Any], rooms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates itemized construction cost breakdown."""
        plot_w = float(requirements.get("plot_width", requirements.get("plot", {}).get("width", 50.0)))
        plot_l = float(requirements.get("plot_length", requirements.get("plot", {}).get("length", 50.0)))
        floors = int(requirements.get("floors", 1))
        budget_tier = str(requirements.get("budget", "standard")).lower()

        base_rate = COST_PER_SQFT_BASE.get(budget_tier, 2200.0)

        total_room_area = sum(r.get("width", 0) * r.get("height", 0) for r in rooms)
        built_up_area = max(total_room_area, plot_w * plot_l * floors * 0.7)

        total_est = built_up_area * base_rate

        # Percentage allocations
        structure_cost = round(total_est * 0.40, -3)
        flooring_cost = round(total_est * 0.12, -3)
        doors_windows_cost = round(total_est * 0.12, -3)
        electrical_cost = round(total_est * 0.10, -3)
        plumbing_cost = round(total_est * 0.10, -3)
        interior_finishes = round(total_est * 0.16, -3)

        calculated_total = (
            structure_cost
            + flooring_cost
            + doors_windows_cost
            + electrical_cost
            + plumbing_cost
            + interior_finishes
        )

        currency_symbol = "₹"

        return {
            "currency": "INR",
            "currency_symbol": currency_symbol,
            "built_up_area_sqft": round(built_up_area, 1),
            "rate_per_sqft": base_rate,
            "budget_tier": budget_tier.capitalize(),
            "breakdown": [
                {"category": "Civil Structure & Foundation", "percentage": 40, "amount": structure_cost},
                {"category": "Flooring & Tiling", "percentage": 12, "amount": flooring_cost},
                {"category": "Doors, Windows & Glazing", "percentage": 12, "amount": doors_windows_cost},
                {"category": "Electrical & HVAC Provisioning", "percentage": 10, "amount": electrical_cost},
                {"category": "Plumbing & Sanitary Fittings", "percentage": 10, "amount": plumbing_cost},
                {"category": "Interior Finishes & Cabinetry", "percentage": 16, "amount": interior_finishes},
            ],
            "total_estimated_cost": calculated_total,
            "disclaimer": "This is an approximate conceptual estimate for preliminary planning. Actual construction cost varies based on local site conditions, contractor selection, and material market fluctuations.",
        }


cost_engine = CostEngine()
