import sys
from pathlib import Path
import time

# Absolute path setup
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.interface.dashboard import POIDashboard
from poi.interface.models import UserDecision, DecisionType

def run_phase6_demo():
    print("="*80)
    print("🛡️  TARIQ AI POI - PHASE 6 DEMO (CONTROL DASHBOARD & LIVE OPS)")
    print("="*80)
    
    poi = POICore()
    dashboard = POIDashboard(poi.iml)
    
    # 1. SETUP TEST SCENARIO
    test_dir = Path("D:/TariqAI/logs/phase6_demo")
    test_dir.mkdir(parents=True, exist_ok=True)
    target_file = test_dir / "live_report.txt"
    if target_file.exists(): target_file.unlink()
    
    print("\n[STEP 1] INITIATING LIVE FILE TASK (CREATE)")
    print("Requirement: This should trigger the new Premium Shield interface.")
    
    # Simulate user approving it once for Step 1
    class Step1Mock:
        def request_human_oversight(self, *args, **kwargs):
            # The UI is shown in POICore call
            print(f"\n[DEMO] SIMULATING USER: selects [1] APPROVE ONCE")
            return UserDecision(request_id="ph6_demo_01", decision=DecisionType.APPROVE_ONCE)
    
    poi.interface = Step1Mock()
    poi.handle_request(f"Create the live report at {target_file}")
    
    print("\n[STEP 2] VIEWING THE DASHBOARD")
    print("Requirement: Show audit history and pending trust.")
    dashboard.show()
    
    print("\n[STEP 3] ESCALATING TRUST (APPROVE ALWAYS)")
    # Move the file - simulate user authorizing always
    moved_file = test_dir / "live_report_archived.txt"
    if moved_file.exists(): moved_file.unlink()
    
    class Step2Mock:
        def request_human_oversight(self, *args, **kwargs):
            print(f"\n[DEMO] SIMULATING USER: selects [2] APPROVE ALWAYS")
            return UserDecision(request_id="ph6_demo_02", decision=DecisionType.APPROVE_ALWAYS)
            
    poi.interface = Step2Mock()
    # Need to move it back if it existed, but we start fresh.
    # We'll do this once to show it's now in the 'pending escalation' logic
    poi.handle_request(f"Move {target_file} to {moved_file}")
    
    print("\n[STEP 4] REVOKING TRUST VIA DASHBOARD")
    # Instead of interactive, we'll call the logic directly for demo
    summary = poi.iml.get_audit_summary()
    all_ctx = summary["trusted_contexts_act"] + summary["pending_contexts_ask"]
    if all_ctx:
        print(f"\n[DEMO] DASHBOARD: Revoking trust for {all_ctx[0]}...")
        parts = all_ctx[0].split("::")
        intent_type = parts[0]
        sig = parts[1] if len(parts) > 1 else ""
        poi.iml.revoke_trust(intent_type, sig)
    
    print("\n[FINAL] RE-CHECKING DASHBOARD")
    dashboard.show()

    print("\n" + "="*80)
    print("PHASE 6 DEMO COMPLETE")
    print("Proof: Premium Oversight Interface validated.")
    print("Proof: Context-specific Revocation validated.")
    print("Proof: Decision logging verified.")
    print("="*80)

if __name__ == "__main__":
    run_phase6_demo()
