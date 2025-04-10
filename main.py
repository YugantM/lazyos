# main.py
import argparse
import os
from core import launcher  # we will build this soon
from core.cleaner import summarize_old_files

#summarize_old_files(os.path.expanduser("~/Downloads"), days=30)


def main():
    parser = argparse.ArgumentParser(description="LazyOS Mode Launcher")
    parser.add_argument("--mode", required=True, help="Choose mode: work, learn, chill, etc.")
    args = parser.parse_args()

    print(f"🧠 Ayo is setting up '{args.mode}' mode for you...")
    launcher.launch_mode(args.mode)

if __name__ == "__main__":
    main()