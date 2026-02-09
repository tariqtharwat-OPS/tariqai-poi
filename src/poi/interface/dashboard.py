import json
from datetime import datetime
from pathlib import Path

class POIDashboard:
    """
    Minimal but real control interface for Tariq AI.
    Provides visibility into Audit History and Trust Registry.
    """
    def __init__(self, iml):
        self.iml = iml

    def show(self):
        print("\n" + "="*80)
        print("🛡️  TARIQ AI POI : CONTROL DASHBOARD")
        print("="*80)
        
        self._show_trust_summary()
        self._show_audit_history()
        
        print("\n" + "="*80)

    def _show_trust_summary(self):
        summary = self.iml.get_audit_summary()
        print("\n[CONTEXT TRUST REGISTRY]")
        
        if not summary["trusted_contexts_act"] and not summary["pending_contexts_ask"]:
            print("  (Empty - No context specific trust established)")
            return

        print(f"  ✅ TRUSTED (ACT): {len(summary['trusted_contexts_act'])}")
        for ctx in summary["trusted_contexts_act"]:
            print(f"    - {ctx}")
            
        print(f"  ⏳ PENDING (ASK): {len(summary['pending_contexts_ask'])}")
        for ctx in summary["pending_contexts_ask"]:
            state = self.iml.get_trust_state(ctx)
            print(f"    - {ctx} ({state['actions_confirmed']}/5 approvals)")

        if summary["revoked_contexts"]:
            print(f"  🚫 REVOKED: {len(summary['revoked_contexts'])}")
            for ctx in summary["revoked_contexts"]:
                print(f"    - {ctx}")

    def _show_audit_history(self):
        history = self.iml.get_full_audit_history()
        print("\n[AUDIT HISTORY (DECISIONS)]")
        
        decisions = history["decisions"][-10:] # Last 10
        if not decisions:
            print("  (No decision history yet)")
        else:
            for d in reversed(decisions):
                ts = datetime.fromisoformat(d["timestamp"]).strftime("%H:%M:%S")
                req_id = d["request_id"]
                decision = d["decision"]
                intent = d["context"].get("intent_type", "Unknown")
                sig = d["context"].get("context_signature", "Unknown")
                
                print(f"  {ts} | ID: {req_id} | {decision.upper():<15} | Intent: {intent:<15} | Context: {sig}")

    def interactive_revoke(self):
        print("\n[REVOKE ACCESS]")
        summary = self.iml.get_audit_summary()
        all_contexts = summary["trusted_contexts_act"] + summary["pending_contexts_ask"]
        
        if not all_contexts:
            print("No active trust contexts to revoke.")
            return

        for i, ctx in enumerate(all_contexts):
            print(f" [{i+1}] {ctx}")
            
        try:
            choice = input("\nSelect context ID to REVOKE (or 'q' to cancel): ").strip()
            if choice.lower() == 'q': return
            
            idx = int(choice) - 1
            if 0 <= idx < len(all_contexts):
                ctx_to_revoke = all_contexts[idx]
                # Split key back into intent and signature
                intent_type, sig = ctx_to_revoke.split("::")
                self.iml.revoke_trust(intent_type, sig)
                print(f"SUCCESS: Trust revoked for {ctx_to_revoke}")
            else:
                print("Invalid selection.")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    from poi.iml.layer import IdentityMemoryLayer
    iml = IdentityMemoryLayer()
    dashboard = POIDashboard(iml)
    
    while True:
        dashboard.show()
        print("\nCOMMANDS: [r] Revoke Context  [q] Quit")
        cmd = input("Choice: ").strip().lower()
        if cmd == 'r': dashboard.interactive_revoke()
        elif cmd == 'q': break
