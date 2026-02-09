# Tariq AI POI : Execution Safety Audit

## 1. What file operations are truly “live”?
The following actions in `D:/TariqAI/src/poi/fe/layer.py` are LIVE and execute against the real host filesystem:
*   `file_create`: Creates empty files.
*   `file_move`: Renames or relocates files/directories.
*   `file_copy`: Duplicates files/directories.
*   `file_delete`: Removes files or recursive directories (WARNING).
*   `file_list`: Reads directory contents.

## 2. What prevents accidental recursive / destructive ops?
*   **Intent Labeling**: `ST` classifies deletion/overwrite as `FILE_DESTRUCTION` with `risk_level="CRITICAL"`.
*   **Governance Block**: `IML` (Identity Memory Layer) treats `CRITICAL` risk as an absolute block. Even with high trust, the code in `iml.validate_action` forces a `False` return on critical items.
*   **Human Gate**: All blocked actions must pass through `ConfirmationManager` which presents a "Consequence Summary" before the user can select "Approve".

## 3. What happens on crash mid-operation?
*   **Zero Protection**: If the Python process crashes during a `shutil.copy` or `os.rename`, the filesystem may contain partially written files (`.tmp` behavior is NOT implemented). 
*   **Corrupt Memory**: If the process crashes during a JSON write for audit logs, the logs may be truncated or corrupted.

## 4. Is there rollback or dry-run always enforced?
*   **NO DRY-RUN**: Actions are executed directly. There is no simulation phase for file operations.
*   **NO ROLLBACK**: If an operation fails (e.g., `PermissionError`), subsequent steps in a multi-step plan are halted, but previous successful steps are NOT undone.
