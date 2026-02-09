import sys
from pathlib import Path

# Add src to path
sys.path.append("D:/TariqAI/src")

from poi.core import POICore

def run_phase2_demo():
    print("="*60)
    print("TARIQ AI POI - PHASE 2 DEMO (PERCEPTION LAYER)")
    print("="*60)
    
    poi = POICore()
    
    # Simulate a request where context matters
    print("\n--- REQUEST 1: ENVIRONMENT-AWARE THINKING ---")
    print("Intent: 'Save the current file'")
    # ST should now see that 'Save' button exists in the perception model
    poi.handle_request("Save the current file")

    print("\n--- REQUEST 2: SEMANTIC MAPPING VERIFICATION ---")
    # Capturing raw perception output to show the user the semantic map
    model = poi.perception.capture_environment()
    print(f"\n[DEMO] Full Semantic Model for '{model.active_window}':")
    for entity in model.entities:
        print(f"  - Entity: {entity.label} ({entity.type})")
        print(f"    Purpose: {entity.purpose}")
        print(f"    Location: {entity.location}")
        print(f"    Confidence: {entity.confidence}")

    print("\n" + "="*60)
    print("PHASE 2 DEMO COMPLETE")
    print("Notice how ST now consumes exactly what 'Vision' sees.")
    print("="*60)

if __name__ == "__main__":
    run_phase2_demo()
