import dearpygui.dearpygui as dpg
import sys
import os
import json
import re
import platform
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.launcher import launch_mode
from core.launcher import load_modes

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'configs', 'modes.json'))

def is_valid_url(url):
    return re.match(r'^https?://', url)

def get_installed_apps_mac():
    app_dirs = ["/Applications", os.path.expanduser("~/Applications")]
    apps = set()

    for directory in app_dirs:
        if os.path.exists(directory):
            for f in os.listdir(directory):
                if f.endswith(".app"):
                    apps.add(f.replace(".app", ""))
    return sorted(apps)

def safe_tag(text):
    return text.strip().replace(" ", "_").replace(".", "_").replace("-", "_").replace("/", "_").lower()

def save_gui_config():
    updated = {}
    modes = load_modes()
    installed_apps = get_installed_apps_mac()

    for mode_name in modes.keys():
        selected_apps = []
        for app in installed_apps:
            tag = f"{mode_name}_app_{safe_tag(app)}"
            if dpg.does_item_exist(tag) and dpg.get_value(tag):
                selected_apps.append(app)

        tab_tag = f"{mode_name}_tabs"
        if dpg.does_item_exist(tab_tag):
            tab_input = dpg.get_value(tab_tag)
            tabs = [url.strip() for url in tab_input.split(",") if url.strip() and is_valid_url(url.strip())]
        else:
            tabs = []

        comment_tag = f"{mode_name}_comment"
        comment = dpg.get_value(comment_tag) if dpg.does_item_exist(comment_tag) else ""

        updated[mode_name] = {
            "apps": selected_apps,
            "tabs": tabs,
            "comment": comment
        }

    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(updated, f, indent=4)
        print("✅ Config saved to modes.json")
        dpg.delete_item("config_window")
    except Exception as e:
        print(f"❌ Error saving config: {e}")

def open_config_editor():
    modes = load_modes()
    installed_apps = get_installed_apps_mac()

    with dpg.window(label="Edit Modes", modal=True, width=600, height=500, tag="config_window"):
        dpg.add_text("🛠️ Configure modes easily")

        with dpg.tab_bar():
            for mode_name, data in modes.items():
                with dpg.tab(label=mode_name.title()):
                    dpg.add_text(f"Editing mode: {mode_name}")

                    # ✅ Normalize the current mode's config apps list
                    normalized_config_apps = [a.strip().lower() for a in data.get("apps", [])]

                    dpg.add_text("Select apps:")

                    with dpg.child_window(width=550, height=180, border=True):
                        for app in installed_apps:
                            normalized_app = app.strip().lower()
                            is_checked = normalized_app in normalized_config_apps
                            checkbox_tag = f"{mode_name}_app_{safe_tag(app)}"

                            #print(f"{'✔' if is_checked else '✘'} {app} → {checkbox_tag}")

                            dpg.add_checkbox(
                                label=app,
                                tag=checkbox_tag,
                                default_value=is_checked
                            )

                    dpg.add_text("Web tabs (comma-separated):")
                    dpg.add_input_text(tag=f"{mode_name}_tabs",
                                       default_value=", ".join(data.get("tabs", [])),
                                       multiline=True, width=500, height=100)

                    dpg.add_text("Mode comment:")
                    dpg.add_input_text(tag=f"{mode_name}_comment",
                                       default_value=data.get("comment", ""), width=500)

        with dpg.group(horizontal=True):
            dpg.add_button(label="✅ Save Config", callback=save_gui_config)
            dpg.add_button(label="❌ Cancel", callback=lambda: dpg.delete_item("config_window"))

def on_mode_click(sender, app_data, user_data):
    launch_mode(user_data)

def build_gui():
    dpg.create_context()
    dpg.create_viewport(title='Ayo Launcher', width=400, height=250)

    with dpg.window(label="Ayo Launcher", width=380, height=220):
        dpg.add_text("👋 Ayo is ready to help you switch modes.")
        dpg.add_spacer(height=10)
        dpg.add_button(label="🚀 Work Mode", callback=on_mode_click, user_data="work")
        dpg.add_button(label="📚 Learn Mode", callback=on_mode_click, user_data="learn")
        dpg.add_button(label="🌴 Chill Mode", callback=on_mode_click, user_data="chill")
        dpg.add_button(label="🛠️ Edit Modes Config", callback=open_config_editor)
        dpg.add_spacer(height=10)
        dpg.add_text("🧠 Tip: You can also run this via CLI.")

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    build_gui()
