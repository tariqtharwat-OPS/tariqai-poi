import logging
import uuid
from typing import Optional
from poi.interface.models import ConfirmationRequest, UserDecision, DecisionType

class ConfirmationManager:
    """
    The human control plane for Tariq AI.
    Handles the presentation of requests and capture of user decisions.
    """
    def __init__(self, iml):
        self.iml = iml
        self.logger = logging.getLogger("ConfirmationManager")

    def request_human_oversight(self, intent_type: str, context_signature: str, risk_level: str, action: str, params: dict) -> UserDecision:
        """
        Presents a request to the user via CLI and returns the decision.
        """
        request_id = str(uuid.uuid4())[:8]
        consequence = self._generate_consequence_summary(action, params, risk_level)
        
        request = ConfirmationRequest(
            request_id=request_id,
            intent_type=intent_type,
            context_signature=context_signature,
            risk_level=risk_level,
            action=action,
            params=params,
            consequence_summary=consequence
        )

        self._display_request(request)
        decision_type = self._get_user_input()
        
        return UserDecision(request_id=request_id, decision=decision_type)

    def _generate_consequence_summary(self, action: str, params: dict, risk_level: str) -> str:
        if risk_level == "CRITICAL":
            path = params.get("path") or params.get("src")
            return f"CRITICAL: This will permanently DELETE or OVERWRITE: {path}"
        
        if action == "file_move":
            return f"Will MOVE '{params.get('src')}' to '{params.get('dst')}'"
        
        if action == "file_copy":
            return f"Will COPY '{params.get('src')}' to '{params.get('dst')}'"
            
        if action == "file_create":
            return f"Will CREATE a new file at: {params.get('path')}"

        if action == "press_button":
            return f"Will interact with UI element: {params.get('label', 'Unknown')}"
            
        if action == "file_op":
            return f"Will modify file at: {params.get('path')}"
            
        return "Standard system interaction."

    def _display_request(self, req: ConfirmationRequest):
        print("\n" + "!" * 60)
        print("🚨 TARIQ AI : CONFIRMATION REQUIRED")
        print("!" * 60)
        print(f"ID: {req.request_id}")
        print(f"INTENT: {req.intent_type}")
        print(f"CONTEXT: {req.context_signature}")
        print(f"RISK: {req.risk_level}")
        print(f"ACTION: {req.action}")
        print(f"CONSEQUENCE: {req.consequence_summary}")
        print("-" * 60)
        print("OPTIONS:")
        print(" [1] Approve Once")
        print(" [2] Approve ALWAYS for this context")
        print(" [3] Reject")
        print(" [4] Revoke prior trust for this context")
        print("-" * 60)

    def _get_user_input(self) -> DecisionType:
        # In a real GUI this would be a button click. 
        # For Phase 4 demo we will default to manual CLI input or simulation.
        choice = input("Select option [1-4]: ").strip()
        mapping = {
            "1": DecisionType.APPROVE_ONCE,
            "2": DecisionType.APPROVE_ALWAYS,
            "3": DecisionType.REJECT,
            "4": DecisionType.REVOKE
        }
        return mapping.get(choice, DecisionType.REJECT)
