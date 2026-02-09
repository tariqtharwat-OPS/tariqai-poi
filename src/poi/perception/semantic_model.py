from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class UIEntity:
    """Represents a semantically understood element in the environment."""
    id: str
    type: str  # e.g., 'button', 'input', 'window', 'file'
    label: str
    purpose: str
    location: Dict[str, int]  # x, y, w, h
    confidence: float
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SemanticEnvironmentModel:
    """The structured output of the Perception Layer."""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "desktop"
    active_window: str = "unknown"
    entities: List[UIEntity] = field(default_factory=list)
    context_hints: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "active_window": self.active_window,
            "entities": [vars(e) for e in self.entities],
            "context_hints": self.context_hints
        }
