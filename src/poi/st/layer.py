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

    def get_intent(self, prompt, perception_model=None):
        """
        New interface for Phase 10.2: Intent + Risk + Plan + Clarification.
        """
        p = prompt.lower()
        
        # 1. UNDERSTAND: Logic for missing info
        has_location = any(w in p for w in ["in ", "at ", "near ", "في ", "بـ"])
        needs_location = any(w in p for w in ["search", "find", "restaurant"])
        
        if needs_location and not has_location:
             self.logger.info("CLARIFY_TRIGGER | Missing location in prompt.")
             return "CLARIFY", {"question": "Which city or location should I search in?", "intent_id": str(uuid.uuid4())[:8]}

        intent_type = self._classify_intent(prompt)
        risk_level = self._assess_risk(prompt)
        context_signature = self._generate_context_signature(prompt, intent_type)
        
        # 2. RESEARCH TRIGGER
        # Determine if we need 'How-to' research
        needs_research = self._needs_howto(prompt, intent_type)
        
        decision = {
            "intent_id": str(uuid.uuid4())[:8],
            "intent_type": intent_type,
            "risk_level": risk_level,
            "context_signature": context_signature,
            "needs_research": needs_research,
            "plan": self._generate_plan(prompt, intent_type, needs_research=needs_research)
        }
        
        self.iml.log_intent(decision["intent_id"], decision)
        return intent_type, decision

    def _needs_howto(self, prompt, intent_type):
        p = prompt.lower()
        # Trigger research for how-to instructions if ambiguous or complex
        if any(w in p for w in ["how to", "طريقة", "شرح", "كيف"]):
            return True
        if intent_type == "GENERAL_QUERY" and len(prompt.split()) > 5:
            return True
        return False

    def _classify_intent(self, prompt):
        p = prompt.lower()
        
        # Deterministic Tool Selection based on entities (URL, extensions)
        url = self._extract_url(prompt)
        if url: return "BROWSER"
        
        # Phase 10.2 SEARCH Prioritization
        if any(w in p for w in ["search", "find", "بحث"]):
            return "BROWSER"
        
        # Arabic support
        if any(w in p for w in ["بحث", "متصفح", "موقع"]): return "BROWSER"
        if any(w in p for w in ["اكسل", "جدول"]): return "DOCUMENT_EXCEL"
        if any(w in p for w in ["وورد", "تقرير", "ملف"]): return "DOCUMENT_WORD"
        if any(w in p for w in ["قائمة", "استعراض"]): return "FILE_NAVIGATION"
        if any(w in p for w in ["انقل", "انسخ", "انشئ"]): return "FILE_OPERATION"

        # Phase 11 Desktop MVP
        if any(w in p for w in ["notepad", "windows", "desktop", "click", "type"]):
            return "DESKTOP_TASK"
        
        if "delete" in p and "gmail" in p:
            return "GMAIL_DELETE"

        # Deterministic Tool Selection based on entities (URL, extensions)
        url = self._extract_url(prompt)
        if url: return "BROWSER"
        
        path = self._extract_path(prompt)
        if path:
            if path.lower().endswith(".docx"): return "DOCUMENT_WORD"
            if path.lower().endswith((".xlsx", ".xls")): return "DOCUMENT_EXCEL"
            if "." in path: return "FILE_OPERATION"

        if any(w in p for w in ["browser", "search", "open page", "visit", "website", "open http"]):
            return "BROWSER"
        if any(w in p for w in ["excel", "xlsx", "spreadsheet", "table"]):
            return "DOCUMENT_EXCEL"
        if any(w in p for w in ["word", "docx", "document", "report"]):
            return "DOCUMENT_WORD"
        if any(w in p for w in ["list", "look inside", "show files", "find", "locate"]):
            return "FILE_NAVIGATION"
        if any(w in p for w in ["rename", "move", "copy", "create", "make folder", "setup"]):
            return "FILE_OPERATION"

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

    def _generate_plan(self, prompt, intent_type, needs_research=False):
        """
        Phase 10.2: Think -> Research -> Plan.
        """
        p = prompt.lower()
        plan = []

        if needs_research:
            # We add a special placeholder action that Core will intercept 
            # Or ST can include the research step if it has access to HowToResearch (passing it in)
            # For simplicity, let's have Core handle the orchestration of Research module
            plan.append({"action": "research_howto", "params": {"query": prompt}})

        
        if intent_type == "BROWSER":
            url = self._extract_url(prompt) or "https://www.google.com"
            plan.extend([
                {"action": "browser_open", "params": {"url": url}},
                {"action": "browser_extract", "params": {"mode": "html"}}
            ])
            
            path = self._extract_path(prompt, skip_urls=True)
            if path:
                plan.append({"action": "file_write", "params": {"path": path}})
            elif "save" in p or "to" in p:
                # Fallback to tmp excel if sushi/restaurant search
                if "excel" in p:
                    plan.append({"action": "excel_create", "params": {"path": "D:/TariqAI/logs/tmp/search_results.xlsx"}})
                else:
                    plan.append({"action": "file_write", "params": {"path": "D:/TariqAI/logs/tmp/extracted.txt"}})

        elif intent_type == "DOCUMENT_WORD":
            path = self._extract_path(prompt) or "D:/TariqAI/logs/new_report.docx"
            plan.append({"action": "word_create", "params": {
                "path": path, 
                "title": "Tariq AI Automated Report",
                "bullets": self._extract_bullets(prompt)
            }})

        elif intent_type == "DOCUMENT_EXCEL":
            path = self._extract_path(prompt) or "D:/TariqAI/logs/data_sheet.xlsx"
            plan.append({"action": "excel_create", "params": {
                "path": path,
                "sheet_name": "TariqData",
                "data": [["Result", "Value"], ["Extraction", "Success"]]
            }})

        elif intent_type == "FILE_NAVIGATION":
            target_path = self._extract_path(prompt) or "."
            plan.append({"action": "file_list", "params": {"path": target_path}})

        elif intent_type == "FILE_OPERATION":
            paths = self._extract_paths(prompt)
            if "create" in p or "make" in p or "انشئ" in p:
                plan.append({"action": "file_create", "params": {"path": paths[0] if paths else "new_file.txt"}})
            elif "move" in p or "rename" in p or "انقل" in p:
                if len(paths) >= 2:
                    plan.append({"action": "file_move", "params": {"src": paths[0], "dst": paths[1]}})
            elif "copy" in p or "انسخ" in p:
                if len(paths) >= 2:
                    plan.append({"action": "file_copy", "params": {"src": paths[0], "dst": paths[1]}})

        elif intent_type == "DESKTOP_TASK":
            if "notepad" in p:
                plan.extend([
                    {"action": "desktop_hotkey", "params": {"keys": ["{Win}", "r"]}},
                    {"action": "desktop_type", "params": {"text": "notepad{Enter}"}},
                    {"action": "desktop_focus", "params": {"window_name": "Notepad"}},
                    {"action": "desktop_type", "params": {"text": "Tariq AI Desktop MVP\nLine 1\nLine 2\nLine 3"}},
                    {"action": "desktop_hotkey", "params": {"keys": ["{Ctrl}", "s"]}},
                    {"action": "desktop_type", "params": {"text": "D:\\TariqAI\\logs\\tmp\\notepad_test.txt{Enter}"}}
                ])
        
        elif intent_type == "GMAIL_DELETE":
             # Blocked by IML, but we can generate a safe assist plan here if needed
             # For Phase 11, the goal is to show it's blocked.
             plan.append({"action": "chat", "params": {"message": "I am prohibited from deleting emails. I can help you set up filters instead."}})

        if not plan:
            plan = [{"action": "chat", "params": {"message": f"I understand your request for {prompt}. How should I proceed?"}}]
            
        return plan


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
