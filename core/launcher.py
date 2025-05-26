import json
import os
import platform
import subprocess
import webbrowser
import datetime
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.logger import log_launch
from core.browser_analyzer import BrowserAnalyzer

# Paths
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'configs', 'modes.json')
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'launch.log')

# Load all modes from config file
def load_modes():
    """Load all modes from config file."""
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def update_modes():
    """Update modes based on browser analysis."""
    analyzer = BrowserAnalyzer()
    history_df = analyzer.get_browser_history(days=30)
    
    if not history_df.empty:
        processed_df = analyzer.preprocess_data(history_df)
        clustered_df = analyzer.cluster_tabs(processed_df)
        modes = analyzer.generate_modes(clustered_df)
        analyzer.update_modes_json(modes, CONFIG_PATH)
        print("✅ Modes updated successfully!")
    else:
        print("⚠️ No browser history data found")

# Launch mode: open apps and browser tabs
def launch_mode(mode_name):
    """Launch mode: open apps and browser tabs."""
    modes = load_modes()
    if mode_name not in modes:
        print(f"❌ Mode '{mode_name}' not found in config.")
        return

    mode = modes[mode_name]
    apps = mode.get("apps", [])
    tabs = mode.get("tabs", [])
    comment = mode.get("comment", "")

    print(f"💡 Launching mode: {mode_name}")
    print(f"📝 Note: {comment}")

    # Launch apps
    for app in apps:
        print(f"🚀 Launching app: {app}")
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", app])
            elif platform.system() == "Windows":
                subprocess.Popen(["start", "", app], shell=True)
            elif platform.system() == "Linux":
                subprocess.Popen([app])
            else:
                print("⚠️ Unsupported OS")
        except Exception as e:
            print(f"❌ Failed to launch {app}: {e}")

    # Launch tabs
    for url in tabs:
        print(f"🌐 Opening tab: {url}")
        webbrowser.open_new_tab(url)

    # Log launch
    log_launch(mode_name, apps, tabs)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--update":
            update_modes()
        else:
            launch_mode(sys.argv[1])
    else:
        print("Usage: python launcher.py [mode_name|--update]")
