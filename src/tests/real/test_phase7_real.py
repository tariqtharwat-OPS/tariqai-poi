import unittest
import sys
import os
from pathlib import Path
from poi.core import POICore
from poi.interface.models import UserDecision, DecisionType

# Absolute path setup
sys.path.append("D:/TariqAI/src")

class Phase7RealTest(unittest.TestCase):
    def setUp(self):
        self.poi = POICore()
        self.test_dir = Path("D:/TariqAI/logs/test_ph7")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.test_file = self.test_dir / "dry_run_victim.txt"
        if self.test_file.exists(): self.test_file.unlink()

    def test_dry_run_enforcement(self):
        """Prove DRY_RUN blocks actual file writes while allowing log traces."""
        os.environ["DRY_RUN"] = "1"
        self.poi.fe.dry_run = True # Force update for existing instance
        
        print("\n[PH7_REAL] Testing DRY_RUN Enforcement...")
        
        # Provide a mock interface that approves the action (so we hit the FE logic)
        class DirectApproveMock:
            def request_human_oversight(self, *args, **kwargs):
                return UserDecision(request_id="ph7_dry_01", decision=DecisionType.APPROVE_ONCE)
        
        self.poi.interface = DirectApproveMock()
        
        res = self.poi.handle_request(f"Create a sensitive file at {self.test_file}")
        
        # Verify FE reported SUCCESS but dry_run=True
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(res["results"][0].get("dry_run"))
        
        # Verify file does NOT exist
        self.assertFalse(self.test_file.exists(), "File should NOT be created in DRY_RUN mode.")
        
        print("[PH7_REAL] DRY_RUN successfully blocked the write.")

    def test_audit_log_and_approval_flow(self):
        """Prove ASK -> Approve -> ACT cycle is reflected in audit logs."""
        os.environ["DRY_RUN"] = "0"
        self.poi.fe.dry_run = False
        
        print("\n[PH7_REAL] Testing Approval Flow & Audit Log...")
        
        # 1. Trigger an action that requires approval
        # We use a unique intent to avoid cached trust
        unique_sig = f"D:/TariqAI/logs/ph7_audit_{os.urandom(4).hex()}.txt"
        
        class MockUI:
            def request_human_oversight(self, *args, **kwargs):
                print("[UI] Approving manually for Phase 7 test.")
                return UserDecision(request_id="ph7_audit_approve", decision=DecisionType.APPROVE_ONCE)
        
        self.poi.interface = MockUI()
        self.poi.handle_request(f"Create file {unique_sig}")
        
        # 2. Check Audit Log
        log_path = Path("D:/TariqAI/persistent_memory/poi/audit_trail.log")
        with open(log_path, "r") as f:
            lines = f.readlines()
            # Find the most recent decision log for ph7_audit_approve
            # Note: DecisionType.APPROVE_ONCE.value is 'approve_once'
            has_decision = any("ph7_audit_approve" in line and "approve_once" in line for line in lines)
            self.assertTrue(has_decision, "Audit log must contain the manual approval record.")

    def tearDown(self):
        if self.test_file.exists(): self.test_file.unlink()

if __name__ == "__main__":
    unittest.main()
