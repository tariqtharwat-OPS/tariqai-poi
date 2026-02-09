import sys
from pathlib import Path
import os

# Absolute path setup
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.interface.models import UserDecision, DecisionType

def run_docs_demo():
    print("="*80)
    print("🛡️  TARIQ AI POI - PHASE 7 DOCS DEMO (WORD & EXCEL)")
    print("="*80)
    
    os.environ["DRY_RUN"] = "0"
    poi = POICore()
    
    # Mock UI to auto-approve
    class DocsMockUI:
        def request_human_oversight(self, *args, **kwargs):
            action = kwargs.get('action')
            path = kwargs.get('params', {}).get('path')
            print(f"\n[SHIELD] Action: {action} -> {path}")
            print("[USER] Approving document generation...")
            return UserDecision(request_id="ph7_docs_demo", decision=DecisionType.APPROVE_ONCE)

    poi.interface = DocsMockUI()
    
    # Paths
    word_path = "D:/TariqAI/logs/ph7_word_demo.docx"
    excel_path = "D:/TariqAI/logs/ph7_excel_demo.xlsx"
    
    print("\n[STEP 1] GENERATING WORD DOCUMENT")
    poi.handle_request(f"Create a word document report at {word_path}")
    
    print("\n[STEP 2] GENERATING EXCEL SPREADSHEET")
    poi.handle_request(f"Create an excel spreadsheet table at {excel_path}")
    
    # Verification
    if Path(word_path).exists() and Path(excel_path).exists():
        print("\n[DEMO] Success: Documents created on disk.")
    else:
        print("\n[DEMO] Failure: Documents missing from disk.")

    print("\n" + "="*80)

if __name__ == "__main__":
    run_docs_demo()
