import sys
import os
import time
from pathlib import Path

# Setup Path
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.interface.models import UserDecision, DecisionType

class AcceptanceUI:
    def __init__(self):
        self.oversight_triggered = False

    def request_human_oversight(self, **kwargs):
        self.oversight_triggered = True
        print(f"[ACCEPTANCE] Oversight triggered for: {kwargs.get('action')}")
        return UserDecision(request_id="acceptance_9_2", decision=DecisionType.APPROVE_ONCE)

def run_acceptance():
    print("="*80)
    print("🛡️  TARIQ AI POI - PHASE 9.2 STABILIZATION ACCEPTANCE")
    print("="*80)
    
    # Ensure Live Mode
    os.environ["DRY_RUN"] = "0"
    
    ui = AcceptanceUI()
    core = POICore(status_callback=lambda msg: print(f"[PROGRESS] {msg}"))
    core.interface = ui
    
    # Task 1: Safe Zone Write (Should NOT trigger ASK)
    task1 = "Open https://example.com and save html to D:/TariqAI/logs/tmp/test.html"
    print(f"\n[TASK 1] {task1}")
    core.handle_request(task1)
    
    if ui.oversight_triggered:
        print("[FAIL] Oversight was triggered for a safe zone path!")
    else:
        print("[SUCCESS] No oversight triggered for safe zone path.")

    # Reset for Task 2
    ui.oversight_triggered = False
    
    # Task 2: Outside Zone Write (Should trigger ASK)
    task2 = "Open https://example.com and save html to D:/TariqAI/logs/governed_acceptance.html"
    print(f"\n[TASK 2] {task2}")
    core.handle_request(task2)
    
    if ui.oversight_triggered:
        print("[SUCCESS] Oversight correctly triggered for governed path.")
    else:
        print("[FAIL] Oversight was NOT triggered for governed path!")
        
    print("\n" + "="*80)
    print("ACCEPTANCE RUN COMPLETE")
    print("="*80)

if __name__ == "__main__":
    run_acceptance()
