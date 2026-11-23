
from pathlib import Path
import subprocess
import sys


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"

PROJECT_NAME = "EverSmooth Optimized"
MANAGER_NAME = "PROJECT MANAGER"

TOOLS = {
    "H": {
            "name": "Help",
            "script": "help.py",
        },
    "1": {
        "name": "Project Doctor",
        "script": "doctor.py",
    },
    "2": {
        "name": "Metadata Explorer",
        "script": "metadata.py",
    },
    "3": {
        "name": "Release Comparison",
        "script": "compare.py",
    },
    "4": {
        "name": "Changelog Generator",
        "script": "changelog.py",
    },
    "5": {
        "name": "Pack Exporter",
        "script": "export.py",
    },
    "6": {
        "name": "Local Data Cleaner",
        "script": "clean.py",
    },
    "7": {
        "name": "Metadata Validator",
        "script": "validate.py",
    },
    "8": {
        "name": "Packwiz Metadata Sync",
        "script": "sync.py",
    },
    "9": {
        "name": "Release Report Generator",
        "script": "report.py",
    },
    "10": {
        "name": "Project Backup",
        "script": "backup.py",
    },
}

EXIT_OPTION = "0"


# ============================================================
# Terminal UI
# ============================================================

def print_header():
    print("\n" + "=" * 60)
    print(f"              {PROJECT_NAME}")
    print(f"                 {MANAGER_NAME}")
    print("=" * 60)


def print_menu():
    sections = {
        "PROJECT TOOLS": ["1", "2", "7", "8"],
        "RELEASE TOOLS": ["3", "4", "5", "9"],
        "MAINTENANCE TOOLS": ["6", "10"],
    }

    print("\nAvailable Tools:\n")

    for section, options in sections.items():
        print(f"  {section}")
        print("  " + "-" * 38)

        for key in options:
            tool = TOOLS[key]
            print(f"  [{key:>2}] {tool['name']}")

        print()

    print(f"  [{EXIT_OPTION}] Exit")


def wait_for_enter():
    input("\nPress Enter to return to the main menu...")


# ============================================================
# Tool Launcher
# ============================================================

def launch_tool(choice):
    tool = TOOLS[choice]
    name = tool["name"]
    script = SCRIPTS_ROOT / tool["script"]

    print(f"\n[LAUNCHING] {name}")
    print("-" * 60)

    if not script.is_file():
        print(f"[ERROR] Script not found: {script}")
        wait_for_enter()
        return

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=PROJECT_ROOT,
            check=False,
        )

        print("\n" + "-" * 60)

        if result.returncode == 0:
            print(f"[SUCCESS] {name} completed successfully.")

        elif result.returncode == 130:
            print(f"[CANCELLED] {name} was interrupted.")

        else:
            print(
                f"[FAILED] {name} exited with code "
                f"{result.returncode}."
            )

    except OSError as error:
        print(f"\n[ERROR] Could not launch {name}: {error}")

    wait_for_enter()


# ============================================================
# Main
# ============================================================

def main():
    while True:
        print_header()
        print_menu()

        choice = input("\nSelect an option: ").strip()

        if choice == EXIT_OPTION:
            print(f"\nExiting {PROJECT_NAME} Project Manager.")
            return 0

        if choice in TOOLS:
            launch_tool(choice)
        else:
            print("\n[ERROR] Invalid selection.")
            wait_for_enter()


if __name__ == "__main__":
    try:
        sys.exit(main())

    except KeyboardInterrupt:
        print("\n\nProject Manager closed.")
        sys.exit(130)
