import unittest
import sys
import threading
import time
from pathlib import Path
from PySide6.QtWidgets import QApplication
from poi.interface.models import DecisionType
from poi.ui.app import GUIConfirmationManager, EngineSignals

# Absolute path setup
sys.path.append("D:/TariqAI/src")

class Phase9RealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a dummy app for signals to work
        cls.app = QApplication.instance()
        if not cls.app:
            cls.app = QApplication(sys.argv)

    def test_gui_bridge_logical_flow(self):
        """Verify GUIConfirmationManager correctly waits and receives decision."""
        from poi.iml.layer import IdentityMemoryLayer
        
        emitter = EngineSignals()
        iml = IdentityMemoryLayer()
        bridge = GUIConfirmationManager(iml, emitter)
        
        decision_receiver = []
        
        def simulate_engine():
            # This simulates the POICore running in a background thread
            res = bridge.request_human_oversight(
                "FILE_OPERATION", "sig_test", "MEDIUM", "file_create", {"path": "test.txt"}
            )
            decision_receiver.append(res)

        engine_thread = threading.Thread(target=simulate_engine)
        
        # Connect signal to simulate a user click after a delay
        def handle_request(req):
            # Simulate waiting 1 second then clicking 'Approve Once'
            time.sleep(1)
            bridge.set_user_decision(DecisionType.APPROVE_ONCE)

        emitter.request_oversight_signal.connect(handle_request)
        
        start_time = time.time()
        engine_thread.start()
        
        # Wait for thread but PROCESS EVENTS to allow signals to flow
        while engine_thread.is_alive() and (time.time() - start_time < 5):
            self.app.processEvents()
            time.sleep(0.1)
            
        duration = time.time() - start_time
        
        self.assertTrue(engine_thread.is_alive() == False, "Thread did not complete (deadlock?)")
        self.assertEqual(len(decision_receiver), 1)
        self.assertEqual(decision_receiver[0].decision, DecisionType.APPROVE_ONCE)
        self.assertGreater(duration, 0.5, "Bridge did not actually wait for simulated user input.")
        print(f"[PH9_REAL] GUI Bridge logic verified. Wait time: {duration:.2f}s")

if __name__ == "__main__":
    unittest.main()
