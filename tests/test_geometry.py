"""
test_geometry.py — Shapely constraint engine geometry tests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from geometry.constraint_engine import constraint_engine


class TestConstraintEngine(unittest.TestCase):

    def _make_reqs(self, w=50.0, l=60.0, floors=1, beds=2, baths=1):
        return {
            "plot_width": w,
            "plot_length": l,
            "floors": floors,
            "bedrooms": beds,
            "bathrooms": baths,
        }

    def test_valid_layout_passes(self):
        reqs = self._make_reqs()
        rooms = [
            {"id": "lr",  "name": "Living Room",  "type": "living_room",  "x": 2.0,  "y": 2.0,  "width": 16.0, "height": 14.0, "floor": 1},
            {"id": "k",   "name": "Kitchen",       "type": "kitchen",       "x": 20.0, "y": 2.0,  "width": 12.0, "height": 10.0, "floor": 1},
            {"id": "b1",  "name": "Bedroom 1",     "type": "bedroom_1",     "x": 2.0,  "y": 20.0, "width": 14.0, "height": 12.0, "floor": 1},
            {"id": "b2",  "name": "Bedroom 2",     "type": "bedroom_2",     "x": 20.0, "y": 20.0, "width": 14.0, "height": 12.0, "floor": 1},
            {"id": "bt1", "name": "Bathroom 1",    "type": "bathroom_1",    "x": 36.0, "y": 20.0, "width":  8.0, "height":  7.0, "floor": 1},
        ]
        is_valid, violations = constraint_engine.validate_layout(rooms, reqs)
        self.assertTrue(is_valid, f"Expected valid layout, got violations:\n" + "\n".join(violations))

    def test_overlapping_rooms_detected(self):
        reqs = self._make_reqs()
        rooms = [
            {"id": "r1", "name": "Room 1", "type": "bedroom_1",  "x": 5.0,  "y": 5.0,  "width": 15.0, "height": 15.0, "floor": 1},
            {"id": "r2", "name": "Room 2", "type": "bathroom_1", "x": 10.0, "y": 10.0, "width": 15.0, "height": 15.0, "floor": 1},
        ]
        is_valid, violations = constraint_engine.validate_layout(rooms, reqs)
        self.assertFalse(is_valid)
        self.assertTrue(any("overlap" in v.lower() for v in violations))

    def test_out_of_bounds_room_detected(self):
        reqs = self._make_reqs(w=30.0, l=30.0)
        rooms = [
            {"id": "big", "name": "Oversized Room", "type": "living_room", "x": 20.0, "y": 20.0, "width": 25.0, "height": 25.0, "floor": 1},
            {"id": "bt1", "name": "Bathroom 1",     "type": "bathroom_1",  "x": 2.0,  "y": 2.0,  "width":  6.0, "height":  5.0, "floor": 1},
        ]
        is_valid, violations = constraint_engine.validate_layout(rooms, reqs)
        self.assertFalse(is_valid)

    def test_missing_bedrooms_detected(self):
        reqs = self._make_reqs(beds=3, baths=2)
        rooms = [
            {"id": "lr",  "name": "Living Room", "type": "living_room",  "x": 2.0, "y": 2.0, "width": 16.0, "height": 14.0, "floor": 1},
            {"id": "bt1", "name": "Bathroom 1",  "type": "bathroom_1",   "x": 2.0, "y": 20.0, "width": 8.0,  "height": 7.0,  "floor": 1},
            {"id": "bt2", "name": "Bathroom 2",  "type": "bathroom_2",   "x": 12.0,"y": 20.0, "width": 8.0,  "height": 7.0,  "floor": 1},
        ]
        is_valid, violations = constraint_engine.validate_layout(rooms, reqs)
        self.assertFalse(is_valid)
        self.assertTrue(any("bedroom" in v.lower() for v in violations))

    def test_missing_staircase_multifloor(self):
        reqs = self._make_reqs(floors=2, beds=1, baths=1)
        rooms = [
            {"id": "lr",  "name": "Living Room", "type": "living_room", "x": 2.0, "y": 2.0,  "width": 16.0, "height": 14.0, "floor": 1},
            {"id": "b1",  "name": "Bedroom 1",   "type": "bedroom_1",   "x": 2.0, "y": 20.0, "width": 14.0, "height": 12.0, "floor": 2},
            {"id": "bt1", "name": "Bathroom 1",  "type": "bathroom_1",  "x": 2.0, "y": 34.0, "width":  8.0, "height":  7.0, "floor": 1},
        ]
        is_valid, violations = constraint_engine.validate_layout(rooms, reqs)
        self.assertFalse(is_valid)
        self.assertTrue(any("staircase" in v.lower() for v in violations))


if __name__ == "__main__":
    unittest.main()
