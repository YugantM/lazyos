import json
import os
import platform
import subprocess
import webbrowser

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'configs', 'modes.json')

def load_modes():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

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
        if platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", app])
        elif platform.system() == "Windows":
            subprocess.Popen(["start", "", app], shell=True)
        elif platform.system() == "Linux":
            subprocess.Popen([app])
        else:
            print("⚠️ Unsupported OS")

    # Launch tabs
    for url in tabs:
        print(f"🌐 Opening tab: {url}")
        webbrowser.open_new_tab(url)
