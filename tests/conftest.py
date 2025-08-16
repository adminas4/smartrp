# tests/conftest.py
import sys, os

# Į sys.path įdedam repo šaknį, kad importai kaip "from backend.app.main import app" veiktų
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
