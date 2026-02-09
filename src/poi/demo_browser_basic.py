import sys
from pathlib import Path
import os

# Absolute path setup
sys.path.append("D:/TariqAI/src")

from poi.core import POICore
from poi.interface.models import UserDecision, DecisionType

def run_browser_demo():
    print("="*80)
    print("🛡️  TARIQ AI POI - PHASE 7 BROWSER DEMO")
    print("="*80)
    
    # 1. Initialize with DRY_RUN to show planning only first
    os.environ["DRY_RUN"] = "1"
    poi = POICore()
    
    # Mock UI to auto-approve
    class BrowserMockUI:
        def request_human_oversight(self, *args, **kwargs):
            action = kwargs.get('action')
            url = kwargs.get('params', {}).get('url')
            print(f"\n[SHIELD] Action: {action} on {url}")
            print("[USER] Approving browser session...")
            return UserDecision(request_id="ph7_browser_demo", decision=DecisionType.APPROVE_ONCE)

    poi.interface = BrowserMockUI()
    
    print("\n[STEP 1] ATTEMPTING BROWSER SEARCH (DRY_RUN)")
    # Note: StrategicThinker extracts URL from prompt
    poi.handle_request("Open website https://example.com and extract content")
    
    print("\n[STEP 2] LIVE BROWSER EXECUTION")
    os.environ["DRY_RUN"] = "0"
    poi.fe.dry_run = False
    
    # Run a real search/extract
    # We'll use a dead-simple public page
    res = poi.handle_request("Visit https://example.com and extract content")
    
    if res["status"] == "SUCCESS":
        result_data = res["results"][0].get("data", {})
        print(f"\n[DEMO] Browser Success!")
        print(f"Title: {result_data.get('title')}")
        print(f"Content Length: {len(result_data.get('content'))} characters")
    else:
        print(f"\n[DEMO] Browser Failed: {res.get('message')}")

    print("\n" + "="*80)

if __name__ == "__main__":
    run_browser_demo()
