
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import urllib.request
import zipfile

from urllib.parse import urlparse


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKWIZ_ROOT = PROJECT_ROOT / "packwiz"
RELEASES_ROOT = PROJECT_ROOT / "releases"

PACKWIZ_DEFAULT = Path(r"D:\Tools\Packwiz\packwiz.exe")

RELEASE_PREFIX = "ESO"
LOADER_NAME = "Fabric"

HANDLOOM_FOLDERS = {
    "mods": "mods",
    "resourcepacks": "resourcepacks",
}


# ============================================================
# Terminal UI
# ============================================================

def print_header():
    print("\n" + "=" * 56)
    print("              EverSmooth Optimized")
    print("                   CLI Exporter")
    print("=" * 56)


def print_error(message):
    print(f"\n[ERROR] {message}")


def print_success(message):
    print(f"\n[OK] {message}")


# ============================================================
# Packwiz Detection
# ============================================================

def find_packwiz():
    executable = shutil.which("packwiz")

    if executable:
        return Path(executable)

    if PACKWIZ_DEFAULT.is_file():
        return PACKWIZ_DEFAULT

    return None


# ============================================================
# Minecraft Version Detection
# ============================================================

def version_sort_key(version):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", version)
    ]


def get_available_versions():
    if not PACKWIZ_ROOT.is_dir():
        print_error(f"Packwiz directory not found: {PACKWIZ_ROOT}")
        return []

    versions = []

    for folder in PACKWIZ_ROOT.iterdir():
        if not folder.is_dir():
            continue

        if (
            (folder / "pack.toml").is_file()
            and (folder / "index.toml").is_file()
        ):
            versions.append(folder.name)

    return sorted(versions, key=version_sort_key)


def select_version(versions):
    print("\nSelect Minecraft Version:\n")

    for index, version in enumerate(versions, start=1):
        print(f"  [{index}] {version}")

    while True:
        choice = input("\nEnter choice: ").strip()

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(versions):
                return versions[choice - 1]

        print_error("Invalid selection. Try again.")


# ============================================================
# Release Information
# ============================================================

def get_release_info(version):
    pack_file = PACKWIZ_ROOT / version / "pack.toml"

    try:
        with pack_file.open("rb") as file:
            pack_data = tomllib.load(file)

    except (OSError, tomllib.TOMLDecodeError) as error:
        print_error(f"Could not read pack.toml: {error}")
        return None

    release_version = pack_data.get("version")
    loader_version = pack_data.get("versions", {}).get("fabric")

    if not release_version:
        print_error("Release version is missing from pack.toml.")
        return None

    if not loader_version:
        print_error("Fabric Loader version is missing from pack.toml.")
        return None

    return {
        "minecraft": version,
        "loader": str(loader_version),
        "release": str(release_version),
    }


def build_release_name(info):
    return (
        f"{RELEASE_PREFIX}+"
        f"{info['minecraft']}+"
        f"{LOADER_NAME}-{info['loader']}+"
        f"{info['release']}"
    )


# ============================================================
# Platform Selection
# ============================================================

def select_platforms():
    print("\nSelect Export Platform:\n")
    print("  [1] Modrinth")
    print("  [2] CurseForge")
    print("  [3] Handloom (Manual)")
    print("  [4] All Three")

    while True:
        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            return ["modrinth"]

        if choice == "2":
            return ["curseforge"]

        if choice == "3":
            return ["handloom"]

        if choice == "4":
            return ["modrinth", "curseforge", "handloom"]

        print_error("Select 1, 2, 3, or 4.")


# ============================================================
# Existing Platform Export
# ============================================================

