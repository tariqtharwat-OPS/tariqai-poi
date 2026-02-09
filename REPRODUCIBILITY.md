# Tariq AI POI : Reproducibility Guide

## 1. Installation
Run the following command from the project root:
```powershell
pip install -r requirements.txt
```

## 2. Run All Tests
Run the following command to execute the full Phase 5 and Phase 6 validation suite:
```powershell
pytest D:/TariqAI/src/tests/smoke/ D:/TariqAI/src/tests/real/
```

## 3. Expected Output
Success looks like:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10
collecting ... collected 4 items

src/tests/real/test_phase5_real.py .                                     [ 25%]
src/tests/real/test_phase6_real.py .                                     [ 50%]
src/tests/smoke/test_phase5_smoke.py .                                   [ 75%]
src/tests/smoke/test_phase6_smoke.py .                                   [100%]

============================== 4 passed in 2.15s ==============================
```

*Note: You will also see INFO and WARNING logs from the IML/FE layers printed to stdout during the 'real' tests. This is expected.*
