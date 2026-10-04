"""
Streamlit Community Cloud entrypoint proxy.
Enables automatic discovery when Streamlit Cloud defaults to 'streamlit_app.py'.
"""
import runpy
import sys
import os

# Ensure current working directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Execute main application script
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py"), run_name="__main__")
