import os
import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'launch.log')

def ensure_log_folder():
    log_dir = os.path.dirname(LOG_PATH)
    os.makedirs(log_dir, exist_ok=True)

def log_launch(mode_name, apps=None, tabs=None):
    ensure_log_folder()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{now}] Mode: {mode_name}\n"

    if apps:
        log_entry += f"  Apps: {', '.join(apps)}\n"
    if tabs:
        log_entry += f"  Tabs: {', '.join(tabs)}\n"

    log_entry += "-" * 40 + "\n"

    with open(LOG_PATH, "a") as f:
        f.write(log_entry)

def log_note(note):
    ensure_log_folder()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, "a") as f:
        f.write(f"[{now}] NOTE: {note}\n")
