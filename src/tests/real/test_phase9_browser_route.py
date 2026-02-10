import unittest
import sys
import os
from pathlib import Path

# Setup Path
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.iml.layer import IdentityMemoryLayer
from poi.st.layer import StrategicThinker

class Phase9BrowserRouteTest(unittest.TestCase):
    def setUp(self):
        self.iml = IdentityMemoryLayer()
        self.st = StrategicThinker(self.iml)

    def test_route_url_and_path(self):
        """Case A: URL + save path -> must route to BROWSER plan with 3 steps."""
        prompt = "Open https://example.com and save html to D:/TariqAI/logs/example_gui.html"
        decision = self.st.process_intent(prompt)
        
        self.assertEqual(decision["intent_type"], "BROWSER")
        plan = decision["plan"]
        
        # Verify 3 steps
        actions = [s["action"] for s in plan]
        self.assertIn("browser_open", actions)
        self.assertIn("browser_extract", actions)
        self.assertIn("file_write", actions)
        
        # Verify file_write has the correct path
        file_step = next(s for s in plan if s["action"] == "file_write")
        self.assertEqual(file_step["params"]["path"], "D:/TariqAI/logs/example_gui.html")
        print("[TEST] URL + Path correctly routed to 3-step BROWSER plan.")

    def test_route_url_only(self):
        """Case B: URL only -> must route to BROWSER open + extract (no file write)."""
        prompt = "Open https://example.com"
        decision = self.st.process_intent(prompt)
        
        self.assertEqual(decision["intent_type"], "BROWSER")
        plan = decision["plan"]
        
        # Verify 2 steps (no file_write)
        actions = [s["action"] for s in plan]
        self.assertIn("browser_open", actions)
        self.assertIn("browser_extract", actions)
        self.assertNotIn("file_write", actions)
        print("[TEST] URL only correctly routed to 2-step BROWSER plan.")

if __name__ == "__main__":
    unittest.main()
