import subprocess
import os

def get_default_browser():
    plist_path = os.path.expanduser('~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist')

    try:
        result = subprocess.run(
            ['plutil', '-extract', 'LSHandlers', 'xml1', '-o', '-', plist_path],
            capture_output=True, text=True
        )

        output = result.stdout.lower()

        if 'chrome' in output:
            return 'chrome'
        elif 'firefox' in output:
            return 'firefox'
        elif 'safari' in output:
            return 'safari'

    except Exception as e:
        print(f"Error detecting default browser: {e}")

    return 'unknown'



import sqlite3
import os
import datetime

def get_chrome_history(limit=100):
    db_path = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/History")

    if not os.path.exists(db_path):
        print("❌ Chrome history DB not found.")
        return []

    # Chrome locks the DB, so copy it
    tmp_copy = "/tmp/chrome_history_copy"
    try:
        os.system(f"cp '{db_path}' '{tmp_copy}'")
        conn = sqlite3.connect(tmp_copy)
        cursor = conn.cursor()

        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()

        def chrome_time_to_unix(microseconds):
            epoch_start = datetime.datetime(1601, 1, 1)
            return epoch_start + datetime.timedelta(microseconds=microseconds)

        history = [{
            "url": row[0],
            "title": row[1],
            "time": chrome_time_to_unix(row[2]).strftime('%Y-%m-%d %H:%M:%S')
        } for row in rows]

        conn.close()
        return history

    except Exception as e:
        print(f"❌ Error reading Chrome history: {e}")
        return []



if get_default_browser() == 'chrome':

    for x in get_chrome_history():
        print(x['title'])