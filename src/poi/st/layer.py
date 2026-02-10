import uuid
import logging

class StrategicThinker:
    """
    Intelligence and Decision layer. Core responsibilities:
    1. Intent Decomposition.
    2. Risk Assessment.
    3. Failure Diagnostics.
    """
    def __init__(self, iml):
        self.iml = iml
        self.logger = logging.getLogger("ST_Layer")

    def process_intent(self, prompt, perception_model=None):
        """
        Main entry point for ST.
        Consumes Perception data to contextualize the intent.
        """
        intent_id = str(uuid.uuid4())[:8]
        self.logger.info(f"THINKING | {intent_id} | Analyzing: {prompt}")
        
        # Integration of Perception Data
        if perception_model:
            self.logger.info(f"CONTEXT_AWARE | Active Window: {perception_model.active_window}")
            # Dynamic risk assessment based on what we actually 'see'
            # e.g. If we see a production bank page, risk goes up.
        
        # In Phase 1, we use simple heuristics for routing
        intent_type = self._classify_intent(prompt)
        risk_level = self._assess_risk(prompt)
        context_signature = self._generate_context_signature(prompt, intent_type)
        
        decision = {
            "intent_id": intent_id,
            "intent_type": intent_type,
            "risk_level": risk_level,
            "context_signature": context_signature,
            "plan": self._generate_plan(prompt, intent_type, perception_model=perception_model)
        }
        
        self.iml.log_intent(intent_id, decision)
        return decision

    def _generate_context_signature(self, prompt, intent_type):
        """
        Creates a signature based on intent and target targets.
        Prevents generalized trust across different files/environments.
        """
        import hashlib
        # Extract potential targets (very simple for Phase 1)
        # In future this will use semantic entities from Perception
        words = prompt.split()
        target = "system"
        for i, word in enumerate(words):
            if "." in word or "/" in word or "\\" in word:
                target = word
                break
        
        sig_base = f"{intent_type}|{target}"
        return hashlib.sha256(sig_base.encode()).hexdigest()[:12]

    def _classify_intent(self, prompt):
        p = prompt.lower()
        if any(w in p for w in ["browser", "search", "open page", "visit", "website"]):
            return "BROWSER"
        if any(w in p for w in ["excel", "xlsx", "spreadsheet", "table"]):
            return "DOCUMENT_EXCEL"
        if any(w in p for w in ["word", "docx", "document", "report"]):
            return "DOCUMENT_WORD"
            
        if any(w in p for w in ["list", "look inside", "show files", "find", "locate"]):
            return "FILE_NAVIGATION"
        if any(w in p for w in ["rename", "move", "copy", "create", "make folder", "setup"]):
            return "FILE_OPERATION"
        if any(w in p for w in ["delete", "remove", "wipe", "overwrite", "erase"]):
            return "FILE_DESTRUCTION"
        
        # Legacy fallbacks
        if any(w in p for w in ["check", "tell", "status", "show"]):
            return "READ_ONLY_STATUS"
        return "GENERAL_QUERY"

    def _assess_risk(self, prompt):
        p = prompt.lower()
        # Destructive actions are always CRITICAL
        if any(w in p for w in ["delete", "remove", "wipe", "overwrite", "erase"]):
            return "CRITICAL"
        
        # Browser and new document creation are MEDIUM
        if any(w in p for w in ["browser", "excel", "xlsx", "word", "docx"]):
            return "MEDIUM"

        # Modification of existing files/folders
        if any(w in p for w in ["rename", "move", "copy"]):
            return "MEDIUM"
        
        # Creation is lower risk but still DATA_MODIFICATION context
        if any(w in p for w in ["create", "make", "setup"]):
            return "MEDIUM"
            
        return "LOW"

    def _generate_plan(self, prompt, intent_type, perception_model=None):
        """
        Phase 7: Intent -> FE Action mapping for Browser/Docs.
        """
        p = prompt.lower()
        
        if intent_type == "BROWSER":
            url = self._extract_url(prompt) or "https://www.google.com"
            params = {"url": url, "extract_content": True}
            if "save" in p or "to" in p:
                path = self._extract_path(prompt, skip_urls=True)
                if path:
                    params["save_path"] = path
            return [{"action": "browser_open", "params": params}]

        if intent_type == "DOCUMENT_WORD":
            path = self._extract_path(prompt) or "D:/TariqAI/logs/new_report.docx"
            return [{"action": "word_create", "params": {
                "path": path, 
                "title": "Tariq AI Automated Report",
                "bullets": self._extract_bullets(prompt) or ["Automatic analysis start"]
            }}]

        if intent_type == "DOCUMENT_EXCEL":
            path = self._extract_path(prompt) or "D:/TariqAI/logs/data_sheet.xlsx"
            return [{"action": "excel_create", "params": {
                "path": path,
                "sheet_name": "TariqData",
                "data": [["Timestamp", "Event"], ["2026-02-10", "Phase 7 Initialization"]]
            }}]

        if perception_model and ("click" in p or "press" in p or "save" in p):
            # Attempt to find a matching entity semantically
            for entity in perception_model.entities:
                # Semantic match: Label or Purpose
                if entity.label.lower() in p or entity.purpose.lower() in p:
                    self.logger.info(f"SEMANTIC_MAP_FOUND | Intent: '{prompt}' -> Entity: {entity.id}")
                    return [{
                        "action": "press_button",
                        "params": {
                            "entity_id": entity.id,
                            "label": entity.label,
                            "location": entity.location
                        }
                    }]

        # 2. Fallbacks (Legacy Phase 1 logic)
        if intent_type == "FILE_NAVIGATION":
            target_path = self._extract_path(prompt) or "."
            return [{"action": "file_list", "params": {"path": target_path}}]

        if intent_type == "FILE_OPERATION":
            # Very simple path extraction for Phase 5 demo
            paths = self._extract_paths(prompt)
            if "create" in p or "make" in p:
                return [{"action": "file_create", "params": {"path": paths[0] if paths else "new_file.txt"}}]
            if "move" in p or "rename" in p:
                if len(paths) >= 2:
                    return [{"action": "file_move", "params": {"src": paths[0], "dst": paths[1]}}]
            if "copy" in p:
                if len(paths) >= 2:
                    return [{"action": "file_copy", "params": {"src": paths[0], "dst": paths[1]}}]
            
        if intent_type == "FILE_DESTRUCTION":
            target_path = self._extract_path(prompt)
            if target_path:
                return [{"action": "file_delete", "params": {"path": target_path}}]

        # 2. Fallbacks (Legacy Phase 1-3 logic)
        if intent_type == "READ_ONLY_STATUS":
            return [{"action": "log", "params": {"message": f"POI Audit: Check status of {prompt}"}}]
        
        return [{"action": "chat", "params": {"message": f"I understand your request for {prompt}. How should I proceed?"}}]

    def _extract_url(self, prompt):
        import re
        urls = re.findall(r'https?://[^\s]+', prompt)
        return urls[0] if urls else None

    def _extract_bullets(self, prompt):
        # Extremely simplified for demo
        return ["Data point extracted from prompt"]

    def _extract_path(self, prompt, skip_urls=False):
        """Simple path extractor for Phase 5."""
        words = prompt.split()
        for word in words:
            clean_word = word.strip("'\"")
            if skip_urls and (clean_word.startswith("http://") or clean_word.startswith("https://")):
                continue
            if "." in clean_word or "/" in clean_word or "\\" in clean_word or clean_word.startswith("logs"):
                return clean_word
        return None

    def _extract_paths(self, prompt):
        """Extracts multiple paths (e.g. for move/copy)."""
        words = prompt.split()
        paths = []
        for word in words:
            if "." in word or "/" in word or "\\" in word or word.startswith("logs"):
                paths.append(word.strip("'\""))
        return paths

    def evaluate_failure(self, step_result):
        """
        Diagnoses why FE failed and determines if retry or escalation is needed.
        """
        self.logger.error(f"DIAGNOSTIC | Step failed: {step_result}")
        return "ESCALATE_TO_USER"
