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
        print("\n" + "╔" + "═" * 78 + "╗")
        print(f"║ 🛡️  TARIQ AI : HUMAN OVERSIGHT REQUIRED {' ' * (37 - len(req.request_id))} {req.request_id} ║")
        print("╠" + "═" * 78 + "╣")
        print(f"║  INTENT      : {req.intent_type:<63} ║")
        print(f"║  CONTEXT SIG : {req.context_signature:<63} ║")
        print(f"║  RISK LEVEL  : {req.risk_level:<63} ║")
        print(f"║  TARGET      : {req.action:<63} ║")
        print("╟" + "─" * 78 + "╢")
        print(f"║  CONSEQUENCE SUMMARY:                                                       ║")
        summary_lines = self._wrap_text(req.consequence_summary, 74)
        for line in summary_lines:
            print(f"║  {line:<76} ║")
        print("╚" + "═" * 78 + "╝")
        print("\nDECISION OPTIONS:")
        print(" [1] APPROVE ONCE   - Proceed with this single operation.")
        print(" [2] APPROVE ALWAYS - Authorize this specific context for future ACT status.")
        print(" [3] REJECT         - Halt all operations for this intent.")
        print(" [4] REVOKE TRUST   - Demote this context immediately to ASK state.")
        print("-" * 80)

    def _wrap_text(self, text, width):
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        if current_line:
            lines.append(" ".join(current_line))
        return lines

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
