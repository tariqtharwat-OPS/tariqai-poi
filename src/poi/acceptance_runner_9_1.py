import sys
import os
from pathlib import Path

# Setup Path
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.interface.models import UserDecision, DecisionType

class AcceptanceUI:
    def request_human_oversight(self, **kwargs):
        print(f"[ACCEPTANCE] Oversight triggered for: {kwargs.get('action')} (intent: {kwargs.get('intent_type')})")
        print(f"[ACCEPTANCE] Auto-approving...")
        return UserDecision(request_id="acceptance_9_1", decision=DecisionType.APPROVE_ONCE)

def run_acceptance():
    print("="*80)
    print("🛡️  TARIQ AI POI - PHASE 9.1 HOTFIX ACCEPTANCE")
    print("="*80)
    
    # Ensure Live Mode
    os.environ["DRY_RUN"] = "0"
    
    core = POICore()
    core.interface = AcceptanceUI()
    
    task = "Open https://example.com and save html to D:/TariqAI/logs/example_gui.html"
    print(f"\n[TASK] {task}")
    core.handle_request(task)
        
    print("\n" + "="*80)
    print("ACCEPTANCE RUN COMPLETE")
    print("="*80)

if __name__ == "__main__":
    run_acceptance()
