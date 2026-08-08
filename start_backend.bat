@echo off
echo ============================================================
echo  AI House Architect - Starting Backend Server
echo ============================================================

set PYTHONPATH=%~dp0

echo [1] Checking if models are trained...
"C:\Users\nasee\AppData\Local\Programs\Python\Python312\python.exe" -c "import os; exit(0 if os.path.exists('models/layout_model/pytorch_layout_model.pt') else 1)"
if %errorlevel% NEQ 0 (
    echo [2] Models not found. Running training bootstrap...
    "C:\Users\nasee\AppData\Local\Programs\Python\Python312\python.exe" run_training.py
) else (
    echo [2] Pre-trained models found. Skipping training.
)

echo [3] Starting FastAPI backend server...
"C:\Users\nasee\AppData\Local\Programs\Python\Python312\python.exe" main.py
