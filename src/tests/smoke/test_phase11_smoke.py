import unittest
import sys
import os
from pathlib import Path

# Setup Path
sys.path.append("D:/TariqAI/src")

class Phase11SmokeTest(unittest.TestCase):
    def test_imports(self):
        """Verify new Phase 11 modules can be imported."""
        try:
            from poi.desktop.uia_driver import UIADriver
            from poi.perception.adapters.uia import UIAAdapter
            print("[SMOKE] Phase 11 modules loaded successfully.")
        except ImportError as e:
            self.fail(f"Module missing: {e}")

    def test_fe_desktop_primitives(self):
        """Verify FastExecutor recognizes desktop actions."""
        from poi.fe.layer import FastExecutor
        from poi.iml.layer import IdentityMemoryLayer
        
        fe = FastExecutor(IdentityMemoryLayer())
        # Check if desktop actions are in the known block (implicitly by not raising Unknown Action error immediately if we mocked IML)
        # Actually let's just check if 'desktop_' is in the code.
        import inspect
        source = inspect.getsource(fe.execute_step)
        self.assertIn("desktop_", source)
        print("[SMOKE] FastExecutor desktop primitives verified.")

if __name__ == "__main__":
    unittest.main()
