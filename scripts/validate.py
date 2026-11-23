
from pathlib import Path
import json
import sys
from urllib.parse import urlparse


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERSIONS_ROOT = PROJECT_ROOT / "versions"

SUPPORTED_SCHEMA_VERSION = 1

CONTENT_TYPES = {
    "mods": [
        "name",
        "author",
        "version",
        "type",
        "required",
        "modrinthUrl",
        "curseforgeUrl",
    ],
    "resourcepacks": [
        "name",
        "author",
        "version",
        "modrinthUrl",
        "curseforgeUrl",
    ],
    "shaders": [
        "name",
        "author",
        "version",
        "modrinthUrl",
        "curseforgeUrl",
    ],
}

PLACEHOLDER_VALUES = {
    "",
    "https://modrinth.com/",
    "https://www.curseforge.com/",
    "https://example.com",
    "https://example.com/",
    "https://placeholder.com",
    "https://placeholder.com/",
}


# ============================================================
# Validation State
# ============================================================

class ValidationReport:
    def __init__(self):
        self.successes = 0
        self.warnings = 0
        self.errors = 0

    def success(self, message):
        self.successes += 1
        print(f"  [OK] {message}")

    def warning(self, message):
        self.warnings += 1
        print(f"  [WARNING] {message}")

    def error(self, message):
        self.errors += 1
        print(f"  [ERROR] {message}")


# ============================================================
# Terminal UI
# ============================================================

def print_header():
    print("\n" + "=" * 58)
    print("               EverSmooth Optimized")
    print("                 Metadata Validator")
    print("=" * 58)


def wait_for_enter():
    input("\nPress Enter to continue...")


# ============================================================
# Version Discovery
# ============================================================

def get_available_versions():
    if not VERSIONS_ROOT.is_dir():
        return []

    return sorted(
        folder.name
        for folder in VERSIONS_ROOT.iterdir()
        if folder.is_dir()
    )


def get_available_releases(minecraft_version):
    version_directory = VERSIONS_ROOT / minecraft_version

    if not version_directory.is_dir():
        return []

    return sorted(
        folder.name
        for folder in version_directory.iterdir()
        if folder.is_dir()
        and (folder / "metadata.json").is_file()
    )


# ============================================================
# Selection
# ============================================================

def select_item(items, title, item_label):
    print(f"\n{title}\n")

    for index, item in enumerate(items, start=1):
        print(f"  [{index}] {item}")

    print("\n  [0] Back")

    while True:
        choice = input("\nEnter choice: ").strip()

        if choice == "0":
            return None

        if choice.isdigit():
            index = int(choice)

            if 1 <= index <= len(items):
                return items[index - 1]

        print(f"\n[ERROR] Invalid {item_label} selection.")


# ============================================================
# Basic Validation
# ============================================================

def validate_required_fields(data, fields, location, report):
    for field in fields:
        if field not in data:
            report.error(f"{location}: Missing field '{field}'.")
            continue

        value = data[field]

        if isinstance(value, str) and not value.strip():
            report.error(f"{location}: '{field}' cannot be empty.")

        elif value is None:
            report.error(f"{location}: '{field}' cannot be null.")


def validate_string_fields(entry, fields, location, report):
    for field in fields:
        if field not in entry:
            report.error(f"{location}: Missing field '{field}'.")
            continue

        value = entry[field]

        if not isinstance(value, str):
            report.error(f"{location}: '{field}' must be a string.")

        elif not value.strip():
            report.error(f"{location}: '{field}' cannot be empty.")


# ============================================================
# URL Validation
# ============================================================

def validate_url(url, field, location, report):
    if not isinstance(url, str):
        report.error(f"{location}: '{field}' must be a string.")
        return

    if url.strip() in PLACEHOLDER_VALUES:
        report.warning(
            f"{location}: '{field}' contains a placeholder URL."
        )
        return

    parsed = urlparse(url)

    if (
        parsed.scheme not in ("http", "https")
        or not parsed.netloc
    ):
        report.error(
            f"{location}: '{field}' is not a valid HTTP(S) URL."
        )


# ============================================================
# Content Validation
# ============================================================

def validate_content_category(category, entries, report):
    location = f"content.{category}"

    if not isinstance(entries, list):
        report.error(f"'{location}' must be an array.")
        return

    report.success(
        f"'{location}' contains {len(entries)} entr(y/ies)."
    )

    required_fields = CONTENT_TYPES[category]
    seen_names = set()

    for index, entry in enumerate(entries):
        entry_location = f"{location}[{index}]"

        if not isinstance(entry, dict):
            report.error(
                f"{entry_location} must be an object."
            )
            continue

        validate_required_fields(
            entry,
            required_fields,
            entry_location,
            report,
        )

        string_fields = [
            field for field in required_fields
            if field != "required"
        ]

        validate_string_fields(
            entry,
            string_fields,
            entry_location,
            report,
        )

        name = entry.get("name")

        if isinstance(name, str) and name.strip():
            normalized_name = name.strip().casefold()

            if normalized_name in seen_names:
                report.error(
                    f"{entry_location}: Duplicate content name "
                    f"'{name}'."
                )
            else:
                seen_names.add(normalized_name)

        if category == "mods":
            if "required" in entry:
                if not isinstance(entry["required"], bool):
                    report.error(
                        f"{entry_location}: 'required' must be "
                        "a boolean."
                    )

            if "type" in entry and entry["type"] != "mod":
                report.warning(
                    f"{entry_location}: Unexpected mod type "
                    f"'{entry['type']}'."
                )

        for field in ("modrinthUrl", "curseforgeUrl"):
            if field in entry:
                validate_url(
                    entry[field],
                    field,
                    entry_location,
                    report,
                )


