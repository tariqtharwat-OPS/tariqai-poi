import logging
import re
from pathlib import Path

class HowToResearch:
    """
    Phase 10.2: Research module to gather how-to instructions.
    """
    def __init__(self, executor):
        self.executor = executor
        self.logger = logging.getLogger("HowToResearch")

    def research_task(self, query):
        """
        Gathers how-to instructions for a given query.
        """
        self.logger.info(f"RESEARCH | Searching for: {query}")
        
        # 1. Search (using browser_open to a search engine for now)
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        res = self.executor.execute_step({"action": "browser_open", "params": {"url": search_url}}, {"intent_type": "RESEARCH", "risk_level": "LOW"})
        
        if res["status"] != "SUCCESS":
            self.logger.warning(f"RESEARCH | Search non-success: {res['status']}. Continuing with generic steps.")

        # 2. Collect sources (Mocked for deterministic phase, usually extracts search result URLs)
        sources = [
            {"title": "How to " + query, "url": search_url},
            {"title": "Official guide", "url": "https://docs.microsoft.com/en-us/search/?terms=" + query}
        ]

        # 3. Extract steps (Simplified heuristic: finding bullet points or numbers)
        # For now, we simulate extraction from content
        steps = [
            "Open the relevant application or website.",
            f"Navigate to the {query} section.",
            "Follow the on-screen instructions.",
            "Save your progress before closing."
        ]

        # 4. Produce Brief
        # Sanitize filename: remove non-alphanumeric but keep Arabic chars
        safe_query = re.sub(r'[^\w\s]', '', query[:30]).replace(' ', '_')
        brief_path = Path(f"D:/TariqAI/logs/tmp/howto_{safe_query}.md")
        
        brief_content = f"# How-To Brief: {query}\n\n"
        brief_content += "## Recommended Steps\n"
        for i, step in enumerate(steps):
            brief_content += f"{i+1}. {step}\n"
        
        brief_content += "\n## Citations\n"
        for src in sources:
            brief_content += f"- [{src['title']}]({src['url']})\n"

        # Write directly to Safe Zone
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        with open(brief_path, "w", encoding="utf-8") as f:
            f.write(brief_content)
        
        self.logger.info(f"RESEARCH | Brief saved to: {brief_path}")

        return {
            "status": "SUCCESS",
            "brief_path": str(brief_path),
            "steps": steps,
            "citations": sources
        }
