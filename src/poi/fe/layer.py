import logging
from pathlib import Path

class FastExecutor:
    """
    Execution Layer. Core responsibilities:
    1. Executing atomic steps.
    2. Mandatory IML confirmation before every system interaction.
    """
    def __init__(self, iml):
        self.iml = iml
        self.logger = logging.getLogger("FE_Layer")

    def execute_step(self, step_data, context):
        """
        Takes a single task step and executes it ONLY IF IML approves.
        """
        action = step_data.get("action")
        params = step_data.get("params", {})
        
        if context.get("bypass_governance"):
            self.logger.info(f"BYPASS | Action '{action}' authorized by HUMAN.")
            allowed, reason, suggested_state = True, "User authorized bypass", "ACT"
        else:
            # MANDATORY: Consult IML before action
            allowed, reason, suggested_state = self.iml.validate_action(
                intent_type=context.get("intent_type"),
                context_signature=context.get("context_signature"),
                risk_level=context.get("risk_level")
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
            if action == "log":
                print(f"[POI_FE] {params.get('message')}")
                return {"status": "SUCCESS", "message": "Logged to STDOUT"}
            
            if action == "file_op":
                file_path = Path(params.get("path"))
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "a") as f:
                    f.write(params.get("content") + "\n")
                return {"status": "SUCCESS", "message": f"Updated {params.get('path')}"}

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
                import shutil
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
                        import shutil
                        shutil.rmtree(p)
                    return {"status": "SUCCESS", "message": f"Deleted: {p}"}
                return {"status": "ERROR", "message": f"Path does not exist: {p}"}

            if action == "press_button":
                # Phase 3 Controlled Execution
                entity_id = params.get("entity_id")
                location = params.get("location")
                label = params.get("label")
                
                # In real scenario, this calls robotic/UI automation driver (browser/AHK)
                # Here we perform a SAFE simulation for Phase 3.
                print(f"[POI_FE] SEMANTIC_ACTION: Pressing '{label}' (ID: {entity_id}) at {location}")
                return {
                    "status": "SUCCESS", 
                    "message": f"Successfully interacted with semantic entity: {label}",
                    "details": {"entity": entity_id, "action": "press"}
                }
                
            return {"status": "ERROR", "message": f"Unknown action: {action}"}
            
        except Exception as e:
            self.logger.error(f"FAILURE | {action} failed: {str(e)}")
            return {"status": "FAILURE", "message": str(e)}
