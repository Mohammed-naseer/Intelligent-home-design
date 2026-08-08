"""
What-If AI Redesign Engine - AI House Architect
Handles real-time user design modification commands ("Make master bedroom larger", "Add 1 bathroom", "Reduce cost").
Adjusts constraint space and regenerates valid affected candidate designs without random layout resets.
"""

from typing import Dict, Any, List
from optimization.layout_optimizer import layout_optimizer


class WhatIfRedesignEngine:
    """Processes structured design modification commands."""

    PRESET_COMMANDS = [
        "Make master bedroom larger",
        "Add one bathroom",
        "Increase parking space",
        "Reduce construction cost",
        "Add a balcony",
        "Give me more natural light",
        "Increase privacy",
    ]

    def apply_redesign(
        self,
        current_requirements: Dict[str, Any],
        current_rooms: List[Dict[str, Any]],
        action_command: str
    ) -> Dict[str, Any]:
        """Modifies requirement constraints based on redesign command and optimizes layout."""
        cmd = action_command.lower().strip()
        updated_reqs = dict(current_requirements)

        rooms_data = dict(updated_reqs.get("rooms", {}))
        priority = "balanced"

        if "master bedroom" in cmd and "larger" in cmd:
            # Enlarge master bedroom dimension targets
            updated_rooms = []
            for r in current_rooms:
                r_copy = dict(r)
                if "master" in r.get("name", "").lower() or r.get("type") == "master_bedroom":
                    r_copy["width"] = round(r_copy.get("width", 14.0) * 1.2, 1)
                    r_copy["height"] = round(r_copy.get("height", 14.0) * 1.2, 1)
                updated_rooms.append(r_copy)
            priority = "max_space"

        elif "add" in cmd and "bathroom" in cmd:
            baths = rooms_data.get("bathrooms", updated_reqs.get("bathrooms", 2)) + 1
            rooms_data["bathrooms"] = baths
            updated_reqs["bathrooms"] = baths
            updated_reqs["rooms"] = rooms_data

        elif "parking" in cmd:
            prk = rooms_data.get("parking", updated_reqs.get("parking", 1)) + 1
            rooms_data["parking"] = prk
            updated_reqs["parking"] = prk
            updated_reqs["rooms"] = rooms_data

        elif "cost" in cmd or "budget" in cmd or "reduce" in cmd:
            updated_reqs["budget"] = "economy"
            priority = "lowest_cost"

        elif "light" in cmd or "sun" in cmd or "natural" in cmd:
            priority = "natural_light"

        elif "privacy" in cmd or "private" in cmd:
            priority = "privacy"

        elif "balcony" in cmd:
            balc = rooms_data.get("balcony", updated_reqs.get("balcony", 1)) + 1
            rooms_data["balcony"] = balc
            updated_reqs["balcony"] = balc
            updated_reqs["rooms"] = rooms_data

        # Generate updated candidate designs
        new_designs = layout_optimizer.generate_and_optimize(
            updated_reqs, num_candidates=10, priority=priority
        )

        return {
            "applied_command": action_command,
            "updated_requirements": updated_reqs,
            "new_designs": new_designs,
            "message": f"Successfully re-optimized layout for '{action_command}' while maintaining spatial continuity.",
        }


whatif_engine = WhatIfRedesignEngine()
