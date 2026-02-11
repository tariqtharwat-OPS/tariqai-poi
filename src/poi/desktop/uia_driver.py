import uiautomation as auto
import logging
import time

class UIADriver:
    def __init__(self):
        self.logger = logging.getLogger("UIA_Driver")
        auto.SetGlobalSearchTimeout(5)  # Default timeout

    def list_windows(self):
        """Returns a list of visible top-level windows."""
        windows = auto.GetRootControl().GetChildren()
        results = []
        for win in windows:
            if win.Name:
                results.append({
                    "name": win.Name,
                    "handle": win.NativeWindowHandle,
                    "class": win.ClassName
                })
        return results

    def focus_window(self, name_contains):
        """Brings a window to the foreground."""
        win = auto.WindowControl(searchDepth=1, Name=name_contains)
        if win.Exists(0):
            win.SetFocus()
            win.ShowWindow(auto.ShowWindowMode.SW_SHOW)
            return True, f"Focused window: {win.Name}"
        return False, f"Window '{name_contains}' not found."

    def find_element(self, name=None, control_type=None, parent=None):
        """Finds an element by name or control type."""
        root = parent if parent else auto.GetRootControl()
        kwargs = {}
        if name: kwargs["Name"] = name
        if control_type: kwargs["ControlType"] = control_type
        
        element = root.Control(**kwargs)
        if element.Exists(0):
            return element
        return None

    def click_element(self, element_name, parent_window=None):
        """Clicks an element by name."""
        root = parent_window if parent_window else auto.GetRootControl()
        element = root.Control(Name=element_name)
        if element.Exists(2):
            element.Click()
            return True, f"Clicked {element_name}"
        return False, f"Element {element_name} not found."

    def type_text(self, text, element_name=None):
        """Types text into an element or current focus."""
        if element_name:
            element = auto.Control(Name=element_name)
            if element.Exists(2):
                element.SetFocus()
                element.SendKeys(text)
                return True, f"Typed into {element_name}"
            return False, f"Element {element_name} not found"
        else:
            auto.SendKeys(text)
            return True, "Typed at current focus"

    def hotkey(self, *keys):
        """Sends a hotkey combo, e.g. 'ctrl', 's'."""
        key_str = ""
        for k in keys:
            if k.lower() == "ctrl": key_str += "{Ctrl}"
            elif k.lower() == "shift": key_str += "{Shift}"
            elif k.lower() == "alt": key_str += "{Alt}"
            else: key_str += k
        auto.SendKeys(key_str)
        return True, f"Sent hotkey: {key_str}"
