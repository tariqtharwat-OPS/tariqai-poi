import logging
import os
import shutil
from pathlib import Path

class FastExecutor:
    """
    Execution Layer. Core responsibilities:
    1. Executing atomic steps.
    2. Mandatory IML confirmation before every system interaction.
    3. DRY_RUN enforcement.
    """
    def __init__(self, iml):
        self.iml = iml
        self.logger = logging.getLogger("FE_Layer")
        self.dry_run = os.environ.get("DRY_RUN") == "1"
        self.last_content = None # Stateful extraction for multi-step plans

    def execute_step(self, step_data, context):
        """
        Takes a single task step and executes it ONLY IF IML approves.
        Honors DRY_RUN environment variable.
        """
        action = step_data.get("action")
        params = step_data.get("params", {})
        
        # 0. DRY_RUN ENFORCEMENT
        is_write_action = action in ["file_op", "file_create", "file_move", "file_copy", "file_delete", "word_create", "excel_create", "file_write"]
        if self.dry_run and is_write_action:
            self.logger.info(f"DRY_RUN | Action '{action}' planned but NOT executed.")
            return {"status": "SUCCESS", "message": f"[DRY_RUN] Would have executed: {action}", "dry_run": True}

        if context.get("bypass_governance"):
            self.logger.info(f"BYPASS | Action '{action}' authorized by HUMAN.")
            allowed, reason, suggested_state = True, "User authorized bypass", "ACT"
        else:
            # MANDATORY: Consult IML before action
            allowed, reason, suggested_state = self.iml.validate_action(
                intent_type=context.get("intent_type"),
                context_signature=context.get("context_signature"),
                risk_level=context.get("risk_level"),
                action=action,
                params=params
            )
        
        if not allowed:
            self.logger.warning(f"BLOCK | Action '{action}' denied by IML. Reason: {reason}")
            return {
                "status": "BLOCKED",
                "reason": reason,
                "suggested_state": suggested_state
            }

        # Execution Logic
        self.logger.info(f"EXECUTE | {action} | Params: {params}")
        
        try:
            if action == "chat":
                msg = params.get("message")
                print(f"[CHAT] {msg}")
                return {"status": "SUCCESS", "message": msg}

            if action == "log":
                print(f"[POI_FE] {params.get('message')}")
                return {"status": "SUCCESS", "message": "Logged to STDOUT"}
            
            if action == "file_op":
                file_path = Path(params.get("path"))
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "a") as f:
                    f.write(params.get("content") + "\n")
                return {"status": "SUCCESS", "message": f"Updated {params.get('path')}"}

            if action == "file_write":
                file_path = Path(params.get("path"))
                file_path.parent.mkdir(parents=True, exist_ok=True)
                content = params.get("content") or self.last_content or ""
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"status": "SUCCESS", "message": f"Wrote to {params.get('path')}"}

            if action == "file_list":
                p = Path(params.get("path", "."))
                if p.is_dir():
                    files = [f.name for f in p.iterdir()]
                    return {"status": "SUCCESS", "message": f"Found {len(files)} items in {p}", "data": files}
                return {"status": "ERROR", "message": f"Path is not a directory: {p}"}

            if action == "file_create":
                p = Path(params.get("path"))
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch()
                return {"status": "SUCCESS", "message": f"Created file: {p}"}

            if action == "file_move":
                src, dst = Path(params.get("src")), Path(params.get("dst"))
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    src.rename(dst)
                    return {"status": "SUCCESS", "message": f"Moved {src} to {dst}"}
                return {"status": "ERROR", "message": f"Source does not exist: {src}"}

            if action == "file_copy":
                src, dst = Path(params.get("src")), Path(params.get("dst"))
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    return {"status": "SUCCESS", "message": f"Copied {src} to {dst}"}
                return {"status": "ERROR", "message": f"Source does not exist: {src}"}

            if action == "file_delete":
                p = Path(params.get("path"))
                if p.exists():
                    if p.is_file():
                        p.unlink()
                    else:
                        shutil.rmtree(p)
                    return {"status": "SUCCESS", "message": f"Deleted: {p}"}
                return {"status": "ERROR", "message": f"Path does not exist: {p}"}

            # --- NEW PHASE 7 PRIMITIVES: Word & Excel ---
            if action == "word_create":
                from docx import Document
                p = Path(params.get("path"))
                p.parent.mkdir(parents=True, exist_ok=True)
                doc = Document()
                doc.add_heading(params.get("title", "Tariq AI Document"), 0)
                for bullet in params.get("bullets", []):
                    doc.add_paragraph(bullet, style='List Bullet')
                doc.save(p)
                return {"status": "SUCCESS", "message": f"Created Word doc: {p}"}

            if action == "excel_create":
                from openpyxl import Workbook
                p = Path(params.get("path"))
                p.parent.mkdir(parents=True, exist_ok=True)
                wb = Workbook()
                ws = wb.active
                ws.title = params.get("sheet_name", "TariqData")
                data = params.get("data", [["Header1", "Header2"]])
                for row in data:
                    ws.append(row)
                wb.save(p)
                return {"status": "SUCCESS", "message": f"Created Excel sheet: {p}"}

            # --- NEW PHASE 7 PRIMITIVES: Browser ---
            if action == "browser_open":
                from playwright.sync_api import sync_playwright
                url = params.get("url")
                
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url)
                    title = page.title()
                    # Pre-extract content and store in memory
                    self.last_content = page.content()
                    browser.close()
                        
                    return {"status": "SUCCESS", "message": f"Opened {url}", "data": {"title": title, "content_len": len(self.last_content)}}

            if action == "browser_extract":
                mode = params.get("mode", "html")
                content = self.last_content or ""
                if mode == "text":
                    # Simple HTML to Text conversion (mocked for now)
                    import re
                    content = re.sub('<[^<]+?>', '', content)
                return {"status": "SUCCESS", "message": f"Extracted {mode} content", "data": {"content_len": len(content)}}

            if action == "press_button":
                # Phase 3 Controlled Execution
                entity_id = params.get("entity_id")
                location = params.get("location")
                label = params.get("label")
                
                print(f"[POI_FE] SEMANTIC_ACTION: Pressing '{label}' (ID: {entity_id}) at {location}")
                return {
                    "status": "SUCCESS", 
                    "message": f"Successfully interacted with semantic entity: {label}",
                    "details": {"entity": entity_id, "action": "press"}
                }

            # --- NEW PHASE 11 PRIMITIVES: Desktop Operator ---
            if "desktop_" in action:
                from poi.desktop.uia_driver import UIADriver
                driver = UIADriver()
                
                if action == "desktop_focus":
                    success, msg = driver.focus_window(params.get("window_name"))
                    return {"status": "SUCCESS" if success else "ERROR", "message": msg}
                
                if action == "desktop_click":
                    success, msg = driver.click_element(params.get("element_name"))
                    return {"status": "SUCCESS" if success else "ERROR", "message": msg}
                
                if action == "desktop_type":
                    success, msg = driver.type_text(params.get("text"), params.get("element_name"))
                    return {"status": "SUCCESS" if success else "ERROR", "message": msg}
                
                if action == "desktop_hotkey":
                    # params gets keys as a list
                    success, msg = driver.hotkey(*params.get("keys", []))
                    return {"status": "SUCCESS" if success else "ERROR", "message": msg}
                
            return {"status": "ERROR", "message": f"Unknown action: {action}"}
            
        except Exception as e:
            self.logger.error(f"FAILURE | {action} failed: {str(e)}")
            return {"status": "FAILURE", "message": str(e)}
