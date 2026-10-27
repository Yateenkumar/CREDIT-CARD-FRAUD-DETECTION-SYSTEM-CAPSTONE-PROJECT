import os
import subprocess
import sys
import time

PYTHON_EXE = sys.executable

def main():
    print("=" * 60)
    print("Starting Credit Card Fraud Detection System...")
    print("=" * 60)
    
    project_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Start FastAPI Backend
    print("[1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [PYTHON_EXE, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=project_dir
    )
    
    # Give backend a moment to spin up
    time.sleep(2)
    
    # 2. Start Streamlit Frontend
    print("[2/2] Starting Streamlit frontend on http://localhost:8501 ...")
    frontend_proc = subprocess.Popen(
        [PYTHON_EXE, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.headless", "true"],
        cwd=project_dir
    )
    
    print("\n" + "=" * 60)
    print("All services are live and running!")
    print("FastAPI Backend: http://127.0.0.1:8000")
    print("Swagger API Docs: http://127.0.0.1:8000/docs")
    print("Streamlit Frontend Web App: http://localhost:8501")
    print("=" * 60 + "\n")
    
    try:
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        try:
            backend_proc.terminate()
        except Exception:
            pass
        try:
            frontend_proc.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    main()