def export_platform(packwiz, version, platform, release_name):
    pack_directory = PACKWIZ_ROOT / version
    output_directory = RELEASES_ROOT / version / platform

    output_directory.mkdir(parents=True, exist_ok=True)

    extensions = {
        "modrinth": ".mrpack",
        "curseforge": ".zip",
    }

    extension = extensions[platform]
    output_file = output_directory / f"{release_name}{extension}"

    if output_file.exists():
        print(f"\nExisting file: {output_file}")

        overwrite = input("Overwrite? [y/N]: ").strip().lower()

        if overwrite != "y":
            print(f"[SKIPPED] {platform.title()}")
            return None

    print(f"\n[EXPORTING] {platform.title()}...")

    command = [
        str(packwiz),
        platform,
        "export",
        "--output",
        str(output_file),
    ]

    try:
        result = subprocess.run(
            command,
            cwd=pack_directory,
            check=False,
        )

        if result.returncode != 0:
            print_error(f"{platform.title()} export failed.")
            return False

        if not output_file.is_file():
            print_error(
                "Export completed without producing the expected file."
            )
            return False

        print_success(f"{platform.title()} export completed.")
        print(f"File: {output_file}")

        return True

    except OSError as error:
        print_error(f"Could not execute Packwiz: {error}")
        return False


# ============================================================
# Handloom - Metadata Reading
# ============================================================

def get_handloom_entries(pack_directory, category):
    category_directory = pack_directory / category

    if not category_directory.is_dir():
        return []

    entries = []

    for metafile in sorted(category_directory.rglob("*.pw.toml")):
        try:
            with metafile.open("rb") as file:
                metadata = tomllib.load(file)

        except (OSError, tomllib.TOMLDecodeError) as error:
            raise RuntimeError(
                f"Could not read {metafile.name}: {error}"
            ) from error

        filename = metadata.get("filename")
        download = metadata.get("download", {})
        url = download.get("url")

        if not filename:
            if url:
                filename = Path(urlparse(url).path).name

        if not filename:
            raise RuntimeError(
                f"Missing filename in {metafile.name}"
            )

        filename = Path(filename).name

        if filename in ("", ".", ".."):
            raise RuntimeError(
                f"Invalid filename in {metafile.name}"
            )

        entries.append({
            "name": metadata.get("name", filename),
            "filename": filename,
            "url": url,
            "hash_format": download.get("hash-format"),
            "hash": download.get("hash"),
            "local_file": category_directory / filename,
            "metafile": metafile,
        })

    return entries


# ============================================================
# Handloom - Hash Verification
# ============================================================

def verify_hash(file_path, hash_format, expected_hash):
    if not hash_format or not expected_hash:
        return True

    algorithm = hash_format.lower().replace("-", "")

    try:
        hasher = hashlib.new(algorithm)

    except ValueError:
        raise RuntimeError(
            f"Unsupported hash algorithm: {hash_format}"
        )

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)

    actual_hash = hasher.hexdigest()

    if actual_hash.lower() != expected_hash.lower():
        raise RuntimeError(
            f"Hash verification failed for {file_path.name}"
        )

    return True


# ============================================================
# Handloom - Download Content
# ============================================================

def download_handloom_file(entry, destination):
    url = entry["url"]

    if not url:
        local_file = entry["local_file"]

        if local_file.is_file():
            shutil.copy2(local_file, destination)

            verify_hash(
                destination,
                entry["hash_format"],
                entry["hash"],
            )

            return

        raise RuntimeError(
            f"No downloadable URL or local file for {entry['name']}. "
            "This entry may require platform-specific resolution."
        )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "EverSmooth-Optimized-Exporter/1.0"
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            with destination.open("wb") as output:
                shutil.copyfileobj(response, output)

    except Exception as error:
        raise RuntimeError(
            f"Download failed for {entry['name']}: {error}"
        ) from error

    verify_hash(
        destination,
        entry["hash_format"],
        entry["hash"],
    )


# ============================================================
# Handloom - Manual ZIP Export
# ============================================================

