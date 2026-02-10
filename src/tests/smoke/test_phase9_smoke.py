import unittest
import sys
from pathlib import Path

# Absolute path setup
sys.path.append("D:/TariqAI/src")

class Phase9SmokeTest(unittest.TestCase):
    def test_gui_imports(self):
        """Verify PySide6 and UI modules can be imported."""
        try:
            from PySide6.QtWidgets import QApplication
            from poi.ui.app import TariqMainWindow
            print("[SMOKE] PySide6 and Tariq UI modules loaded successfully.")
        except ImportError as e:
            self.fail(f"GUI Dependency or module missing: {e}")

if __name__ == "__main__":
    unittest.main()
