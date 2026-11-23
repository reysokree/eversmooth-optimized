
# ============================================================
# EverSmooth Optimized - Help Center
# ============================================================

PROJECT_NAME = "EverSmooth Optimized"

COMMANDS = {
    "1": {
        "name": "Project Doctor",
        "file": "doctor.py",
        "category": "PROJECT TOOLS",
        "purpose": "Performs a health check of the entire project.",
        "details": [
            "Checks the project directory structure.",
            "Checks release metadata and required fields.",
            "Verifies Packwiz configuration and index files.",
            "Checks indexed files and SHA-256 hashes.",
            "Detects missing files, duplicates, and configuration issues.",
        ],
        "usage": "python scripts/doctor.py",
        "modifies": "No. Performs read-only checks.",
        "when": "Use this to check whether your project is healthy.",
    },
    "2": {
        "name": "Metadata Explorer",
        "file": "metadata.py",
        "category": "PROJECT TOOLS",
        "purpose": "Explore and export release metadata.",
        "details": [
            "Selects a Minecraft version and release.",
            "Displays mod information.",
            "Displays resource pack information.",
            "Displays shader information.",
            "Exports metadata into a Markdown file.",
        ],
        "usage": "python scripts/metadata.py",
        "modifies": "Creates generated metadata Markdown exports.",
        "when": "Use this to inspect or document included content.",
    },
    "3": {
        "name": "Release Comparison",
        "file": "compare.py",
        "category": "RELEASE TOOLS",
        "purpose": "Compares two releases of EverSmooth Optimized.",
        "details": [
            "Detects newly added content.",
            "Detects removed content.",
            "Detects updated content and metadata.",
            "Compares mods, resource packs, and shaders.",
            "Shows pack information changes.",
        ],
        "usage": "python scripts/compare.py",
        "modifies": "No. Performs read-only comparisons.",
        "when": "Use this before preparing a new release.",
    },
    "4": {
        "name": "Changelog Generator",
        "file": "changelog.py",
        "category": "RELEASE TOOLS",
        "purpose": "Generates a changelog between two releases.",
        "details": [
            "Compares an older release with a newer release.",
            "Lists added content.",
            "Lists removed content.",
            "Lists updated content.",
            "Includes release summary and content statistics.",
            "Saves a release-specific CHANGELOG.md.",
        ],
        "usage": "python scripts/changelog.py",
        "modifies": "Creates or overwrites a generated release changelog after confirmation.",
        "when": "Use this when documenting changes in a new release.",
    },
    "5": {
        "name": "Pack Exporter",
        "file": "export.py",
        "category": "RELEASE TOOLS",
        "purpose": "Exports Packwiz modpacks for supported platforms.",
        "details": [
            "Detects available Minecraft versions.",
            "Reads Packwiz configuration.",
            "Builds the official release archive name.",
            "Supports Modrinth export.",
            "Supports CurseForge export.",
            "Can export to both platforms.",
        ],
        "usage": "python scripts/export.py",
        "modifies": "Creates exported modpack archives.",
        "when": "Use this to prepare platform-specific modpack releases.",
    },
    "6": {
        "name": "Local Data Cleaner",
        "file": "clean.py",
        "category": "MAINTENANCE TOOLS",
        "purpose": "Removes selected generated project directories.",
        "details": [
            "Cleans the generated releases directory.",
            "Cleans the generated metadata-exports directory.",
            "Requests confirmation before deletion.",
            "Does not delete source Packwiz files or release metadata.",
        ],
        "usage": "python scripts/clean.py",
        "modifies": "Yes. Deletes selected generated directories.",
        "when": "Use this to remove generated files and free disk space.",
    },
    "7": {
        "name": "Metadata Validator",
        "file": "validate.py",
        "category": "PROJECT TOOLS",
        "purpose": "Validates release metadata JSON files.",
        "details": [
            "Checks JSON syntax.",
            "Checks schema version.",
            "Checks Minecraft and release versions.",
            "Checks loader information.",
            "Checks mods, resource packs, and shaders.",
            "Detects missing fields, duplicates, and invalid URLs.",
        ],
        "usage": "python scripts/validate.py",
        "modifies": "No. Performs read-only validation.",
        "when": "Use this after editing metadata.json.",
    },
    "8": {
        "name": "Packwiz Metadata Sync",
        "file": "sync.py",
        "category": "PROJECT TOOLS",
        "purpose": "Checks synchronization between Packwiz and release metadata.",
        "details": [
            "Reads Packwiz index entries.",
            "Reads Packwiz metafiles.",
            "Compares mod names with metadata.",
            "Compares resource pack names with metadata.",
            "Checks shader metadata entries.",
            "Reports missing and unclassified entries.",
        ],
        "usage": "python scripts/sync.py",
        "modifies": "No. Performs read-only synchronization checks.",
        "when": "Use this to check whether Packwiz content matches metadata.json.",
    },
    "9": {
        "name": "Release Report Generator",
        "file": "report.py",
        "category": "RELEASE TOOLS",
        "purpose": "Generates a detailed Markdown report for a release.",
        "details": [
            "Summarizes Minecraft and Fabric versions.",
            "Counts mods, resource packs, and shaders.",
            "Counts required and optional mods.",
            "Lists content and project links.",
            "Includes Packwiz synchronization results.",
            "Reports metadata warnings.",
        ],
        "usage": "python scripts/report.py",
        "modifies": "Creates a generated release report.",
        "when": "Use this to create a detailed release overview.",
    },
    "10": {
        "name": "Project Backup",
        "file": "backup.py",
        "category": "MAINTENANCE TOOLS",
        "purpose": "Creates a ZIP backup of the entire project.",
        "details": [
            "Includes project files and folders.",
            "Includes hidden files and Git data.",
            "Includes generated directories and previous backups.",
            "Uses timestamped ZIP archive names.",
            "Verifies archive integrity after creation.",
            "Requests confirmation before starting.",
        ],
        "usage": "python scripts/backup.py",
        "modifies": "Creates a backup archive inside the backups directory.",
        "when": "Use this before major changes or as a project backup.",
    },
    "11": {
        "name": "Project Manager",
        "file": "menu.py",
        "category": "PROJECT MANAGEMENT",
        "purpose": "Provides a central menu to launch project utilities.",
        "details": [
            "Displays available project tools.",
            "Launches scripts using the current Python interpreter.",
            "Returns to the main menu after execution.",
            "Reports successful, cancelled, and failed executions.",
        ],
        "usage": "python scripts/menu.py",
        "modifies": "Depends on the selected utility.",
        "when": "Use this to access project utilities from one menu.",
    },
}


