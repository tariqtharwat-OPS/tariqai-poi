import unittest
import sys
from pathlib import Path

sys.path.append("D:/TariqAI/src")
from poi.tech_watch.watcher import TechWatchModule

class TestTechWatch(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("D:/TariqAI/persistent_memory/poi/tech_watch_test")
        self.watcher = TechWatchModule(report_dir=str(self.test_dir))

    def test_report_generation_no_patching(self):
        """Verify report is created but no source code is modified."""
        # 1. Capture state of a core file
        core_file = Path("D:/TariqAI/src/poi/core.py")
        original_mtime = core_file.stat().st_mtime
        
        # 2. Run watcher
        report_path = self.watcher.generate_weekly_report()
        
        # 3. Assertions
        self.assertTrue(Path(report_path).exists(), "Report should be generated.")
        self.assertEqual(core_file.stat().st_mtime, original_mtime, "Core logic MUST NOT be modified by TechWatch.")
        
        # 4. Content check
        with open(report_path, 'r') as f:
            content = f.read()
            self.assertIn("POLICY NOTICE", content)
            self.assertIn("No autonomous implementation", content)

    def tearDown(self):
        # Cleanup test reports
        if self.test_dir.exists():
            for f in self.test_dir.iterdir():
                f.unlink()
            self.test_dir.rmdir()

if __name__ == "__main__":
    unittest.main()
