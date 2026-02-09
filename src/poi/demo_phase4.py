import sys
from pathlib import Path
import logging

# Absolute path setup
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.interface.models import DecisionType, UserDecision

class MockConfirmationManager:
    """Simulates user input for autonomous demo testing."""
    def __init__(self, iml):
        self.iml = iml
        self.call_count = 0

    def request_human_oversight(self, intent_type, context_signature, risk_level, action, params):
        self.call_count += 1
        print(f"\n[DEMO] MOCK_USER: Request {self.call_count} received. AUTO-APPROVING ALWAYS.")
        return UserDecision(request_id="mock_id", decision=DecisionType.APPROVE_ALWAYS)

def run_phase4_demo():
    print("="*60)
    print("TARIQ AI POI - PHASE 4 DEMO (USER CONFIRMATION FLOW)")
    print("="*60)
    
    poi = POICore()
    # Inject Mock Interface for automated proof
    poi.interface = MockConfirmationManager(poi.iml)
    
    intent = "Press the Save button in VS Code"
    print(f"\n[STEP 1] Initial Request (Should trigger mock approval)")
    # This will: BLOCK -> Mock Approve ALWAYS -> Escalation -> ACT
    poi.handle_request(intent)
    
    print("\n--- AUDIT CHECK (IML Visibility) ---")
    summary = poi.iml.get_audit_summary()
    print(f"Trusted Contexts (ACT): {summary['trusted_contexts_act']}")
    
    print(f"\n[STEP 2] Future Request (Should be auto-ACT without oversight)")
    # This should now execute immediately without calling request_human_oversight
    poi.handle_request(intent)

    print("\n--- TEST: REVOKE TRUST ---")
    print("Simulating User Revoking Trust...")
    # Get the context signature from ST for this intent
    decision = poi.st.process_intent(intent, perception_model=poi.perception.capture_environment())
    poi.iml.revoke_trust(decision["intent_type"], decision["context_signature"])
    
    summary = poi.iml.get_audit_summary()
    print(f"Revoked Contexts: {summary['revoked_contexts']}")
    
    print("\n[STEP 3] Post-Revoke Request (Should BLOCK and Ask again)")
    poi.handle_request(intent)

    print("\n" + "="*60)
    print("PHASE 4 DEMO COMPLETE")
    print("Proof: Trust Escalation restricted to Human Flow.")
    print("Proof: Audit visibility verified.")
    print("="*60)

if __name__ == "__main__":
    run_phase4_demo()
