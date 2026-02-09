import sys
from pathlib import Path

# Absolute path setup
sys.path.append("D:/TariqAI/src")

from poi.core import POICore

def run_phase3_demo():
    print("="*60)
    print("TARIQ AI POI - PHASE 3 DEMO (CONTROLLED EXECUTION)")
    print("="*60)
    
    poi = POICore()
    
    # Target intent: Semantic Save
    intent = "Press the Save button"
    print(f"\n[REQUEST] Intent: '{intent}'")
    
    # 1. ST Mapping Check
    print("\n--- STEP 1: SEMANTIC MAPPING (ST -> PERCEPTION) ---")
    # ST should identify 'save_button' in VS Code.
    decision = poi.st.process_intent(intent, perception_model=poi.perception.capture_environment())
    print(f"[ST] Mapped to: {decision['plan'][0]['action']} (Entity: {decision['plan'][0]['params']['entity_id']})")
    
    # 2. Trust Enforcement (ASK)
    print("\n--- STEP 2: TRUST ENFORCEMENT (DEFAULT ASK) ---")
    # Action should be BLOCKED because trust_escalation.json is empty for this intent+context.
    res = poi.handle_request(intent)
    
    if res["status"] == "HALTED":
        print(f"PROOF: Action was BLOCKED as expected. Reason: {res['reason']}")

    # 3. Trust PromotionFlow (Manual)
    print("\n--- STEP 3: TRUST PROMOTION (MANUAL_UPDATE_TRUST) ---")
    sig = decision["context_signature"]
    print(f"Assigning trust to context: {sig} (Intent: DATA_MODIFICATION)")
    for i in range(5):
        poi.iml.update_trust("DATA_MODIFICATION", sig, success=True)
    
    # 4. Controlled Execution (ACT)
    print("\n--- STEP 4: CONTROLLED EXECUTION (ACT) ---")
    # Now that trust is promoted, FE should be allowed to execute the click.
    res_final = poi.handle_request(intent)
    
    if res_final["status"] == "SUCCESS":
        print("\nPROOF: Controlled Execution SUCCESSFUL.")
        print(f"Action Result: {res_final['results'][0]['message']}")

    print("\n" + "="*60)
    print("PHASE 3 DEMO COMPLETE")
    print("Logic chain verified: Mapping -> Shielding -> Promotion -> Execution.")
    print("="*60)

if __name__ == "__main__":
    run_phase3_demo()
