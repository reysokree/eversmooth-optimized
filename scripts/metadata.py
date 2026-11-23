
from pathlib import Path
import json
import re
import sys


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VERSIONS_ROOT = PROJECT_ROOT / "versions"
EXPORT_ROOT = PROJECT_ROOT / "metadata-exports"

APP_NAME = "EverSmooth Optimized"
LINE = "=" * 58


# ============================================================
# Terminal UI
# ============================================================

def clear_screen():
    print("\033[2J\033[H", end="")


def header():
    print(LINE)
    print(f"                 {APP_NAME}")
    print("                  METADATA EXPLORER")
    print(LINE)


def section(title):
    print()
    print(LINE)
    print(f"  {title}")
    print(LINE)


def pause():
    input("\nPress Enter to continue...")


def error(message):
    print(f"\n[ERROR] {message}")


def success(message):
    print(f"\n[OK] {message}")


def exit_application():
    print("\nThank you for using EverSmooth Optimized!")
    sys.exit(0)


def get_choice(prompt, valid_choices):
    """Get a selection. B goes back; exit is handled only in Explorer."""
    while True:
        choice = input(f"\n{prompt} ").strip().lower()

        if choice == "b":
            return "b"

        if choice in valid_choices:
            return choice

        print("[ERROR] Invalid selection. Try again.")


# ============================================================
# Version Detection
# ============================================================

def version_sort_key(version):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", version)
    ]


def get_minecraft_versions():
    if not VERSIONS_ROOT.is_dir():
        return []

    versions = []

    for folder in VERSIONS_ROOT.iterdir():
        if not folder.is_dir():
            continue

        releases = [
            release
            for release in folder.iterdir()
            if release.is_dir()
            and (release / "metadata.json").is_file()
        ]

        if releases:
            versions.append(folder.name)

    return sorted(versions, key=version_sort_key)


def get_releases(minecraft_version):
    version_directory = VERSIONS_ROOT / minecraft_version

    if not version_directory.is_dir():
        return []

    releases = [
        folder.name
        for folder in version_directory.iterdir()
        if folder.is_dir()
        and (folder / "metadata.json").is_file()
    ]

    return sorted(releases, key=version_sort_key)


# ============================================================
# Metadata Loading
# ============================================================

def load_metadata(minecraft_version, release_version):
    metadata_file = (
        VERSIONS_ROOT
        / minecraft_version
        / release_version
        / "metadata.json"
    )

    try:
        with metadata_file.open("r", encoding="utf-8") as file:
            metadata = json.load(file)

        if not isinstance(metadata, dict):
            raise ValueError("Metadata must contain a JSON object.")

        return metadata

    except FileNotFoundError:
        error(f"Metadata file not found: {metadata_file}")

    except json.JSONDecodeError as exc:
        error(f"Invalid JSON: {exc}")

    except (OSError, ValueError) as exc:
        error(f"Could not load metadata: {exc}")

    return None


# ============================================================
# Content Helpers
# ============================================================

def get_content(metadata, content_type):
    content = metadata.get("content", {})

    if not isinstance(content, dict):
        return []

    items = content.get(content_type, [])

    if not isinstance(items, list):
        return []

    return [
        item for item in items
        if isinstance(item, dict)
    ]


def get_value(item, key, default="Unknown"):
    value = item.get(key, default)

    if value is None or value == "":
        return default

    return str(value)


def get_project_links(item):
    links = []

    for platform, key in (
        ("Modrinth", "modrinthUrl"),
        ("CurseForge", "curseforgeUrl"),
    ):
        url = item.get(key)

        if isinstance(url, str) and url.strip():
            links.append((platform, url.strip()))

    return links


def print_content_list(items, content_type):
    if not items:
        print(f"\nThis release does not contain any {content_type}.")
        return

    print(f"\nTotal {content_type}: {len(items)}\n")

    for index, item in enumerate(items, start=1):
        print(f"  [{index:02}] {get_value(item, 'name')}")
        print(f"       Author  : {get_value(item, 'author')}")
        print(f"       Version : {get_value(item, 'version')}")

        if content_type == "mods":
            required = item.get("required", False)
            print(f"       Required: {'Yes' if required else 'No'}")

        for platform, url in get_project_links(item):
            print(f"       {platform:<10}: {url}")

        print()


# ============================================================
# Pack Information
# ============================================================

