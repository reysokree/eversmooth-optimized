
from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib

from pathlib import Path
from urllib.parse import urlparse


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_ROOT_FILES = [
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "modpack-info.json",
]

REQUIRED_DIRECTORIES = [
    ".github",
    "assets",
    "content",
    "packwiz",
    "platforms",
    "scripts",
    "versions",
]

CONTENT_TYPES = {
    "mods": {
        "required_fields": [
            "name", "author", "version", "type", "required",
            "modrinthUrl", "curseforgeUrl",
        ],
    },
    "resourcepacks": {
        "required_fields": [
            "name", "author", "version",
            "modrinthUrl", "curseforgeUrl",
        ],
    },
    "shaders": {
        "required_fields": [
            "name", "author", "version",
            "modrinthUrl", "curseforgeUrl",
        ],
    },
}


# ============================================================
# Terminal output
# ============================================================

class Doctor:
    def __init__(self):
        self.errors = 0
        self.warnings = 0
        self.successes = 0

    def ok(self, message):
        self.successes += 1
        print(f"  [OK]      {message}")

    def warning(self, message):
        self.warnings += 1
        print(f"  [WARNING] {message}")

    def error(self, message):
        self.errors += 1
        print(f"  [ERROR]   {message}")

    def section(self, title):
        print(f"\n{'─' * 60}")
        print(f" {title}")
        print(f"{'─' * 60}")


doctor = Doctor()


# ============================================================
# Helpers
# ============================================================

def relative(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        doctor.error(
            f"Invalid JSON in {relative(path)} "
            f"(line {error.lineno}, column {error.colno})"
        )
    except OSError as error:
        doctor.error(f"Could not read {relative(path)}: {error}")

    return None


def load_toml(path: Path):
    try:
        with path.open("rb") as file:
            return tomllib.load(file)
    except tomllib.TOMLDecodeError as error:
        doctor.error(f"Invalid TOML in {relative(path)}: {error}")
    except OSError as error:
        doctor.error(f"Could not read {relative(path)}: {error}")

    return None


def is_valid_url(value):
    if not isinstance(value, str):
        return False

    parsed = urlparse(value)

    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
    )


def is_placeholder_url(value):
    return (
        isinstance(value, str)
        and any(
            placeholder in value.lower()
            for placeholder in (
                "example-mod",
                "example.com",
                "your-project",
                "placeholder",
            )
        )
    )


def check_required_fields(data, fields, location):
    for field in fields:
        if field not in data:
            doctor.error(f"{location}: missing field '{field}'")
        elif data[field] is None or data[field] == "":
            doctor.error(f"{location}: empty field '{field}'")


def parse_pack_version(version):
    return isinstance(version, str) and bool(
        re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version)
    )


# ============================================================
# Root checks
# ============================================================

def check_root():
    doctor.section("PROJECT STRUCTURE")

    for filename in REQUIRED_ROOT_FILES:
        path = PROJECT_ROOT / filename

        if path.is_file():
            doctor.ok(f"Found {filename}")
        else:
            doctor.warning(f"Missing root file: {filename}")

    for directory in REQUIRED_DIRECTORIES:
        path = PROJECT_ROOT / directory

        if path.is_dir():
            doctor.ok(f"Found directory {directory}/")
        else:
            doctor.warning(f"Missing directory: {directory}/")


# ============================================================
# Metadata validation
# ============================================================

