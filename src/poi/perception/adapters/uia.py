import uiautomation as auto
from poi.perception.semantic_model import UIEntity
import logging

class UIAAdapter:
    def __init__(self):
        self.logger = logging.getLogger("UIA_Adapter")

    def capture_entities(self):
        """Extracts significant interactive elements from the foreground window."""
        entities = []
        try:
            window = auto.GetForegroundWindow()
            if not window: return []

            # We limit depth to avoid massive trees
            children = window.GetChildren()
            for child in children:
                # We prioritize Buttons, Edit fields (Inputs), and Menus
                c_type = child.ControlTypeName
                if c_type in ["ButtonControl", "EditControl", "MenuItemControl", "ListItemControl"]:
                    entities.append(UIEntity(
                        id=str(child.NativeWindowHandle),
                        label=child.Name or "Unnamed",
                        location={"rect": f"{child.BoundingRectangle.left},{child.BoundingRectangle.top}"},
                        purpose=c_type,
                        type=c_type.replace("Control", "").lower(),
                        confidence=1.0
                    ))
        except Exception as e:
            self.logger.error(f"UIA capture failed: {e}")
            
        return entities
