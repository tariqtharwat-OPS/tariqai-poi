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
        Simulates the process of:
        Vision -> Semantic Understanding -> Actionable Entities.
        """
        self.logger.info("OBSERVE_DESKTOP | Performing semantic scan")
        
        # In a real implementation, this would call a Vision model or UI Inspector.
        # Here we produce a semantic map of a simulated 'Automation' task screen.
        
        model = SemanticEnvironmentModel(
            source="windows_desktop",
            active_window="Visual Studio Code - TariqAI",
            context_hints=["code_editor", "development_environment"]
        )

        # Semantically identified entities
        model.entities = [
            UIEntity(
                id="explorer_panel",
                type="panel",
                label="File Explorer",
                purpose="navigation",
                location={"x": 0, "y": 0, "w": 300, "h": 1000},
                confidence=0.98
            ),
            UIEntity(
                id="save_button",
                type="button",
                label="Save",
                purpose="persistence",
                location={"x": 500, "y": 10, "w": 40, "h": 20},
                confidence=0.95,
                properties={"shortcut": "Ctrl+S"}
            ),
            UIEntity(
                id="terminal_area",
                type="output",
                label="Integrated Terminal",
                purpose="execution_feedback",
                location={"x": 300, "y": 800, "w": 1600, "h": 200},
                confidence=0.99
            )
        ]

        return model