def check_metadata(metadata_path, minecraft_folder, release_folder):
    doctor.section(
        f"METADATA: {minecraft_folder.name} / {release_folder.name}"
    )

    metadata = load_json(metadata_path)

    if not isinstance(metadata, dict):
        doctor.error("Metadata must contain a JSON object.")
        return None

    required_top_level = [
        "schemaVersion",
        "modpackVersion",
        "minecraft",
        "loader",
        "content",
    ]

    check_required_fields(
        metadata,
        required_top_level,
        relative(metadata_path),
    )

    if metadata.get("schemaVersion") != 1:
        doctor.error("Unsupported or invalid schemaVersion (expected 1).")
    else:
        doctor.ok("Metadata schema version is 1")

    release_version = metadata.get("modpackVersion")

    if release_version != release_folder.name:
        doctor.error(
            f"modpackVersion mismatch: metadata says "
            f"'{release_version}', folder says '{release_folder.name}'"
        )
    else:
        doctor.ok("Release version matches its folder")

    if not parse_pack_version(release_version):
        doctor.warning(
            f"Release version '{release_version}' does not follow "
            "the expected semantic version format."
        )

    minecraft = metadata.get("minecraft")
    loader = metadata.get("loader")
    content = metadata.get("content")

    if not isinstance(minecraft, dict):
        doctor.error("'minecraft' must be an object.")
        minecraft = {}

    if not isinstance(loader, dict):
        doctor.error("'loader' must be an object.")
        loader = {}

    if not isinstance(content, dict):
        doctor.error("'content' must be an object.")
        content = {}

    check_required_fields(
        minecraft,
        ["version", "releaseType"],
        "minecraft",
    )

    check_required_fields(
        loader,
        ["type", "version"],
        "loader",
    )

    if minecraft.get("version") != minecraft_folder.name:
        doctor.error(
            f"Minecraft version mismatch: metadata says "
            f"'{minecraft.get('version')}', folder says "
            f"'{minecraft_folder.name}'"
        )
    else:
        doctor.ok(
            f"Minecraft version matches: {minecraft_folder.name}"
        )

    if loader.get("type") and loader["type"] not in (
        "fabric", "forge", "neoforge", "quilt"
    ):
        doctor.warning(f"Unrecognized loader type: {loader['type']}")

    for content_type, config in CONTENT_TYPES.items():
        entries = content.get(content_type, [])

        if not isinstance(entries, list):
            doctor.error(
                f"content.{content_type} must be an array."
            )
            continue

        doctor.ok(
            f"Found {len(entries)} {content_type} entries"
        )

        seen_names = set()

        for index, entry in enumerate(entries, start=1):
            location = f"content.{content_type}[{index}]"

            if not isinstance(entry, dict):
                doctor.error(f"{location} must be an object.")
                continue

            check_required_fields(
                entry,
                config["required_fields"],
                location,
            )

            name = entry.get("name")

            if isinstance(name, str) and name.strip():
                normalized_name = name.strip().casefold()

                if normalized_name in seen_names:
                    doctor.error(
                        f"Duplicate {content_type} entry: {name}"
                    )
                else:
                    seen_names.add(normalized_name)

            if content_type == "mods":
                if "required" in entry and not isinstance(
                    entry["required"], bool
                ):
                    doctor.error(
                        f"{location}: 'required' must be true or false."
                    )

                if entry.get("type") != "mod":
                    doctor.warning(
                        f"{location}: unexpected mod type "
                        f"'{entry.get('type')}'"
                    )

            for field in ("modrinthUrl", "curseforgeUrl"):
                url = entry.get(field)

                if url is None or url == "":
                    continue

                if not is_valid_url(url):
                    doctor.error(
                        f"{location}: invalid URL in '{field}'"
                    )
                elif is_placeholder_url(url):
                    doctor.warning(
                        f"{location}: placeholder URL in '{field}'"
                    )

    return metadata


# ============================================================
# Packwiz validation
# ============================================================

def check_packwiz(minecraft_version, release_version, metadata):
    doctor.section(f"PACKWIZ: {minecraft_version}")

    pack_directory = (
        PROJECT_ROOT / "packwiz" / minecraft_version
    )

    if not pack_directory.is_dir():
        doctor.error(
            f"Missing Packwiz directory: {relative(pack_directory)}"
        )
        return

    required_files = [
        "pack.toml",
        "index.toml",
        ".packwizignore",
    ]

    for filename in required_files:
        path = pack_directory / filename

        if path.is_file():
            doctor.ok(f"Found {relative(path)}")
        else:
            doctor.error(f"Missing {relative(path)}")

    pack_file = pack_directory / "pack.toml"
    index_file = pack_directory / "index.toml"

    pack_data = (
        load_toml(pack_file)
        if pack_file.is_file()
        else None
    )

    if isinstance(pack_data, dict):
        versions = pack_data.get("versions", {})

        if not isinstance(versions, dict):
            versions = {}

        pack_mc = versions.get("minecraft")
        pack_loader = versions.get("fabric")

        if pack_mc != minecraft_version:
            doctor.error(
                f"pack.toml Minecraft version mismatch: "
                f"expected {minecraft_version}, found {pack_mc}"
            )
        else:
            doctor.ok("pack.toml Minecraft version matches")

        if pack_data.get("name") != "EverSmooth Optimized":
            doctor.warning(
                "pack.toml name is not 'EverSmooth Optimized'"
            )
        else:
            doctor.ok("Packwiz project name matches")

        if metadata and isinstance(metadata.get("loader"), dict):
            metadata_loader = metadata["loader"]

            if (
                metadata_loader.get("type") == "fabric"
                and metadata_loader.get("version") != pack_loader
            ):
                doctor.error(
                    "Fabric loader version differs between "
                    "metadata.json and pack.toml"
                )
            elif metadata_loader.get("type") == "fabric":
                doctor.ok("Fabric loader version matches metadata")

        if pack_data.get("version") != release_version:
            doctor.error(
                f"pack.toml version mismatch: expected "
                f"{release_version}, found {pack_data.get('version')}"
            )
        else:
            doctor.ok("Packwiz release version matches")

    if index_file.is_file():
        index_data = load_toml(index_file)

        if isinstance(index_data, dict):
            files = index_data.get("files", [])

            if not isinstance(files, list):
                doctor.error("index.toml 'files' must be an array.")
                files = []

            doctor.ok(f"Found {len(files)} indexed Packwiz files")

            check_index_files(pack_directory, files)


