import logging
import sys
from pathlib import Path

# Add src to path for poi imports
sys.path.append(str(Path(__file__).parent.parent))

from poi.iml.layer import IdentityMemoryLayer
from poi.st.layer import StrategicThinker
from poi.fe.layer import FastExecutor
from poi.perception.layer import PerceptionLayer
from poi.perception.adapters.desktop import DesktopAdapter
from poi.interface.manager import ConfirmationManager
from poi.interface.models import DecisionType

class POICore:
    """
    Main Orchestrator for Phase 1.
    Coordinates ST, FE, and IML.
    """
    def __init__(self, status_callback=None):
        self._setup_logging()
        self.iml = IdentityMemoryLayer()
        self.st = StrategicThinker(self.iml)
        self.fe = FastExecutor(self.iml)
        self.status_callback = status_callback
        
        # Phase 10.2 Research Module
        from poi.research.howto import HowToResearch
        self.research = HowToResearch(self.fe)
        
        # Phase 2: Perception Layer
        self.perception = PerceptionLayer()
        self.perception.add_adapter(DesktopAdapter())
        
        # Phase 4: Interface Layer
        self.interface = ConfirmationManager(self.iml)
        
        logger.info("Tariq POI Core Initialized @ Phase 10.2")

    def _setup_logging(self):
        self.logger = logging.getLogger("POI_Core")
        # Ensure no duplicate handlers if re-initialized
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s | %(name)s | %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def handle_request(self, prompt):
        """
        Universal Flow: UNDERSTAND -> RESEARCH -> PLAN -> EXECUTE
        """
        if self.status_callback: self.status_callback("Analyzing request...")
        
        # 1. SENSE
        perception_model = self.perception.capture_environment()
        
        # 2. THINK (Decomposition & Routing)
        intent_type, decision = self.st.get_intent(prompt, perception_model=perception_model)
        
        # Handle Clarification
        if intent_type == "CLARIFY":
            question = decision.get("question")
            self.logger.info(f"CLARIFY | Asking: {question}")
            if self.status_callback: self.status_callback("Need more info...")
            # In a real UI this would wait for input. For now, we print it.
            return {"status": "CLARIFICATION_REQUIRED", "message": question}

        # 3. RESEARCH & EXECUTE
        results = []
        context = {
            "prompt": prompt,
            "intent_type": decision["intent_type"],
            "risk_level": decision["risk_level"],
            "context_signature": decision["context_signature"]
        }
        
        for i, step in enumerate(decision["plan"]):
            action = step.get("action")
            params = step.get("params", {})
            
            if self.status_callback: 
                self.status_callback(f"Step {i+1}/{len(decision['plan'])}: {action}...")
            
            # ORCHESTRATION: Special handling for Research
            if action == "research_howto":
                self.logger.info(f"CORE | Triggering research for: {params.get('query')}")
                res = self.research.research_task(params.get("query"))
                results.append(res)
                continue

            # EXECUTION ATTEMPT via Fast Executor
            res = self.fe.execute_step(step, context)
            
            # GOVERNANCE BLOCK -> Escalation
            if res["status"] == "BLOCKED":
                print(f"[SHIELD] Action blocked by IML. Requesting human oversight...")
                
                user_decision = self.interface.request_human_oversight(
                    intent_type=context["intent_type"],
                    context_signature=context["context_signature"],
                    risk_level=context["risk_level"],
                    action=step["action"],
                    params=step.get("params", {})
                )
                
                # LOG DECISION TO IML (Phase 6)
                self.iml.log_human_decision(user_decision.request_id, user_decision.decision, context)
                
                if user_decision.decision in [DecisionType.APPROVE_ONCE, DecisionType.APPROVE_ALWAYS]:
                    print(f"[USER] Action approved ({user_decision.decision.value}). Re-executing...")
                    
                    if user_decision.decision == DecisionType.APPROVE_ALWAYS:
                        # Escalation AUTHORITY: Update trust registry
                        self.iml.update_trust(context["intent_type"], context["context_signature"], success=True)
                    
                    # Force re-execution by bypassing IML check this once? 
                    # No, FE must always check. In Phase 4 we mock the IML approval for 'once' 
                    # by passing a temporary bypass token or just letting the user-approve update trust.
                    # For safety, let's just retry the step if approved.
                    res = self.fe.execute_step(step, context={**context, "bypass_governance": True})
                elif user_decision.decision == DecisionType.REVOKE:
                    self.iml.revoke_trust(context["intent_type"], context["context_signature"])
                    return {"status": "REVOKED", "reason": "User revoked trust"}
                else:
                    print(f"[USER] Action rejected.")
                    return {"status": "HALTED", "reason": "User rejected action", "steps": results}

            results.append(res)
            
            if res["status"] == "FAILURE":
                print(f"[RECOVER] Step failed. Consulting ST...")
                diagnostic = self.st.evaluate_failure(res)
                return {"status": "FAILED", "diagnostic": diagnostic}

        # 3. COMMIT TO MEMORY
        success = all(r["status"] == "SUCCESS" for r in results)
        
        # Auto-update trust only for LOW risk intents that were already validated
        # and didn't require human override.
        if context["risk_level"] == "LOW" and not context.get("bypass_governance"):
            # Internal logic can only suggest, but for simplicity in demo:
            pass
        
        self.iml.record_outcome(decision["intent_id"], {"status": "COMPLETED", "results": results})
        
        print(f"[IML] Outcome recorded for {decision['intent_type']}.")
        return {"status": "SUCCESS", "results": results}

# Global instance
logger = logging.getLogger("POI_Global")
if __name__ == "__main__":
    core = POICore()
    print("="*80)
    print("🛡️  TARIQ AI POI - INTERACTIVE ASSISTANT")
    print("="*80)
    print("Type 'exit' to quit.")
    
    while True:
        try:
            prompt = input("\n[USER] > ").strip()
            if prompt.lower() in ["exit", "quit"]:
                break
            if not prompt:
                continue
                
            core.handle_request(prompt)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nShutting down Tariq AI POI...")
