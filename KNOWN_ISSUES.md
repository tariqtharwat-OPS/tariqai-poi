# Tariq AI POI : Known Issues & Failure Modes

## 1. Known Bugs
*   **Path Parser Failure**: Fails to extract paths containing spaces or multiple periods outside of the extension.
*   **Trust Re-init**: If `trust_escalation.json` is manually deleted, all trust is lost with no backup restoration.
*   **Dashboard Rendering**: Long audit trails (>1000 entries) cause significant lag in CLI rendering as the entire file is parsed in-memory.

## 2. Race Conditions
*   **Concurrent I/O**: `iml.record_outcome` and `iml.log_human_decision` both modify JSON files. In a multi-threaded scenario, one write would overwrite the other. (System is currently single-threaded/sequential).
*   **Log Collision**: Multiple processes pointing to the same `audit_trail.log` will result in interleaved/garbled lines.

## 3. Logic Assumptions
*   **Human is Trustworthy**: The system assumes any human decision is "safe." It does not cross-reference human approval against the Constitution if the human explicitly clicks "Approve."
*   **Absolute Paths**: Assumes the host OS uses `/` or `\` correctly based on Python's `Path` object; however, ST regex is mostly tuned for Unix/Windows hybrid style seen in user prompts.

## 4. Areas with No Test Coverage
*   **Adapter Failure**: No tests for when `DesktopAdapter` fails to capture a screenshot or window list (Perception Layer).
*   **Disk Full**: No test coverage for file operation failures due to IO errors (Permission, Disk Space, etc.).
*   **Governance Bypass**: No negative tests for attempting to bypass governance with an invalid token (not yet implemented).
