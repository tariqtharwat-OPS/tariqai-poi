# Tariq AI POI : Tech Stack Review (2025/2026)

## 1. Python Version Compatibility
*   **Current**: Python 3.12.10
*   **Compatibility**: Compatible with 3.10+ (uses type hinting and Pathlib). Fully supports latest 3.13 features but not yet implemented.

## 2. Dependency List
*   **Standard Library**: `pathlib`, `json`, `logging`, `uuid`, `unittest`, `shutil`, `datetime`.
*   **External (Dev only)**: `pytest` (v7.0.0+).

## 3. Outdated or Fragile Technologies
*   **Hand-rolled Intent Parsing**: ST uses manual string patterns and simple logic to map prompts to actions. Extremely fragile compared to modern tool-calling LLM integrations.
*   **Manual Persistence**: JSON files are used for database-like storage. Lack of ACID compliance (No transactions, no rollbacks).
*   **Simulated UI Layer**: `FE` actions for UI (`press_button`) are just log entries. No real connectivity to the OS display server.

## 4. 2025 Alternatives (Advanced)
| Component | Current Tech | 2025 Alternative | Pros / Cons |
| :--- | :--- | :--- | :--- |
| **Logic** | Manual ST Plan | **LangChain / PydanticAI** | **Pros**: Robust tool usage, structured data. **Cons**: Heavy deps, API cost. |
| **Parsing** | Regex / String Ops | **Instructor / LLM Tool Calling** | **Pros**: Handles messy human input. **Cons**: Latency. |
| **Persistence** | JSON Files | **SQLite (WAL mode)** | **Pros**: Atomic, thread-safe. **Cons**: Requires migration. |
| **UI Control** | Print simulation | **Playwright / PyAutoGUI** | **Pros**: Real OS interaction. **Cons**: Brittle on resolution changes. |

## 5. Replacement Priority
*   **REPLACE NOW**: Path extraction logic in `ST`. It is the primary cause of failures in Phase 5/6 demos.
*   **REPLACE LATER**: Migration from JSON persistence to SQLite to prevent "Crash Mid-Op" corruption.
*   **REPLACE LATER**: Bridge between simulated UI actions and real `Autohotkey` or `SikuliX` scripts.
