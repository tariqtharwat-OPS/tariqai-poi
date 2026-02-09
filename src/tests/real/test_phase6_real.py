import sys
from pathlib import Path
import unittest
import json

# Absolute path setup
PROJECT_ROOT = "D:/TariqAI"
sys.path.append(f"{PROJECT_ROOT}/src")

from poi.core import POICore
from poi.interface.models import UserDecision, DecisionType

class Phase6RealWorldTest(unittest.TestCase):
    def setUp(self):
        self.poi = POICore()
        self.test_dir = Path("D:/TariqAI/logs/test_real_ph6")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.test_file = self.test_dir / "live_ops_task.txt"
        
        # Ensure fresh starts
        if self.test_file.exists(): self.test_file.unlink()

    def test_live_interface_decision_flow(self):
        """Simulate real-world: Intent -> Interface Block -> Decision -> Logging -> ACT."""
        print("\n[PH6_REAL] Initiating Live File Task...")
        
        # 1. Mock Interface that simulates an 'APPROVE_ALWAYS' user choice
        class LiveInterfaceMock:
            def request_human_oversight(self, *args, **kwargs):
                print(f"[UI] User selected: APPROVE_ALWAYS")
                return UserDecision(request_id="ph6_live_001", decision=DecisionType.APPROVE_ALWAYS)
        
        self.poi.interface = LiveInterfaceMock()
        
        # 2. Trigger Action (Creation)
        intent = f"Create file {self.test_file}"
        res = self.poi.handle_request(intent)
        
        # 3. VERIFY: Core Flow
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(self.test_file.exists())
        
        # 4. VERIFY: Audit Integration (History logging)
        history = self.poi.iml.get_full_audit_history()
        has_decision = any(d["request_id"] == "ph6_live_001" and d["decision"] == "approve_always" 
                           for d in history["decisions"])
        self.assertTrue(has_decision, "The user decision should be recorded in the audit history.")
        
        print("[PH6_REAL] Dashboard verification...")
        from poi.interface.dashboard import POIDashboard
        dash = POIDashboard(self.poi.iml)
        # Capture stdout to verify dashboard output briefly (omitted for brevity, just calling)
        dash.show()

    def tearDown(self):
        if self.test_file.exists(): self.test_file.unlink()
        if self.test_dir.exists(): self.test_dir.rmdir()

if __name__ == "__main__":
    unittest.main()
