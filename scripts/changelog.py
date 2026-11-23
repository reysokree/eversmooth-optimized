
from __future__ import annotations

import json
import sys

from pathlib import Path
from datetime import datetime, timezone


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
    print(f"\n{'─' * 60}")
    print(f" {text}")
    print(f"{'─' * 60}")


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

        print(color("\nInvalid selection.", Colors.YELLOW))


def select_releases(releases):
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
            print(color("\nNo other release available.", Colors.YELLOW))
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
# Content helpers
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

        if key not in result:
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
# Markdown generation helpers
# ============================================================

def escape_markdown(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def format_value(value):
    if value is None:
        return "`not specified`"

    if isinstance(value, bool):
        return "`true`" if value else "`false`"

    return f"`{escape_markdown(value)}`"


def format_entry(entry):
    name = escape_markdown(entry["name"])
    version = entry.get("version")

    if version:
        return f"- **{name}** — `{escape_markdown(version)}`"

    return f"- **{name}**"


def add_content_section(lines, title, result):
    lines.append(f"## {title}")
    lines.append("")

    for key, heading_text in (
        ("added", "### Added"),
        ("removed", "### Removed"),
    ):
        entries = result[key]

        if entries:
            lines.append(heading_text)
            lines.append("")

            for entry in entries:
                lines.append(format_entry(entry))

            lines.append("")

    if result["updated"]:
        lines.append("### Updated")
        lines.append("")

        for item in result["updated"]:
            lines.append(f"- **{escape_markdown(item['name'])}**")

            for change in item["changes"]:
                old = format_value(change["old"])
                new = format_value(change["new"])

                lines.append(
                    f"  - `{change['field']}`: {old} → {new}"
                )

        lines.append("")

    if not any(
        result[key]
        for key in ("added", "removed", "updated")
    ):
        lines.append("No changes.")
        lines.append("")

    return {
        "added": len(result["added"]),
        "removed": len(result["removed"]),
        "updated": len(result["updated"]),
        "unchanged": len(result["unchanged"]),
    }


# ============================================================
# Pack information
# ============================================================

def add_pack_information(lines, old_metadata, new_metadata):
    lines.append("## Pack Information")
    lines.append("")

    old_minecraft = old_metadata.get("minecraft", {})
    new_minecraft = new_metadata.get("minecraft", {})

    old_loader = old_metadata.get("loader", {})
    new_loader = new_metadata.get("loader", {})

    fields = [
        (
            "Minecraft Version",
            old_minecraft.get("version"),
            new_minecraft.get("version"),
        ),
        (
            "Release Type",
            old_minecraft.get("releaseType"),
            new_minecraft.get("releaseType"),
        ),
        (
            "Loader",
            old_loader.get("type"),
            new_loader.get("type"),
        ),
        (
            "Loader Version",
            old_loader.get("version"),
            new_loader.get("version"),
        ),
    ]

    lines.append("| Property | Previous | Current |")
    lines.append("|---|---|---|")

    for label, old_value, new_value in fields:
        lines.append(
            f"| {label} | {format_value(old_value)} "
            f"| {format_value(new_value)} |"
        )

    lines.append("")


# ============================================================
# Full changelog generation
# ============================================================

def generate_changelog(
    minecraft_version,
    older,
    newer,
    old_metadata,
    new_metadata,
):
    lines = [
        f"# EverSmooth Optimized {newer}",
        "",
        f"> Minecraft {minecraft_version}",
        "",
        f"Changes since `{older}`.",
        "",
    ]

    add_pack_information(lines, old_metadata, new_metadata)

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

        counts = add_content_section(lines, title, result)

        for key in totals:
            totals[key] += counts[key]

    lines.extend([
        "## Summary",
        "",
        "| Change | Count |",
        "|---|---:|",
        f"| Added | {totals['added']} |",
        f"| Removed | {totals['removed']} |",
        f"| Updated | {totals['updated']} |",
        f"| Unchanged | {totals['unchanged']} |",
        "",
        "---",
        "",
        f"*Generated automatically by EverSmooth Optimized "
        f"Changelog CLI on "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}.*",
        "",
    ])

    return "\n".join(lines)


# ============================================================
# Main workflow
# ============================================================

def run_changelog(minecraft_version, older, newer):
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

    output_path = (
        VERSIONS_ROOT
        / minecraft_version
        / newer
        / "CHANGELOG.md"
    )

    heading("CHANGELOG PREVIEW")

    print(f" Minecraft : {minecraft_version}")
    print(f" Previous  : {older}")
    print(f" Current   : {newer}")
    print(f" Output    : {output_path.relative_to(PROJECT_ROOT)}")

    if output_path.exists():
        print(
            color(
                "\nA CHANGELOG.md already exists for this release.",
                Colors.YELLOW,
            )
        )

    changelog = generate_changelog(
        minecraft_version,
        older,
        newer,
        old_metadata,
        new_metadata,
    )

    print("\n" + "─" * 60)
    print(changelog)
    print("─" * 60)

    while True:
        choice = input(
            "\nGenerate this changelog? [Y/N]: "
        ).strip().lower()

        if choice in ("y", "yes"):
            break

        if choice in ("n", "no"):
            print(color("\nGeneration cancelled.", Colors.YELLOW))
            return

        print("Enter Y or N.")

    try:
        output_path.write_text(changelog, encoding="utf-8")
    except OSError as error:
        print(color(f"\nCould not write changelog: {error}", Colors.RED))
        return

    print(
        color(
            f"\nChangelog generated successfully!",
            Colors.GREEN,
        )
    )
    print(f"Saved to: {output_path.relative_to(PROJECT_ROOT)}")


# ============================================================
# Application
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("       EverSmooth Optimized - Changelog Generator")
    print("=" * 60)

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
                    "\nAt least two releases are required.",
                    Colors.YELLOW,
                )
            )
            pause()
            continue

        selection = select_releases(releases)

        if selection is None:
            continue

        older, newer = selection

        run_changelog(minecraft_version, older, newer)
        pause()

    print("\nChangelog Generator closed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