# ============================================================
# Terminal UI
# ============================================================

def line():
    print("=" * 68)


def print_header():
    print("\n")
    line()
    print(f"                 {PROJECT_NAME}")
    print("                       HELP CENTER")
    line()


def print_command_list():
    categories = [
        "PROJECT TOOLS",
        "RELEASE TOOLS",
        "MAINTENANCE TOOLS",
        "PROJECT MANAGEMENT",
    ]

    for category in categories:
        print(f"\n  {category}")
        print("  " + "-" * 48)

        for key, command in COMMANDS.items():
            if command["category"] == category:
                print(f"  [{key:>2}] {command['name']}")


def show_command(key):
    command = COMMANDS[key]

    print("\n")
    line()
    print(f"  {command['name'].upper()}")
    line()

    print(f"\n  File: {command['file']}")
    print(f"  Category: {command['category']}")

    print("\n  PURPOSE")
    print(f"  {command['purpose']}")

    print("\n  WHAT IT DOES")

    for detail in command["details"]:
        print(f"  - {detail}")

    print("\n  HOW TO RUN")
    print(f"  {command['usage']}")

    print("\n  FILE OPERATIONS")
    print(f"  {command['modifies']}")

    print("\n  WHEN TO USE")
    print(f"  {command['when']}")

    line()


def wait_for_enter():
    input("\nPress Enter to continue...")


# ============================================================
# Main
# ============================================================

def main():
    while True:
        print_header()
        print_command_list()

        print("\n")
        line()
        print("  [0] Back / Exit")
        line()

        choice = input("\nSelect a command to learn about: ").strip()

        if choice == "0":
            print("\nLeaving Help Center.")
            return 0

        if choice in COMMANDS:
            show_command(choice)
            wait_for_enter()
        else:
            print("\n[ERROR] Invalid selection.")
            wait_for_enter()


if __name__ == "__main__":
    try:
        import sys
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nHelp Center closed.")
        sys.exit(130)
