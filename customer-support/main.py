# main.py
import os
import sys
import subprocess
import time
from dotenv import load_dotenv
load_dotenv()

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Check backend package
if not os.path.exists(os.path.join(PROJECT_ROOT, "backend", "__init__.py")):
    raise RuntimeError("❌ backend/__init__.py is missing. Create an empty file to make it a package.")

# Paths
APP_PATH = os.path.join(PROJECT_ROOT, "frontend", "app.py")
DASHBOARD_PATH = os.path.join(PROJECT_ROOT, "frontend", "dashboard.py")

if not os.path.exists(APP_PATH) or not os.path.exists(DASHBOARD_PATH):
    raise FileNotFoundError("❌ Could not find app.py or dashboard.py")

# Start both apps on different ports
print("🚀 Launching FAQ RAG App (port 8501)...")
app_proc = subprocess.Popen(["streamlit", "run", APP_PATH, "--server.port", "8501"])

# Small delay to avoid conflicts
time.sleep(3)

print("📊 Launching Admin Dashboard (port 8502)...")
dash_proc = subprocess.Popen(["streamlit", "run", DASHBOARD_PATH, "--server.port", "8502"])

print("\n✅ Both apps are running!")
print("🌐 User App:       http://localhost:8501")
print("🔐 Admin Dashboard: http://localhost:8502")

# Keep the script running to maintain subprocesses
try:
    app_proc.wait()
    dash_proc.wait()
except KeyboardInterrupt:
    print("\n🛑 Shutting down...")
    app_proc.terminate()
    dash_proc.terminate()