def check_index_files(pack_directory, files):
    seen_paths = set()

    for entry in files:
        if not isinstance(entry, dict):
            doctor.error("Invalid entry in index.toml")
            continue

        file_name = entry.get("file")

        if not isinstance(file_name, str) or not file_name:
            doctor.error("An index.toml entry has no valid file path.")
            continue

        relative_path = Path(file_name)

        if relative_path.is_absolute() or ".." in relative_path.parts:
            doctor.error(
                f"Unsafe path in index.toml: {file_name}"
            )
            continue

        normalized = relative_path.as_posix().casefold()

        if normalized in seen_paths:
            doctor.error(f"Duplicate index entry: {file_name}")
            continue

        seen_paths.add(normalized)

        target = pack_directory / relative_path

        if not target.is_file():
            doctor.error(
                f"Indexed file is missing: {relative(pack_directory / relative_path)}"
            )
            continue

        expected_hash = entry.get("hash")
        hash_format = entry.get("hash-format", "sha256")

        if not expected_hash:
            doctor.warning(
                f"No hash found for indexed file: {file_name}"
            )
            continue

        if hash_format != "sha256":
            doctor.warning(
                f"Unsupported hash format '{hash_format}': {file_name}"
            )
            continue

        try:
            actual_hash = hashlib.sha256(
                target.read_bytes()
            ).hexdigest()
        except OSError as error:
            doctor.error(f"Could not read {file_name}: {error}")
            continue

        if actual_hash != expected_hash:
            doctor.error(
                f"SHA-256 mismatch: {file_name}"
            )
        else:
            doctor.ok(f"Hash verified: {file_name}")


# ============================================================
# Release discovery
# ============================================================

def discover_releases():
    versions_root = PROJECT_ROOT / "versions"

    if not versions_root.is_dir():
        doctor.error("Missing versions/ directory.")
        return []

    releases = []

    for minecraft_folder in sorted(versions_root.iterdir()):
        if not minecraft_folder.is_dir():
            continue

        for release_folder in sorted(minecraft_folder.iterdir()):
            if not release_folder.is_dir():
                continue

            metadata_path = release_folder / "metadata.json"
            readme_path = release_folder / "README.md"

            if not metadata_path.is_file():
                doctor.error(
                    f"Missing metadata.json: {relative(release_folder)}"
                )
                continue

            if not readme_path.is_file():
                doctor.warning(
                    f"Missing README.md: {relative(release_folder)}"
                )

            releases.append(
                (
                    minecraft_folder,
                    release_folder,
                    metadata_path,
                )
            )

    return releases


# ============================================================
# Main
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("       EverSmooth Optimized - Project Doctor")
    print("=" * 60)

    print(f"\nProject: {PROJECT_ROOT}")

    if not PROJECT_ROOT.is_dir():
        print("\n[ERROR] Project directory does not exist.")
        return 1

    check_root()

    releases = discover_releases()

    doctor.section("RELEASE DISCOVERY")

    if not releases:
        doctor.error("No valid release folders were discovered.")
    else:
        doctor.ok(f"Discovered {len(releases)} release(s)")

    for minecraft_folder, release_folder, metadata_path in releases:
        metadata = check_metadata(
            metadata_path,
            minecraft_folder,
            release_folder,
        )

        check_packwiz(
            minecraft_folder.name,
            release_folder.name,
            metadata,
        )

    doctor.section("FINAL REPORT")

    print(f"  Successful checks : {doctor.successes}")
    print(f"  Warnings          : {doctor.warnings}")
    print(f"  Errors            : {doctor.errors}")

    print("\n" + "=" * 60)

    if doctor.errors:
        print("  RESULT: FAILED")
        print("  Fix the errors above and run Doctor again.")
    elif doctor.warnings:
        print("  RESULT: PASSED WITH WARNINGS")
    else:
        print("  RESULT: HEALTHY")

    print("=" * 60 + "\n")

    return 1 if doctor.errors else 0


if __name__ == "__main__":
    sys.exit(main())
