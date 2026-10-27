@echo off
set "PYTHON_EXE=C:\Users\yatee\AppData\Roaming\uv\python\cpython-3.10.22-windows-x86_64-none\python.exe"
cd /d "%~dp0"
"%PYTHON_EXE%" deploy_hf.py
pause
