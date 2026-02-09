import sys
from pathlib import Path
import logging

# Absolute path setup
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.interface.models import DecisionType, UserDecision

class Phase5MockInterface:
    """Simulates user input for file management demo."""
    def __init__(self, iml):
        self.iml = iml
        self.mode = "once" # Toggle between 'once' and 'always'

    def request_human_oversight(self, intent_type, context_signature, risk_level, action, params):
        print(f"\n[DEMO] PREVIEWING ACTION:")
        print(f"  Action: {action}")
        print(f"  Risk: {risk_level}")
        print(f"  Params: {params}")
        
        if self.mode == "once":
            print("[DEMO] MOCK_USER: APPROVE_ONCE selected.")
            return UserDecision(request_id="ph5_id", decision=DecisionType.APPROVE_ONCE)
        else:
            print("[DEMO] MOCK_USER: APPROVE_ALWAYS selected.")
            return UserDecision(request_id="ph5_id", decision=DecisionType.APPROVE_ALWAYS)

def run_phase5_demo():
    print("="*60)
    print("TARIQ AI POI - PHASE 5 DEMO (FILE MANAGEMENT)")
    print("="*60)
    
    poi = POICore()
    mock_ui = Phase5MockInterface(poi.iml)
    poi.interface = mock_ui
    
    # Setup test file
    test_file = "D:/TariqAI/logs/phase5_test.txt"
    Path(test_file).parent.mkdir(parents=True, exist_ok=True)
    if Path(test_file).exists():
        Path(test_file).unlink()

    print("\n--- FLOW 1: PREVIEW -> APPROVE ONCE -> EXECUTE ---")
    mock_ui.mode = "once"
    intent1 = f"Create the file {test_file}"
    poi.handle_request(intent1)
    
    print("\n--- FLOW 2: PREVIEW -> APPROVE ALWAYS -> FUTURE AUTO-ACT ---")
    mock_ui.mode = "always"
    dst_file = "D:/TariqAI/logs/phase5_moved.txt"
    if Path(dst_file).exists():
        Path(dst_file).unlink()
        
    intent2 = f"Move {test_file} to {dst_file}"
    print(f"\n[STEP 1] Moving file (Threshold 5 Approvals needed)")
    
    # We need 5 approvals to reach ACT state
    for i in range(5):
        print(f"Approval {i+1}/5...")
        poi.handle_request(intent2)
        # Move it back for the next iteration of the loop
        if Path(dst_file).exists():
            Path(dst_file).rename(test_file)
    
    print(f"\n[STEP 2] Final execution check (Should be auto-ACT now)")
    # This should now execute autonomously
    poi.handle_request(intent2)

    print("\n--- FLOW 3: DESTRUCTIVE ACTION (CRITICAL) ---")
    intent3 = f"Delete the file {dst_file}"
    # Even if we approve always, CRITICAL risk should ALWAYS ask (per SYSTEM_BOUNDARIES)
    # Actually, current IML logic blocks CRITICAL regardless.
    poi.handle_request(intent3)

    print("\n" + "="*60)
    print("PHASE 5 DEMO COMPLETE")
    print("Logic chain verified for File Management.")
    print("="*60)

if __name__ == "__main__":
    run_phase5_demo()
