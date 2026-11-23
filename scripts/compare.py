
from __future__ import annotations

import json
import sys

from pathlib import Path


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERSIONS_ROOT = PROJECT_ROOT / "versions"

CONTENT_TYPES = {
    "mods": "Mods",
    "resourcepacks": "Resource Packs",
    "shaders": "Shaders",
}

TRACKED_FIELDS = [
    "version",
    "author",
    "type",
    "required",
    "modrinthUrl",
    "curseforgeUrl",
]


# ============================================================
# Terminal output
# ============================================================

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


def color(text, value):
    return f"{value}{text}{Colors.RESET}"


def heading(text):
    print(f"\n{'─' * 65}")
    print(f" {text}")
    print(f"{'─' * 65}")


def pause():
    input("\nPress Enter to continue...")


# ============================================================
# Data loading
# ============================================================

def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        print(
            color(
                f"Invalid JSON in {path}: {error}",
                Colors.RED,
            )
        )
    except OSError as error:
        print(color(f"Could not read {path}: {error}", Colors.RED))

    return None


def discover_versions():
    if not VERSIONS_ROOT.is_dir():
        return []

    return sorted(
        folder.name
        for folder in VERSIONS_ROOT.iterdir()
        if folder.is_dir()
        and any(
            release.is_dir()
            and (release / "metadata.json").is_file()
            for release in folder.iterdir()
        )
    )


def discover_releases(minecraft_version):
    minecraft_path = VERSIONS_ROOT / minecraft_version

    if not minecraft_path.is_dir():
        return []

    return sorted(
        folder.name
        for folder in minecraft_path.iterdir()
        if folder.is_dir()
        and (folder / "metadata.json").is_file()
    )


# ============================================================
# Interactive selection
# ============================================================

def select_option(title, options):
    while True:
        heading(title)

        for index, option in enumerate(options, start=1):
            print(f" [{index}] {option}")

        print("\n [0] Back")

        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            return None

        if choice.isdigit():
            index = int(choice)

            if 1 <= index <= len(options):
                return options[index - 1]

        print(color("\nInvalid selection. Try again.", Colors.YELLOW))


def select_comparison_releases(releases):
    while True:
        heading("SELECT RELEASES")

        print(" Select the older release first.\n")

        for index, release in enumerate(releases, start=1):
            print(f" [{index}] {release}")

        print("\n [0] Back")

        first = input("\nOlder release: ").strip()

        if first == "0":
            return None

        if not first.isdigit() or not 1 <= int(first) <= len(releases):
            print(color("\nInvalid selection.", Colors.YELLOW))
            continue

        older = releases[int(first) - 1]

        newer_options = [
            release for release in releases
            if release != older
        ]

        if not newer_options:
            print(
                color(
                    "\nYou need at least two releases to compare.",
                    Colors.YELLOW,
                )
            )
            return None

        while True:
            heading("SELECT NEWER RELEASE")

            print(f" Older release: {older}\n")

            for index, release in enumerate(newer_options, start=1):
                print(f" [{index}] {release}")

            print("\n [0] Back")

            second = input("\nNewer release: ").strip()

            if second == "0":
                break

            if second.isdigit() and 1 <= int(second) <= len(newer_options):
                newer = newer_options[int(second) - 1]
                return older, newer

            print(color("\nInvalid selection.", Colors.YELLOW))


# ============================================================
# Comparison helpers
# ============================================================

def get_content(metadata, content_type):
    content = metadata.get("content", {})

    if not isinstance(content, dict):
        return []

    entries = content.get(content_type, [])

    if not isinstance(entries, list):
        return []

    return [
        entry for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
        and entry["name"].strip()
    ]


def normalize_name(name):
    return name.strip().casefold()


def build_content_map(entries):
    result = {}

    for entry in entries:
        key = normalize_name(entry["name"])

        if key in result:
            print(
                color(
                    f"Duplicate content name encountered: {entry['name']}",
                    Colors.YELLOW,
                )
            )
            continue

        result[key] = entry

    return result


def compare_content(old_entries, new_entries):
    old_map = build_content_map(old_entries)
    new_map = build_content_map(new_entries)

    old_names = set(old_map)
    new_names = set(new_map)

    added = [
        new_map[name]
        for name in sorted(new_names - old_names)
    ]

    removed = [
        old_map[name]
        for name in sorted(old_names - new_names)
    ]

    updated = []
    unchanged = []

    for name in sorted(old_names & new_names):
        old_entry = old_map[name]
        new_entry = new_map[name]

        changes = []

        for field in TRACKED_FIELDS:
            old_value = old_entry.get(field)
            new_value = new_entry.get(field)

            if old_value != new_value:
                changes.append({
                    "field": field,
                    "old": old_value,
                    "new": new_value,
                })

        if changes:
            updated.append({
                "name": new_entry["name"],
                "changes": changes,
            })
        else:
            unchanged.append(new_entry["name"])

    return {
        "added": added,
        "removed": removed,
        "updated": updated,
        "unchanged": unchanged,
    }


# ============================================================
# Display comparison
# ============================================================

