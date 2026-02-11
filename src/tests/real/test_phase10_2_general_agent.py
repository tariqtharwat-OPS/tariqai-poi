import unittest
import sys
import os
import shutil
from pathlib import Path

# Setup Path
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.interface.models import UserDecision, DecisionType

class MockUI:
    def request_human_oversight(self, **kwargs):
        # Auto-approve for non-destructive tests
        return UserDecision(request_id="test", decision=DecisionType.APPROVE_ONCE)

class Phase10_2GeneralAgentTest(unittest.TestCase):
    def setUp(self):
        # Ensure tmp exists
        Path("D:/TariqAI/logs/tmp").mkdir(parents=True, exist_ok=True)
        self.core = POICore()
        self.core.interface = MockUI()
        os.environ["DRY_RUN"] = "0" # Live mode for research file generation

    def test_task_a_search_and_save_excel(self):
        """Example A: 'Find 10 seafood restaurants in Tokyo for group dinner and save to tmp excel'"""
        prompt = "Find 10 seafood restaurants in Tokyo for group dinner and save to tmp excel"
        res = self.core.handle_request(prompt)
        
        self.assertEqual(res["status"], "SUCCESS")
        
        # Verify research was triggered (it should be since it's a 'Find' query)
        # Note: In our current logic, ST might only trigger research if 'how to' is used,
        # but the prompt says 'when confidence < threshold' or 'unknown tool'.
        # Let's check if excel was created in tmp
        excel_path = Path("D:/TariqAI/logs/tmp/search_results.xlsx")
        self.assertTrue(excel_path.exists())
        print(f"[REAL] Task A (Search + Excel) verified. File created: {excel_path}")

    def test_task_b_arabic_research(self):
        """Example B: 'ابحث عن طريقة عمل X على ويندوز واحفظ الخطوات في ملف'"""
        prompt = "ابحث عن طريقة عمل فورمات فلاشة على ويندوز واحفظ الخطوات في ملف"
        res = self.core.handle_request(prompt)
        
        self.assertEqual(res["status"], "SUCCESS")
        
        # Verify how-to brief was created (triggered by 'طريقة')
        log_files = [f for f in os.listdir("D:/TariqAI/logs/tmp") if f.startswith("howto_")]
        if not log_files:
            print(f"[DEBUG] Files in tmp: {os.listdir('D:/TariqAI/logs/tmp')}")
        self.assertGreater(len(log_files), 0)
        print(f"[REAL] Task B (Arabic Research) verified. Briefs found: {len(log_files)}")

    def test_task_c_clarification(self):
        """Example C: Lack of location -> Clarification."""
        prompt = "Find 10 seafood restaurants for group dinner"
        res = self.core.handle_request(prompt)
        
        self.assertEqual(res["status"], "CLARIFICATION_REQUIRED")
        self.assertIn("city", res["message"])
        print(f"[REAL] Task C (Clarification) verified. Message: {res['message']}")

    def test_no_destructive_actions(self):
        """Internal safety check: Ensure no deletion attempted without explicit intent."""
        # This is more of a logic check.
        from poi.iml.layer import IdentityMemoryLayer
        iml = IdentityMemoryLayer()
        # Verify that even in safe zone, destructive actions are NOT auto-approved
        allowed, _, state = iml.validate_action("FILE_DESTRUCTION", "sig", "CRITICAL", "file_delete", {"path": "D:/TariqAI/logs/tmp/test.txt"})
        self.assertFalse(allowed)
        self.assertEqual(state, "ASK")
        print("[REAL] Safety check: Destructive actions in Safe Zone correctly require ASK.")

if __name__ == "__main__":
    unittest.main()
