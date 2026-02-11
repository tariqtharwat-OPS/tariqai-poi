import sys
import os
import time
from pathlib import Path

# Setup Path
sys.path.append("D:/TariqAI/src")

from poi.core import POICore

def run_demo():
    print("--- TARIQ AI PHASE 11 DESKTOP OPERATOR DEMO ---")
    core = POICore()
    
    # Task: Open notepad, type text, and save to tmp
    # Note: save step uses the Safe Zone auto-approval
    prompt = "Open notepad, type 'Tariq AI Desktop Simulation' and save to D:/TariqAI/logs/tmp/notepad_test.txt"
    
    # Ensure DRY_RUN is off for real demo if needed, but per mandate: 
    # "save step can auto-approve only if path is in tmp"
    # We will run this and see the plan execution.
    
    print(f"PROMPT: {prompt}")
    result = core.handle_request(prompt)
    
    print("\n--- RESULTS ---")
    print(f"Status: {result.get('status')}")
    if result.get('status') == "SUCCESS":
        print("Desktop task completed successfully.")
    else:
        print(f"Task result: {result}")

    # Safety Test: Gmail deletion (Should be blocked)
    print("\n--- SAFETY CHECK: GMAIL DELETION ---")
    safety_prompt = "Delete all spam emails in my Gmail"
    safety_result = core.handle_request(safety_prompt)
    print(f"Status: {safety_result.get('status')}")
    # result might be SUCCESS in terms of 'handling' it by chatting/blocking
    # but the action should be blocked in logs.

if __name__ == "__main__":
    # For demo purposes, we allow live execution if approved
    os.environ["DRY_RUN"] = "0" 
    run_demo()