def display_changes(title, changes):
    print(f"\n{Colors.BOLD}{title}{Colors.RESET}")

    if not changes:
        print(color("  None", Colors.GRAY))
        return

    for item in changes:
        print(f"  - {item['name']}")

        for change in item["changes"]:
            old = change["old"]
            new = change["new"]

            print(
                f"      {change['field']}: "
                f"{old!r} -> {new!r}"
            )


def display_content_comparison(title, result):
    heading(title)

    added = result["added"]
    removed = result["removed"]
    updated = result["updated"]
    unchanged = result["unchanged"]

    print(
        f" {color(f'+ {len(added)} Added', Colors.GREEN)}"
        f"   "
        f"{color(f'- {len(removed)} Removed', Colors.RED)}"
        f"   "
        f"{color(f'~ {len(updated)} Updated', Colors.YELLOW)}"
        f"   "
        f"{color(f'= {len(unchanged)} Unchanged', Colors.GRAY)}"
    )

    print(f"\n{color('ADDED', Colors.GREEN)}")

    if added:
        for entry in added:
            print(f"  + {entry['name']}")
    else:
        print(color("  None", Colors.GRAY))

    print(f"\n{color('REMOVED', Colors.RED)}")

    if removed:
        for entry in removed:
            print(f"  - {entry['name']}")
    else:
        print(color("  None", Colors.GRAY))

    display_changes(
        color("UPDATED", Colors.YELLOW),
        updated,
    )

    print(f"\n{color('UNCHANGED', Colors.GRAY)}")

    if unchanged:
        for name in unchanged:
            print(f"  = {name}")
    else:
        print(color("  None", Colors.GRAY))


# ============================================================
# Pack information comparison
# ============================================================

def compare_pack_information(old_metadata, new_metadata):
    heading("PACK INFORMATION")

    old_minecraft = old_metadata.get("minecraft", {})
    new_minecraft = new_metadata.get("minecraft", {})

    old_loader = old_metadata.get("loader", {})
    new_loader = new_metadata.get("loader", {})

    fields = [
        ("Minecraft Version", old_minecraft.get("version"),
         new_minecraft.get("version")),
        ("Release Type", old_minecraft.get("releaseType"),
         new_minecraft.get("releaseType")),
        ("Loader Type", old_loader.get("type"),
         new_loader.get("type")),
        ("Loader Version", old_loader.get("version"),
         new_loader.get("version")),
    ]

    for label, old_value, new_value in fields:
        if old_value != new_value:
            print(
                f" {color('CHANGED', Colors.YELLOW)} "
                f"{label}: {old_value!r} -> {new_value!r}"
            )
        else:
            print(
                f" {color('UNCHANGED', Colors.GRAY)} "
                f"{label}: {old_value!r}"
            )


# ============================================================
# Comparison report
# ============================================================

def run_comparison(minecraft_version, older, newer):
    old_path = (
        VERSIONS_ROOT / minecraft_version / older / "metadata.json"
    )

    new_path = (
        VERSIONS_ROOT / minecraft_version / newer / "metadata.json"
    )

    old_metadata = load_json(old_path)
    new_metadata = load_json(new_path)

    if not isinstance(old_metadata, dict):
        return

    if not isinstance(new_metadata, dict):
        return

    heading("EVERSMOOTH OPTIMIZED - RELEASE COMPARISON")

    print(f" Minecraft Version : {minecraft_version}")
    print(f" Older Release     : {older}")
    print(f" Newer Release     : {newer}")

    compare_pack_information(old_metadata, new_metadata)

    totals = {
        "added": 0,
        "removed": 0,
        "updated": 0,
        "unchanged": 0,
    }

    for content_type, title in CONTENT_TYPES.items():
        result = compare_content(
            get_content(old_metadata, content_type),
            get_content(new_metadata, content_type),
        )

        display_content_comparison(title, result)

        for key in totals:
            totals[key] += len(result[key])

    heading("COMPARISON SUMMARY")

    print(f" Added entries     : {color(str(totals['added']), Colors.GREEN)}")
    print(f" Removed entries   : {color(str(totals['removed']), Colors.RED)}")
    print(f" Updated entries   : {color(str(totals['updated']), Colors.YELLOW)}")
    print(f" Unchanged entries : {color(str(totals['unchanged']), Colors.GRAY)}")

    print("\n" + "=" * 65)
    print(" Comparison completed.")
    print("=" * 65)


# ============================================================
# Main
# ============================================================

def main():
    print("\n" + "=" * 65)
    print("       EverSmooth Optimized - Release Comparator")
    print("=" * 65)

    minecraft_versions = discover_versions()

    if not minecraft_versions:
        print(color("\nNo Minecraft versions found.", Colors.RED))
        return 1

    while True:
        minecraft_version = select_option(
            "SELECT MINECRAFT VERSION",
            minecraft_versions,
        )

        if minecraft_version is None:
            break

        releases = discover_releases(minecraft_version)

        if len(releases) < 2:
            print(
                color(
                    "\nAt least two releases are required for comparison.",
                    Colors.YELLOW,
                )
            )
            pause()
            continue

        selection = select_comparison_releases(releases)

        if selection is None:
            continue

        older, newer = selection

        run_comparison(minecraft_version, older, newer)
        pause()

    print("\nComparator closed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
