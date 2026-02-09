import sys
import unittest
from pathlib import Path

# Absolute path setup
PROJECT_ROOT = "D:/TariqAI"
sys.path.append(f"{PROJECT_ROOT}/src")

from poi.core import POICore

class Phase5SmokeTest(unittest.TestCase):
    def setUp(self):
        self.poi = POICore()
        # Ensure we don't accidentally use real console input
        class SilentMock:
            def request_human_oversight(self, *args, **kwargs):
                from poi.interface.models import UserDecision, DecisionType
                return UserDecision(request_id="smoke", decision=DecisionType.REJECT)
        self.poi.interface = SilentMock()

    def test_core_initialization(self):
        """Verify all POI layers are initialized."""
        self.assertIsNotNone(self.poi.st)
        self.assertIsNotNone(self.poi.fe)
        self.assertIsNotNone(self.poi.iml)
        self.assertIsNotNone(self.poi.perception)

    def test_file_navigation_intent(self):
        """Verify ST correctly classifies file navigation."""
        decision = self.poi.st.process_intent("List files in D:/TariqAI/logs")
        self.assertEqual(decision["intent_type"], "FILE_NAVIGATION")
        self.assertEqual(decision["risk_level"], "LOW")

    def test_governance_block(self):
        """Verify IML blocks file operations by default."""
        res = self.poi.handle_request("Create file D:/TariqAI/logs/smoke_test.txt")
        self.assertEqual(res["status"], "HALTED")
        self.assertEqual(res["reason"], "User rejected action")

if __name__ == "__main__":
    unittest.main()
