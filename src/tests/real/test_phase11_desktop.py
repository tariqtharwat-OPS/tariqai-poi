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
        return UserDecision(request_id="test", decision=DecisionType.REJECT)

class Phase11DesktopTest(unittest.TestCase):
    def setUp(self):
        self.core = POICore()
        self.core.interface = MockUI()
        os.environ["DRY_RUN"] = "1" # Mandatory DRY_RUN for automated tests

    def test_notepad_plan_generation(self):
        """Verify plan generation for notepad task."""
        prompt = "Open notepad, type text and save to D:/TariqAI/logs/tmp/notepad_test.txt"
        # We don't execute real desktop actions in CI/automated tests, 
        # but we check if the plan includes desktop actions.
        from poi.st.layer import StrategicThinker
        from poi.iml.layer import IdentityMemoryLayer
        st = StrategicThinker(IdentityMemoryLayer())
        
        intent, decision = st.get_intent(prompt)
        self.assertEqual(intent, "DESKTOP_TASK")
        
        actions = [step["action"] for step in decision["plan"]]
        self.assertIn("desktop_hotkey", actions)
        self.assertIn("desktop_type", actions)
        self.assertIn("desktop_focus", actions)
        print("[REAL] Notepad plan generation verified.")

    def test_safety_gmail_block(self):
        """Verify Gmail deletion is blocked and provides safe assist response."""
        prompt = "Delete all spam emails in my Gmail"
        res = self.core.handle_request(prompt)
        
        # In our implementation, IML blocks it and ST returns a chat message
        # Let's check the result
        self.assertIn("prohibited", res["chat_response"] if "chat_response" in res else str(res))
        print("[REAL] Safety: Gmail deletion block verified.")

if __name__ == "__main__":
    unittest.main()