def export_handloom(version, release_name):
    pack_directory = PACKWIZ_ROOT / version
    output_directory = RELEASES_ROOT / version / "handloom"

    output_directory.mkdir(parents=True, exist_ok=True)

    output_file = output_directory / f"{release_name}.zip"

    if output_file.exists():
        print(f"\nExisting file: {output_file}")

        overwrite = input("Overwrite? [y/N]: ").strip().lower()

        if overwrite != "y":
            print("[SKIPPED] Handloom")
            return None

    print("\n[HANDLOOM] Reading Packwiz metadata...")

    try:
        content = {}

        for category in HANDLOOM_FOLDERS:
            entries = get_handloom_entries(
                pack_directory,
                category,
            )

            content[category] = entries

            print(
                f"[FOUND] {category.title()}: {len(entries)} file(s)"
            )

        total_files = sum(len(entries) for entries in content.values())

        if total_files == 0:
            raise RuntimeError(
                "No mods or resource packs were found."
            )

        with tempfile.TemporaryDirectory(
            prefix="eversmooth-handloom-"
        ) as temporary_directory:

            temporary_root = Path(temporary_directory)

            staging_directory = temporary_root / "pack"
            staging_directory.mkdir()

            print("\n[HANDLOOM] Downloading content...")

            for category, entries in content.items():
                category_directory = staging_directory / category
                category_directory.mkdir()

                used_names = set()

                for index, entry in enumerate(entries, start=1):
                    filename = entry["filename"]

                    if filename.lower() in used_names:
                        raise RuntimeError(
                            f"Duplicate filename in {category}: {filename}"
                        )

                    used_names.add(filename.lower())

                    destination = category_directory / filename

                    print(
                        f"[{index}/{len(entries)}] "
                        f"{entry['name']}"
                    )

                    download_handloom_file(
                        entry,
                        destination,
                    )

            print("\n[HANDLOOM] Creating ZIP archive...")

            temporary_zip = temporary_root / "handloom.zip"

            with zipfile.ZipFile(
                temporary_zip,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=6,
            ) as archive:

                for file_path in sorted(staging_directory.rglob("*")):
                    if file_path.is_file():
                        archive.write(
                            file_path,
                            file_path.relative_to(staging_directory).as_posix(),
                        )

            with zipfile.ZipFile(temporary_zip, "r") as archive:
                corrupted_file = archive.testzip()

                if corrupted_file:
                    raise RuntimeError(
                        f"ZIP verification failed: {corrupted_file}"
                    )

            shutil.move(str(temporary_zip), str(output_file))

        print_success("Handloom export completed.")
        print(f"Files included: {total_files}")
        print(f"File: {output_file}")

        return True

    except Exception as error:
        print_error(f"Handloom export failed: {error}")
        return False


# ============================================================
# Main
# ============================================================

def main():
    print_header()

    print("\nDetecting Packwiz...")

    packwiz = find_packwiz()

    if not packwiz:
        print_error("Packwiz executable not found.")
        return 1

    print_success(f"Packwiz detected: {packwiz}")

    print("\nDetecting Minecraft versions...")

    versions = get_available_versions()

    if not versions:
        print_error("No valid Minecraft versions found.")
        print(f"Expected location: {PACKWIZ_ROOT}")
        return 1

    print_success(f"Found {len(versions)} Minecraft version(s).")

    version = select_version(versions)

    info = get_release_info(version)

    if not info:
        return 1

    release_name = build_release_name(info)

    print_success("Release information detected.")

    print(f"\nRelease name: {release_name}")
    print(f"Minecraft:    {info['minecraft']}")
    print(f"Fabric:       {info['loader']}")
    print(f"Pack version: {info['release']}")

    platforms = select_platforms()

    print("\n" + "=" * 56)
    print(f"Release:   {release_name}")
    print(f"Platforms: {', '.join(platforms).title()}")
    print("=" * 56)

    results = {}

    for platform in platforms:
        if platform == "handloom":
            results[platform] = export_handloom(
                version,
                release_name,
            )

        else:
            results[platform] = export_platform(
                packwiz,
                version,
                platform,
                release_name,
            )

    print("\n" + "=" * 56)
    print("                  EXPORT SUMMARY")
    print("=" * 56)

    for platform, result in results.items():
        if result is True:
            status = "SUCCESS"
        elif result is None:
            status = "SKIPPED"
        else:
            status = "FAILED"

        print(f"{platform.title():<15} {status}")

    print(f"\nRelease directory: {RELEASES_ROOT / version}")
    print("=" * 56)

    return 1 if any(value is False for value in results.values()) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())

    except KeyboardInterrupt:
        print("\n\nExport cancelled.")
        sys.exit(130)
