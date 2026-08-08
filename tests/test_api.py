"""
test_api.py — FastAPI route tests for AI House Architect v2 endpoints
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
try:
    from fastapi.testclient import TestClient
    from main import app
    CLIENT_AVAILABLE = True
except Exception:
    CLIENT_AVAILABLE = False


class TestV2APIRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if CLIENT_AVAILABLE:
            cls.client = TestClient(app)

    @unittest.skipUnless(CLIENT_AVAILABLE, "FastAPI TestClient not available")
    def test_analyze_requirements(self):
        payload = {
            "plot": {"length": 60.0, "width": 50.0},
            "floors": 2,
            "rooms": {"bedrooms": 4, "bathrooms": 3, "kitchen": 1, "living_dining": 1, "parking": 2, "balcony": 1, "garden": True, "home_office": False, "pooja_prayer_room": False},
            "budget": "premium",
            "architectural_style": "modern",
            "climate_location": "tropical",
            "cultural_preference": "vastu",
            "accessibility": False,
            "future_expansion": False,
        }
        res = self.client.post("/api/v2/analyze-requirements", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("specification", res.json())

    @unittest.skipUnless(CLIENT_AVAILABLE, "FastAPI TestClient not available")
    def test_generate_designs(self):
        payload = {
            "plot": {"length": 50.0, "width": 40.0},
            "floors": 1,
            "rooms": {"bedrooms": 3, "bathrooms": 2, "kitchen": 1, "living_dining": 1, "parking": 1, "balcony": 1, "garden": True, "home_office": False, "pooja_prayer_room": False},
            "budget": "standard",
            "architectural_style": "contemporary",
            "climate_location": "temperate",
            "cultural_preference": "none",
            "accessibility": False,
            "future_expansion": False,
        }
        res = self.client.post("/api/v2/generate-designs", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("designs", data)
        self.assertGreater(len(data["designs"]), 0)

    @unittest.skipUnless(CLIENT_AVAILABLE, "FastAPI TestClient not available")
    def test_cost_estimate(self):
        payload = {
            "requirements": {
                "plot_width": 50.0, "plot_length": 60.0, "floors": 2,
                "budget": "premium", "bedrooms": 4, "bathrooms": 3
            },
            "rooms": [
                {"type": "living_room", "width": 18.0, "height": 15.0},
                {"type": "master_bedroom", "width": 16.0, "height": 14.0},
            ]
        }
        res = self.client.post("/api/v2/cost-estimate", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("cost_estimate", res.json())

    @unittest.skipUnless(CLIENT_AVAILABLE, "FastAPI TestClient not available")
    def test_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
