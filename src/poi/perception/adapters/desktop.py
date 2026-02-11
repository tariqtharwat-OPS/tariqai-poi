import logging
import sys
from pathlib import Path

# Fix path to allow absolute-style imports if needed
sys.path.append("D:/TariqAI/src")

from poi.perception.semantic_model import SemanticEnvironmentModel, UIEntity
from poi.perception.layer import PerceptionAdapter

class DesktopAdapter(PerceptionAdapter):
    """
    Read-only desktop perception adapter.
    Translates raw screen state (simulated/OCR/Vision) into semantic entities.
    """
    def __init__(self):
        self.logger = logging.getLogger("DesktopAdapter")

    def observe(self) -> SemanticEnvironmentModel:
        """
        Polls UIA for real desktop entities and merges with baseline model.
        """
        self.logger.info("OBSERVE_DESKTOP | Performing UIA scan")
        
        from poi.perception.adapters.uia import UIAAdapter
        uia = UIAAdapter()
        real_entities = uia.capture_entities()

        model = SemanticEnvironmentModel(
            source="windows_uia",
            active_window="System Foreground", # Simplification
            context_hints=["desktop_automation"]
        )

        # Merging real entities into model
        model.entities.extend(real_entities)
        
        # Keep fallback only if empty
        if not model.entities:
            model.entities.append(UIEntity(
                id="fallback_btn", type="button", label="Fallback", purpose="demo", location={"x":0,"y":0}, confidence=0.5
            ))

        return model
