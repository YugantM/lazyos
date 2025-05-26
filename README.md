<p align="center">
  <img src="https://raw.githubusercontent.com/YugantM/lazyos/main/assets/images/logo/logo_main.png" height="120px"><br>
  <b>LazyOS</b> · Powered by Ayo 🧠<br>
  <i>Your local-first assistant for flow, focus, and digital freedom.</i>
</p>
<hr>


LazyOS is a lightweight, cross-platform smart assistant that learns your habits, automates your daily workflows, manages browser clutter, and keeps your system clean — all while respecting your privacy.

## 🎯 Coming Soon

- 🔁 One-click context switching (Work, Chill, Learn, Sleep)
- 🌐 Smart browser tab organizer & launcher
- 📁 Auto-cleanup of old files, unused apps & downloads
- 🧠 Pattern recognition (offline/local ML)
- 🎙️ Offline voice command support (Vosk/Whisper)
- 📊 Local activity dashboard (time in each mode, app usage)
- ⚙️ CLI + GUI interface with floating launcher (DearPyGui)
- Plugin system for devs to create custom workflows
- Cross-device profile sync (optional, encrypted)
- Community-driven mode templates

## 🚀 Getting Started

1. **Installation**  
   Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/YugantM/lazyos.git
   cd lazyos
   pip install -r requirements.txt
   ```

2. **Configuration**  
   Define your modes in `configs/modes.json`. Example:
   ```json
   {
     "work": {
       "apps": ["Safari", "Terminal"],
       "tabs": ["https://github.com", "https://stackoverflow.com"],
       "comment": "Work mode for coding"
     }
   }
   ```

3. **Usage**  
   Run the launcher with:
   ```bash
   python core/launcher.py work
   ```

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) and submit pull requests or report issues on our [Issue Tracker](https://github.com/YugantM/lazyos/issues).

## 🛡️ Philosophy

No cloud. No tracking. Just automation that feels like magic.

---

## 🔗 Project Status

🚧 Currently in early prototyping phase. MVP is CLI + tab launcher + file cleanup system.

---

Made with love by [@yugantm](https://github.com/yugantm)
