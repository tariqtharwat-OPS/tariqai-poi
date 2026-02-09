import unittest
import sys
import os
from pathlib import Path

# Absolute path setup
sys.path.append("D:/TariqAI/src")

class Phase7SmokeTest(unittest.TestCase):
    def test_imports(self):
        """Verify new dependencies are available."""
        try:
            import docx
            import openpyxl
            import playwright
            print("[SMOKE] All Phase 7 dependencies (docx, openpyxl, playwright) loaded.")
        except ImportError as e:
            self.fail(f"Dependency missing: {e}")

    def test_dry_run_flag(self):
        """Verify FE correctly reads DRY_RUN environment variable."""
        from poi.fe.layer import FastExecutor
        from poi.iml.layer import IdentityMemoryLayer
        
        iml = IdentityMemoryLayer()
        
        # Test 1: DRY_RUN Active
        os.environ["DRY_RUN"] = "1"
        fe_dry = FastExecutor(iml)
        self.assertTrue(fe_dry.dry_run)
        
        # Test 2: DRY_RUN Inactive
        os.environ["DRY_RUN"] = "0"
        fe_live = FastExecutor(iml)
        self.assertFalse(fe_live.dry_run)

    def test_action_recognition(self):
        """Verify new Phase 7 actions are handled by FastExecutor."""
        from poi.fe.layer import FastExecutor
        from poi.iml.layer import IdentityMemoryLayer
        
        iml = IdentityMemoryLayer()
        fe = FastExecutor(iml)
        fe.dry_run = True # Safety
        
        actions = {
            "word_create": {"path": "logs/smoke.docx"},
            "excel_create": {"path": "logs/smoke.xlsx"},
            "browser_open": {"url": "about:blank"}
        }
        for action, params in actions.items():
            res = fe.execute_step({"action": action, "params": params}, {"bypass_governance": True})
            self.assertNotEqual(res["status"], "ERROR", f"Action {action} should be recognized.")
            self.assertTrue(res.get("dry_run") or res["status"] == "SUCCESS" or res["status"] == "FAILURE", f"Action {action} failed: {res.get('message')}")

if __name__ == "__main__":
    unittest.main()
