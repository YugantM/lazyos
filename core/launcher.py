import json
import os
import platform
import subprocess
import webbrowser
import datetime
from core.logger import log_launch


# Paths
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'configs', 'modes.json')
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'launch.log')

# Load all modes from config file
def load_modes():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

# Launch mode: open apps and browser tabs
def launch_mode(mode_name):
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
