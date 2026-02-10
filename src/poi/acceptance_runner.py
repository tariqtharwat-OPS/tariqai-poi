import sys
import os
from pathlib import Path

# Setup Path
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.interface.models import UserDecision, DecisionType

class AcceptanceUI:
    def request_human_oversight(self, **kwargs):
        print(f"[ACCEPTANCE] Auto-approving: {kwargs.get('action')}")
        return UserDecision(request_id="acceptance_001", decision=DecisionType.APPROVE_ONCE)

def run_acceptance():
    print("="*80)
    print("🛡️  TARIQ AI POI - PHASE 7 ACCEPTANCE RUN")
    print("="*80)
    
    # Ensure Live Mode
    os.environ["DRY_RUN"] = "0"
    
    core = POICore()
    core.interface = AcceptanceUI()
    
    tasks = [
        "Visit https://example.com and save to D:/TariqAI/logs/acceptance_browser.txt",
        "Create a Word document at D:/TariqAI/logs/acceptance_word.docx",
        "Create an Excel spreadsheet at D:/TariqAI/logs/acceptance_excel.xlsx"
    ]
    
    for i, task in enumerate(tasks):
        print(f"\n[TASK {i+1}] {task}")
        core.handle_request(task)
        
    print("\n" + "="*80)
    print("ACCEPTANCE RUN COMPLETE")
    print("="*80)

if __name__ == "__main__":
    run_acceptance()
