import unittest
import sys
import os
from pathlib import Path

# Setup Path
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.research.howto import HowToResearch

class Phase10_2SmokeTest(unittest.TestCase):
    def test_imports(self):
        """Verify core and research modules can be imported."""
        try:
            from poi.research.howto import HowToResearch
            from poi.st.layer import StrategicThinker
            print("[SMOKE] Phase 10.2 modules loaded successfully.")
        except ImportError as e:
            self.fail(f"Module missing: {e}")

    def test_basic_routing(self):
        """Verify deterministic routing for Phase 10.2."""
        from poi.iml.layer import IdentityMemoryLayer
        from poi.st.layer import StrategicThinker
        
        st = StrategicThinker(IdentityMemoryLayer())
        
        # Test 1: URL -> BROWSER
        intent, _ = st.get_intent("visit https://example.com")
        self.assertEqual(intent, "BROWSER")
        
        # Test 2: .docx -> WORD
        intent, _ = st.get_intent("create report.docx")
        self.assertEqual(intent, "DOCUMENT_WORD")
        
        # Test 3: Arabic 'بحث' -> BROWSER
        intent, _ = st.get_intent("بحث عن أخبار")
        self.assertEqual(intent, "BROWSER")
        
        print("[SMOKE] Basic routing verified (EN/AR/Deterministic).")

if __name__ == "__main__":
    unittest.main()
