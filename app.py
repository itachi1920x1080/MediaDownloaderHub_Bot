import os
import sys
import importlib.util

# Change working directory to backend so that paths resolve correctly
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

# Load backend/app.py safely without naming conflicts
spec = importlib.util.spec_from_file_location("backend_app", os.path.join(backend_dir, "app.py"))
backend_app = importlib.util.module_from_spec(spec)
sys.modules["backend_app"] = backend_app
spec.loader.exec_module(backend_app)

# Expose the Flask app object so gunicorn can find it
app = backend_app.app
