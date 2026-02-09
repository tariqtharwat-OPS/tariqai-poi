import sys
import unittest
from pathlib import Path

# Absolute path setup
PROJECT_ROOT = "D:/TariqAI"
sys.path.append(f"{PROJECT_ROOT}/src")

from poi.core import POICore

class Phase6SmokeTest(unittest.TestCase):
    def setUp(self):
        self.poi = POICore()

    def test_dashboard_components(self):
        """Verify dashboard can access combined audit data."""
        from poi.interface.dashboard import POIDashboard
        dash = POIDashboard(self.poi.iml)
        history = self.poi.iml.get_full_audit_history()
        self.assertIn("intents", history)
        self.assertIn("decisions", history)

    def test_decision_logging(self):
        """Verify IML explicitly logs human decisions."""
        self.poi.iml.log_human_decision("test_req", "APPROVE_ONCE", {"context_signature": "smoke_sig"})
        history = self.poi.iml.get_full_audit_history()
        self.assertTrue(any(d["request_id"] == "test_req" for d in history["decisions"]))

if __name__ == "__main__":
    unittest.main()
