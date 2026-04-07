import sys
import os
import subprocess

def main():
    """Isolated entry point for the agentic-factory CLI."""
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'app.py')
    
    # Force a fresh subprocess to avoid runtime/context conflicts
    cmd = [
        sys.executable, 
        "-m", 
        "streamlit", 
        "run", 
        filename,
        "--server.headless", "false",
        "--server.runOnSave", "false"
    ] + sys.argv[1:]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error launching factory: {e}")
        sys.exit(1)
