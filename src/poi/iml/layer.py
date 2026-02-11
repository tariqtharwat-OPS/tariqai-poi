import json
import os
import logging
from datetime import datetime
from pathlib import Path

class IdentityMemoryLayer:
    """
    Governor of Tariq AI. Core responsibilities:
    1. Validation of all intents and actions against Constitution.
    2. Maintaining Trust Escalation counts.
    3. Persistent Audit Logging.
    """
    def __init__(self, base_path="persistent_memory/poi"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.base_path / "action_memory.json"
        self.trust_registry = self.base_path / "trust_escalation.json"
        self.audit_log = self.base_path / "audit_trail.log"
        self.decision_history_file = self.base_path / "decision_history.json"
        
        self._init_files()
        self._setup_logging()

    def _init_files(self):
        if not self.memory_file.exists():
            self.memory_file.write_text(json.dumps([]))
        if not self.trust_registry.exists():
            self.trust_registry.write_text(json.dumps({}))
        if not self.decision_history_file.exists():
            self.decision_history_file.write_text(json.dumps([]))

    def _setup_logging(self):
        self.logger = logging.getLogger("IML_Audit")
        self.logger.setLevel(logging.INFO)
        
        # Ensure file handler exists and is linked to audit_trail.log
        if not any(isinstance(h, logging.FileHandler) for h in self.logger.handlers):
            handler = logging.FileHandler(self.audit_log)
            formatter = logging.Formatter('%(asctime)s | POI_AUDIT | %(levelname)s | %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.info("IML_LOGGING_INITIALIZED")

    def log_intent(self, intent_id, intent_data):
        self.logger.info(f"INTENT_RECEIVED | {intent_id} | {json.dumps(intent_data)}")

    def validate_action(self, intent_type, context_signature, risk_level, action=None, params=None):
        """
        Consults the Constitution and past failures.
        IML CONSUMES risk_level from Strategic Thinker.
        """
        # SAFE ZONE RULE (Phase 9.2)
        # Allows for rapid iteration in non-critical log directories
        if action == "file_write":
            path = str(params.get("path", ""))
            if path.replace("\\", "/").startswith("D:/TariqAI/logs/tmp/"):
                self.logger.info(f"SAFE_ZONE_PASS | {action} to {path}")
                return True, "Safe zone auto-approval", "ACT"

        if action in ["chat", "log"]:
            return True, "Informational action auto-approval", "ACT"

        # BOUNDARY CHECK: Desktop Safety (Phase 11)
        if action and "desktop_" in action:
            # Block destructive UI labels
            p_lower = str(params or {}).lower()
            if any(w in p_lower for w in ["delete", "remove", "wipe", "format", "login", "signin", "send"]):
                 self.logger.warning(f"DESKTOP_SAFETY_BLOCK | Destructive label in: {action}")
                 return False, f"Destructive desktop action '{action}' blocked for safety.", "BLOCK"

        # Gmail Safety Example
        if intent_type == "GMAIL_DELETE" and action not in ["chat", "log"]:
             self.logger.warning(f"CONSTITUTION_BLOCK | Gmail deletion blocked by policy.")
             return False, "Deletion in Gmail is blocked. Suggested: Use Safe Assist for filters.", "BLOCK"

        # BOUNDARY CHECK: Critical risk always defaults to ASK
        if risk_level == "CRITICAL":
            self.logger.warning(f"CRITICAL_RISK_BLOCK | Intent: {intent_type}")
            return False, "Critical risk level requires human oversight", "ASK"
        
        # Check trust level keyed by intent + context signature
        trust_key = f"{intent_type}::{context_signature}"
        trust_state = self.get_trust_state(trust_key)
        
        if trust_state["actions_confirmed"] < 5:
            self.logger.info(f"TRUST_INSUFFICIENT | {trust_key} | {trust_state['actions_confirmed']}/5")
            return False, f"Insufficient trust history for this specific context ({trust_state['actions_confirmed']}/5)", "ASK"
        
        return True, "Validated for autonomous execution", "ACT"

    def get_trust_state(self, trust_key):
        with open(self.trust_registry, 'r') as f:
            trust = json.load(f)
        return trust.get(trust_key, {"actions_confirmed": 0, "state": "ASK"})

    def update_trust(self, intent_type, context_signature, success=True):
        """
        AUTHORITY NOTICE: This must only be called via the User Confirmation Flow.
        Keys trust by (intent_type + context_signature).
        """
        trust_key = f"{intent_type}::{context_signature}"
        
        with open(self.trust_registry, 'r') as f:
            trust = json.load(f)
        
        state = trust.get(trust_key, {"actions_confirmed": 0, "state": "ASK"})
        if success:
            state["actions_confirmed"] += 1
            if state["actions_confirmed"] >= 5:
                state["state"] = "ACT" 
        else:
            # Immediate demotion on any failure or user rejection
            state["actions_confirmed"] = 0
            state["state"] = "ASK" 
            
        trust[trust_key] = state
        with open(self.trust_registry, 'w') as f:
            json.dump(trust, f, indent=4)
        
        self.logger.info(f"TRUST_UPDATED | {trust_key} | New State: {state}")

    def revoke_trust(self, intent_type, context_signature):
        """Explicitly revokes all trust for a context."""
        trust_key = f"{intent_type}::{context_signature}"
        with open(self.trust_registry, 'r') as f:
            trust = json.load(f)
        
        trust[trust_key] = {"actions_confirmed": 0, "state": "ASK", "revoked": True}
        
        with open(self.trust_registry, 'w') as f:
            json.dump(trust, f, indent=4)
        self.logger.warning(f"TRUST_REVOKED | {trust_key}")

    def get_audit_summary(self):
        """Returns summary of trusted contexts for audit visibility."""
        with open(self.trust_registry, 'r') as f:
            trust = json.load(f)
        
        return {
            "trusted_contexts_act": [k for k, v in trust.items() if v["state"] == "ACT"],
            "pending_contexts_ask": [k for k, v in trust.items() if v["state"] == "ASK" and v.get("actions_confirmed", 0) > 0],
            "revoked_contexts": [k for k, v in trust.items() if v.get("revoked")]
        }

    def log_human_decision(self, request_id, decision_type, context):
        """Records a human decision in the audit trail."""
        with open(self.decision_history_file, 'r') as f:
            history = json.load(f)
        
        # Ensure decision is serializable (handle Enum)
        decision_val = decision_type.value if hasattr(decision_type, 'value') else str(decision_type)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "decision": decision_val,
            "context": context
        }
        history.append(entry)
        
        with open(self.decision_history_file, 'w') as f:
            json.dump(history, f, indent=4)
        
        self.logger.info(f"HUMAN_DECISION | {request_id} | {decision_val} | Context: {context.get('context_signature')}")

    def get_full_audit_history(self):
        """Returns the full list of intents and decisions."""
        with open(self.memory_file, 'r') as f:
            intents = json.load(f)
        with open(self.decision_history_file, 'r') as f:
            decisions = json.load(f)
        
        return {
            "intents": intents,
            "decisions": decisions
        }

    def record_outcome(self, action_id, result):
        with open(self.memory_file, 'r') as f:
            memory = json.load(f)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_id": action_id,
            "result": result
        }
        memory.append(entry)
        
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=4)
        
        self.logger.info(f"ACTION_COMPLETED | {action_id} | Status: {result['status']}")
