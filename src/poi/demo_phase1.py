from core import POICore
import json

def run_phase1_demo():
    print("="*50)
    print("TARIQ AI POI - PHASE 1 DEMO")
    print("="*50)
    
    poi = POICore()
    
    print("\n--- TEST 1: NO HISTORICAL TRUST (CONTEXT A) ---")
    print("Request: 'Create logs/test_a.txt'")
    # This should be BLOCKED (No history for test_a.txt)
    res_a = poi.st.process_intent("Create logs/test_a.txt")
    poi.handle_request("Create logs/test_a.txt")
    
    print("\n--- TEST 2: MANUAL PROMOTION (MANUAL_UPDATE_TRUST) ---")
    print("User explicitly approves Context A...")
    sig_a = res_a["context_signature"]
    for _ in range(5):
        poi.iml.update_trust("DATA_MODIFICATION", sig_a, success=True)
    
    print("\n--- TEST 3: CONTEXT SEPARATION (CONTEXT B) ---")
    print("Request: 'Create logs/test_b.txt'")
    # This should be BLOCKED (Historical trust is for A, not B)
    poi.handle_request("Create logs/test_b.txt")
    
    print("\n--- TEST 4: ACT EXECUTION (CONTEXT A) ---")
    print("Request: 'Create logs/test_a.txt' (Retry)")
    # This should now PASS
    poi.handle_request("Create logs/test_a.txt")
    
    print("\n--- TEST 5: DESTRUCTIVE RISK (ST CLASSIFIED) ---")
    print("Request: 'Wipe the database'")
    # Classified as CRITICAL by ST -> Blocked by IML regardless of trust
    poi.handle_request("Wipe the database")

    print("\n" + "="*50)
    print("DEMO COMPLETE")
    print("Check 'persistent_memory/poi/audit_trail.log' for full trace.")
    print("="*50)

if __name__ == "__main__":
    run_phase1_demo()