def show_pack_information(metadata):
    minecraft = metadata.get("minecraft", {})
    loader = metadata.get("loader", {})

    if not isinstance(minecraft, dict):
        minecraft = {}

    if not isinstance(loader, dict):
        loader = {}

    mods = get_content(metadata, "mods")
    resourcepacks = get_content(metadata, "resourcepacks")
    shaders = get_content(metadata, "shaders")

    section("PACK INFORMATION")

    print(f"\n  Pack Version  : {get_value(metadata, 'modpackVersion')}")
    print(f"  Schema Version: {get_value(metadata, 'schemaVersion')}")
    print(f"  Minecraft     : {get_value(minecraft, 'version')}")
    print(f"  Release Type  : {get_value(minecraft, 'releaseType')}")
    print(f"  Loader        : {get_value(loader, 'type').title()}")
    print(f"  Loader Version: {get_value(loader, 'version')}")

    section("CONTENT STATISTICS")

    print(f"\n  Mods          : {len(mods)}")
    print(f"  Resource Packs: {len(resourcepacks)}")
    print(f"  Shaders       : {len(shaders)}")
    print(f"  Total Content : {len(mods) + len(resourcepacks) + len(shaders)}")


# ============================================================
# Read Individual Content
# ============================================================

def read_content(metadata, content_type, title):
    while True:
        clear_screen()
        header()
        section(title)

        items = get_content(metadata, content_type)

        if content_type == "shaders" and not items:
            print("\nThis release does not contain any shaders.")
        else:
            print_content_list(items, content_type)

        print("\n[B] Back")

        choice = input("\nChoose an option: ").strip().lower()

        if choice == "b":
            return

        print("\nPlease enter B to go back.")
        pause()


# ============================================================
# Read All Metadata
# ============================================================

def read_all_metadata(metadata):
    clear_screen()
    header()

    show_pack_information(metadata)

    section("MODS")
    print_content_list(get_content(metadata, "mods"), "mods")

    section("RESOURCE PACKS")
    print_content_list(
        get_content(metadata, "resourcepacks"),
        "resource packs",
    )

    section("SHADERS")
    print_content_list(
        get_content(metadata, "shaders"),
        "shaders",
    )

    print("\n" + LINE)
    print("                  END OF METADATA")
    print(LINE)

    pause()


# ============================================================
# Markdown Export Helpers
# ============================================================

def markdown_escape(value):
    """Escape basic Markdown table characters."""
    return str(value).replace("|", r"\|").replace("\n", " ")


def markdown_content_section(title, items, content_type):
    lines = [f"## {title}", ""]

    if not items:
        lines.append(
            f"This release does not contain any {content_type}."
        )
        lines.append("")
        return lines

    lines.extend([
        f"Total: **{len(items)}**",
        "",
        "| # | Name | Author | Version |",
        "|---:|---|---|---|",
    ])

    for index, item in enumerate(items, start=1):
        name = markdown_escape(get_value(item, "name"))
        author = markdown_escape(get_value(item, "author"))
        version = markdown_escape(get_value(item, "version"))

        lines.append(
            f"| {index} | {name} | {author} | {version} |"
        )

        if content_type == "mods":
            required = "Yes" if item.get("required", False) else "No"
            lines.append(
                f"| | **Required:** {required} | | |"
            )

        links = get_project_links(item)

        for platform, url in links:
            lines.append(
                f"| | [{platform}]({url}) | | |"
            )

    lines.append("")
    return lines


def generate_markdown(metadata, minecraft_version, release_version):
    minecraft = metadata.get("minecraft", {})
    loader = metadata.get("loader", {})

    if not isinstance(minecraft, dict):
        minecraft = {}

    if not isinstance(loader, dict):
        loader = {}

    mods = get_content(metadata, "mods")
    resourcepacks = get_content(metadata, "resourcepacks")
    shaders = get_content(metadata, "shaders")

    lines = [
        f"# {APP_NAME}",
        "",
        "## Release Metadata",
        "",
        f"- **Minecraft Version:** {minecraft_version}",
        f"- **Release:** {release_version}",
        f"- **Pack Version:** {get_value(metadata, 'modpackVersion')}",
        f"- **Release Type:** {get_value(minecraft, 'releaseType')}",
        f"- **Loader:** {get_value(loader, 'type').title()}",
        f"- **Loader Version:** {get_value(loader, 'version')}",
        f"- **Schema Version:** {get_value(metadata, 'schemaVersion')}",
        "",
        "## Content Summary",
        "",
        f"- Mods: {len(mods)}",
        f"- Resource Packs: {len(resourcepacks)}",
        f"- Shaders: {len(shaders)}",
        f"- Total Content: {len(mods) + len(resourcepacks) + len(shaders)}",
        "",
    ]

    lines.extend(
        markdown_content_section("Mods", mods, "mods")
    )

    lines.extend(
        markdown_content_section(
            "Resource Packs",
            resourcepacks,
            "resource packs",
        )
    )

    lines.extend(
        markdown_content_section("Shaders", shaders, "shaders")
    )

    lines.extend([
        "---",
        "",
        "*Generated by EverSmooth Optimized Metadata Explorer.*",
        "",
    ])

    return "\n".join(lines)