# ============================================================
# Metadata Validation
# ============================================================

def validate_metadata(metadata_file):
    report = ValidationReport()

    print(f"\n[VALIDATING] {metadata_file.relative_to(PROJECT_ROOT)}")
    print("-" * 58)

    try:
        with metadata_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        report.error(
            f"Invalid JSON at line {error.lineno}, "
            f"column {error.colno}: {error.msg}"
        )
        return report

    except OSError as error:
        report.error(f"Could not read file: {error}")
        return report

    if not isinstance(data, dict):
        report.error("Metadata root must be a JSON object.")
        return report

    report.success("Valid JSON syntax.")

    top_level_fields = [
        "schemaVersion",
        "modpackVersion",
        "minecraft",
        "loader",
        "content",
    ]

    validate_required_fields(
        data,
        top_level_fields,
        "metadata",
        report,
    )

    # Schema version
    schema_version = data.get("schemaVersion")

    if isinstance(schema_version, int) and not isinstance(
        schema_version, bool
    ):
        if schema_version == SUPPORTED_SCHEMA_VERSION:
            report.success(
                f"Schema version {schema_version} is supported."
            )
        else:
            report.error(
                f"Unsupported schema version: {schema_version}."
            )
    else:
        report.error("'schemaVersion' must be an integer.")

    # Release version
    release_folder = metadata_file.parent.name
    modpack_version = data.get("modpackVersion")

    if isinstance(modpack_version, str):
        if modpack_version == release_folder:
            report.success("Release version matches folder name.")
        else:
            report.error(
                f"Release version '{modpack_version}' does not "
                f"match folder '{release_folder}'."
            )

    # Minecraft information
    minecraft = data.get("minecraft")

    if isinstance(minecraft, dict):
        validate_required_fields(
            minecraft,
            ["version", "releaseType"],
            "minecraft",
            report,
        )

        validate_string_fields(
            minecraft,
            ["version", "releaseType"],
            "minecraft",
            report,
        )

        folder_version = metadata_file.parent.parent.name
        minecraft_version = minecraft.get("version")

        if isinstance(minecraft_version, str):
            if minecraft_version == folder_version:
                report.success(
                    "Minecraft version matches folder name."
                )
            else:
                report.error(
                    f"Minecraft version '{minecraft_version}' "
                    f"does not match folder '{folder_version}'."
                )

    elif minecraft is not None:
        report.error("'minecraft' must be an object.")

    # Loader information
    loader = data.get("loader")

    if isinstance(loader, dict):
        validate_required_fields(
            loader,
            ["type", "version"],
            "loader",
            report,
        )

        validate_string_fields(
            loader,
            ["type", "version"],
            "loader",
            report,
        )

        loader_type = loader.get("type")

        if isinstance(loader_type, str):
            if loader_type.lower() not in {
                "fabric",
                "forge",
                "quilt",
                "neoforge",
            }:
                report.warning(
                    f"Unrecognized loader type: '{loader_type}'."
                )

    elif loader is not None:
        report.error("'loader' must be an object.")

    # Content
    content = data.get("content")

    if isinstance(content, dict):
        for category in CONTENT_TYPES:
            if category not in content:
                report.error(
                    f"Missing content category '{category}'."
                )
                continue

            validate_content_category(
                category,
                content[category],
                report,
            )

    elif content is not None:
        report.error("'content' must be an object.")

    return report


# ============================================================
# Validation Summary
# ============================================================

def print_summary(report):
    print("\n" + "=" * 58)
    print("                  VALIDATION SUMMARY")
    print("=" * 58)

    print(f"Successful: {report.successes}")
    print(f"Warnings:   {report.warnings}")
    print(f"Errors:     {report.errors}")

    print("=" * 58)

    if report.errors:
        print("\n[FAILED] Metadata validation found errors.")
    elif report.warnings:
        print("\n[PASSED WITH WARNINGS] Review the warnings above.")
    else:
        print("\n[PASSED] Metadata is valid.")


# ============================================================
# Main
# ============================================================

def main():
    while True:
        print_header()

        versions = get_available_versions()

        if not versions:
            print("\n[ERROR] No Minecraft versions found.")
            print(f"Expected location: {VERSIONS_ROOT}")
            return 1

        version = select_item(
            versions,
            "Select Minecraft Version:",
            "version",
        )

        if version is None:
            return 0

        while True:
            releases = get_available_releases(version)

            print_header()

            if not releases:
                print(f"\n[ERROR] No releases found for {version}.")
                wait_for_enter()
                break

            release = select_item(
                releases,
                f"Select Release for Minecraft {version}:",
                "release",
            )

            if release is None:
                break

            metadata_file = (
                VERSIONS_ROOT
                / version
                / release
                / "metadata.json"
            )

            report = validate_metadata(metadata_file)
            print_summary(report)

            wait_for_enter()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nValidation cancelled.")
        sys.exit(130)
