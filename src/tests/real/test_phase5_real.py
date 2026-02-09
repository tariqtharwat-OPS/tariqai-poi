import sys
from pathlib import Path
import unittest

# Absolute path setup
PROJECT_ROOT = "D:/TariqAI"
sys.path.append(f"{PROJECT_ROOT}/src")

from poi.core import POICore
from poi.interface.models import UserDecision, DecisionType

class Phase5RealWorldTest(unittest.TestCase):
    def setUp(self):
        self.poi = POICore()
        self.test_dir = Path("D:/TariqAI/logs/test_real_ph5")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.test_file = self.test_dir / "governed_file.txt"
        
        # Reset trust for this specific test context
        self.intent_type = "FILE_OPERATION"
        # We'll calculate the signature later in the test

    def test_trust_escalation_lifecycle(self):
        """Simulate real-world: Block -> Ask -> Approve Always -> Auto-ACT."""
        intent = f"Create file {self.test_file}"
        
        # 1. SETUP INTERFACE MOCK
        class LifecycleMock:
            def __init__(self): self.approvals = 0
            def request_human_oversight(self, *args, **kwargs):
                self.approvals += 1
                return UserDecision(request_id="real", decision=DecisionType.APPROVE_ALWAYS)
        
        mock_ui = LifecycleMock()
        self.poi.interface = mock_ui

        # 2. ESCALATION (Phase 1-4 Rules: 5 approvals needed)
        print("\n[REAL_TEST] Starting Trust Escalation Loop...")
        for i in range(5):
            res = self.poi.handle_request(intent)
            self.assertEqual(res["status"], "SUCCESS")
            # Cleanup for next loop iteration
            if self.test_file.exists(): self.test_file.unlink()

        # 3. VERIFY AUTO-ACT
        # Reset mock call count to ensure it's NOT called this time
        mock_ui.approvals = 0
        print("[REAL_TEST] Verifying Autonomous Execution (ACT)...")
        res_auto = self.poi.handle_request(intent)
        
        self.assertEqual(res_auto["status"], "SUCCESS")
        self.assertEqual(mock_ui.approvals, 0, "Autonomous execution should NOT have asked for permission.")
        self.assertTrue(self.test_file.exists())

    def tearDown(self):
        if self.test_file.exists(): self.test_file.unlink()
        if self.test_dir.exists(): self.test_dir.rmdir()

if __name__ == "__main__":
    unittest.main()
