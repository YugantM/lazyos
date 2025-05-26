import os
import json
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'launch.log')

def ensure_log_folder():
    log_dir = os.path.dirname(LOG_PATH)
    os.makedirs(log_dir, exist_ok=True)

def log_launch(mode_name, apps, tabs):
    """Log a mode launch event."""
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    
    # Create log entry
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'mode': mode_name,
        'apps': apps,
        'tabs': tabs
    }
    
    # Append to log file
    with open(LOG_PATH, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def log_note(note):
    ensure_log_folder()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, "a") as f:
        f.write(f"[{now}] NOTE: {note}\n")