# ============================================================
# Markdown Export
# ============================================================

def export_markdown(metadata, minecraft_version, release_version):
    output_directory = (
        EXPORT_ROOT
        / minecraft_version
        / release_version
    )

    output_file = output_directory / "metadata.md"

    try:
        output_directory.mkdir(parents=True, exist_ok=True)

        markdown = generate_markdown(
            metadata,
            minecraft_version,
            release_version,
        )

        output_file.write_text(markdown, encoding="utf-8")

        success("Markdown export completed!")
        print(f"\nFile: {output_file}")

    except OSError as exc:
        error(f"Could not export Markdown: {exc}")

    pause()


# ============================================================
# Content Explorer
# ============================================================

def content_menu(metadata, minecraft_version, release_version):
    while True:
        clear_screen()
        header()

        print(f"\n  Minecraft: {minecraft_version}")
        print(f"  Release  : {release_version}")

        section("CONTENT EXPLORER")

        print("\n  [1] Read Mods")
        print("  [2] Read Resource Packs")
        print("  [3] Read Shaders")
        print("  [4] Pack Information")
        print("  [5] Read All Metadata")
        print("  [6] Export Metadata to Markdown")
        print("\n  [0] Exit")

        choice = get_choice(
            "Choose an option:",
            ["0", "1", "2", "3", "4", "5", "6"],
        )

        if choice == "0":
            exit_application()

        elif choice == "1":
            read_content(metadata, "mods", "MODS")

        elif choice == "2":
            read_content(
                metadata,
                "resourcepacks",
                "RESOURCE PACKS",
            )

        elif choice == "3":
            read_content(metadata, "shaders", "SHADERS")

        elif choice == "4":
            clear_screen()
            header()
            show_pack_information(metadata)
            pause()

        elif choice == "5":
            read_all_metadata(metadata)

        elif choice == "6":
            export_markdown(
                metadata,
                minecraft_version,
                release_version,
            )


# ============================================================
# Release Selection
# ============================================================

def release_menu(minecraft_version):
    releases = get_releases(minecraft_version)

    if not releases:
        error("No releases found for this Minecraft version.")
        pause()
        return

    while True:
        clear_screen()
        header()
        section(f"MINECRAFT {minecraft_version} - RELEASES")

        for index, release in enumerate(releases, start=1):
            print(f"  [{index}] {release}")

        print("\n  [B] Back")

        choices = [
            str(index)
            for index in range(1, len(releases) + 1)
        ]

        choice = get_choice("Select a release:", choices)

        if choice == "b":
            return

        release_version = releases[int(choice) - 1]

        metadata = load_metadata(
            minecraft_version,
            release_version,
        )

        if metadata is None:
            pause()
            continue

        content_menu(
            metadata,
            minecraft_version,
            release_version,
        )


# ============================================================
# Minecraft Version Selection
# ============================================================

def main_menu():
    versions = get_minecraft_versions()

    if not versions:
        error("No Minecraft versions with release metadata were found.")
        print(f"\nExpected directory: {VERSIONS_ROOT}")
        return 1

    while True:
        clear_screen()
        header()
        section("SELECT MINECRAFT VERSION")

        for index, version in enumerate(versions, start=1):
            print(f"  [{index}] Minecraft {version}")

        choices = [
            str(index)
            for index in range(1, len(versions) + 1)
        ]

        choice = get_choice("Choose a Minecraft version:", choices)

        if choice == "b":
            continue

        release_menu(versions[int(choice) - 1])


# ============================================================
# Entry Point
# ============================================================

def main():
    try:
        return main_menu()

    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
