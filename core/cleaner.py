import os
import time
from datetime import datetime

def get_old_files(folder_path, days_threshold=30):
    """
    Scan for files not accessed in the last X days.
    Returns a list of (file_path, size_in_MB, last_access_time).
    """
    old_files = []
    cutoff_time = time.time() - (days_threshold * 86400)

    if not os.path.exists(folder_path):
        print(f"⚠️ Folder not found: {folder_path}")
        return old_files

    for root, _, files in os.walk(folder_path):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                last_access = os.path.getatime(filepath)
                if last_access < cutoff_time:
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    old_files.append((filepath, round(size_mb, 2), datetime.fromtimestamp(last_access)))
            except Exception as e:
                print(f"❌ Error accessing {filepath}: {e}")
    return old_files

def summarize_old_files(folder_path, days=30):
    old_files = get_old_files(folder_path, days)
    total_size = sum(f[1] for f in old_files)

    print(f"\n📂 Folder: {folder_path}")
    print(f"🕒 Files not accessed in last {days} days: {len(old_files)}")
    print(f"🧮 Total space: {round(total_size, 2)} MB")

    for f in old_files:
        print(f"  🗂️ {f[0]} — {f[1]} MB — last accessed {f[2]}")

    return old_files
