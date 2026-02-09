# Intelligence Core Specification (ICS)

## I. Architecture Overview
The Tariq AI Intelligence Core is a tri-layered routing system designed to balance speed, reasoning depth, and contextual continuity.

## II. Layer Definitions & Responsibility Boundaries

### **1. Fast Executor (FE)**
*   **Role**: Reaction and Routine.
*   **Responsibility**: Executing high-frequency, low-entropy sequences (typing, clicking known semantic targets, standard file I/O).
*   **Constraint**: Zero reasoning. If a step deviates by 1% from the expected outcome, the FE must halt and escalate to the Strategic Thinker.
*   **Routing**: Triggered for tasks with >98% historical success or direct technical mapping.

### **2. Strategic Thinker (ST)**
*   **Role**: Synthesis and Planning.
*   **Responsibility**: Semantic environment analysis (Vision-to-Intent), multi-step task decomposition, error diagnostics, and strategy revision.
*   **Constraint**: High-latency, high-cost. Restricted to "Planning Phase" and "Failure Recovery" only.
*   **Routing**: Triggered for initial intent mapping, ambiguous environment states, or FE halts.

### **3. Identity & Memory Layer (IML)**
*   **Role**: Truth and Standard.
*   **Responsibility**: Maintaining the "Constitution" alignment, user preferences, failure history (Anti-Patterns), and successful workflow signatures.
*   **Constraint**: Read-access for every FE/ST call; Write-access post-validation of outcomes.
*   **Routing**: Acts as the "Governor" for both FE and ST. No action proceeds if IML identifies a Constitutional violation or a previously recorded failure pattern.

## III. Routing Rules
1. **Initial Input**: ST analyzes the Intent against IML history.
2. **Path Selection**: 
    - If "Routine": Pass to FE.
    - If "Novel": ST maintains control, executing one step at a time via FE bridges.
3. **Environment Change**: Perception detects a UI change -> Immediate shift from FE to ST for re-evaluation.
4. **Outcome Validation**: Post-execution, IML records the Delta between "Expected" and "Actual" results.
