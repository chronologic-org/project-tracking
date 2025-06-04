"""
Entry point for the Team Project & Problem Tracker application.
"""
import os
import sys
import streamlit.web.cli as stcli

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "src/app.py"]
    sys.exit(stcli.main()) 