import unittest
import sys
import os
from pathlib import Path

# Setup Path
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.iml.layer import IdentityMemoryLayer

class Phase9SafeZoneTest(unittest.TestCase):
    def setUp(self):
        self.iml = IdentityMemoryLayer()
        # Ensure we are in LIVE mode for write testing (but we'll check IML logic)
        os.environ["DRY_RUN"] = "0"

    def test_safe_zone_auto_approval(self):
        """Verify file_write inside tmp/ is auto-approved."""
        action = "file_write"
        params = {"path": "D:/TariqAI/logs/tmp/test.html"}
        
        allowed, reason, state = self.iml.validate_action(
            "BROWSER", "sig_tmp", "LOW", action, params
        )
        
        self.assertTrue(allowed)
        self.assertEqual(reason, "Safe zone auto-approval")
        print("[TEST] Safe zone auto-approval verified for tmp/ path.")

    def test_outside_zone_ask(self):
        """Verify file_write outside tmp/ still triggers ASK (due to low trust)."""
        action = "file_write"
        params = {"path": "D:/TariqAI/logs/governed.html"}
        
        allowed, reason, state = self.iml.validate_action(
            "BROWSER", "sig_outside", "LOW", action, params
        )
        
        self.assertFalse(allowed)
        self.assertEqual(state, "ASK")
        print("[TEST] Outside zone correctly triggers ASK.")

    def test_destructive_inside_tmp_ask(self):
        """Verify destructive actions even inside tmp/ still trigger ASK."""
        action = "file_delete" # Note: IML logic currently only auto-approves 'file_write'
        params = {"path": "D:/TariqAI/logs/tmp/important.txt"}
        
        allowed, reason, state = self.iml.validate_action(
            "FILE_DESTRUCTION", "sig_tmp_del", "CRITICAL", action, params
        )
        
        self.assertFalse(allowed)
        self.assertEqual(state, "ASK")
        print("[TEST] Destructive action in tmp correctly triggers ASK.")

if __name__ == "__main__":
    unittest.main()
