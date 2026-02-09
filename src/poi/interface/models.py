from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional

class DecisionType(Enum):
    APPROVE_ONCE = "approve_once"
    APPROVE_ALWAYS = "approve_always"
    REJECT = "reject"
    REVOKE = "revoke"

@dataclass
class ConfirmationRequest:
    """The formal request for human oversight."""
    request_id: str
    intent_type: str
    context_signature: str
    risk_level: str
    action: str
    params: Dict[str, Any]
    consequence_summary: str

@dataclass
class UserDecision:
    """The result of human deliberation."""
    request_id: str
    decision: DecisionType
    reason: Optional[str] = None
