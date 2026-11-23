
from pathlib import Path
import json
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERSIONS_DIR = PROJECT_ROOT / "versions"
PACKWIZ_DIR = PROJECT_ROOT / "packwiz"

CATEGORIES = {
    "mods": "Mods",
    "resourcepacks": "Resource Packs",
    "shaders": "Shaders",
}

CATEGORY_FOLDERS = {
    "mods": {"mods"},
    "resourcepacks": {"resourcepacks"},
    "shaders": {"shaders", "shaderpacks"},
}


def line():
    print("=" * 64)


def pause():
    input("\nPress Enter to continue...")


def select_item(items, title, label):
    if not items:
        print(f"\nNo {label.lower()} found.")
        pause()
        return None

    while True:
        print(f"\n{title}")
        line()

        for number, item in enumerate(items, start=1):
            print(f"[{number}] {item}")

        print("[0] Back")

        choice = input("\nSelect: ").strip()

        if choice == "0":
            return None

        if choice.isdigit() and 1 <= int(choice) <= len(items):
            return items[int(choice) - 1]

        print("Invalid selection.")


def get_versions():
    if not VERSIONS_DIR.exists():
        return []

    return sorted(
        folder.name
        for folder in VERSIONS_DIR.iterdir()
        if folder.is_dir()
    )


def get_releases(mc_version):
    version_path = VERSIONS_DIR / mc_version

    if not version_path.exists():
        return []

    return sorted(
        folder.name
        for folder in version_path.iterdir()
        if folder.is_dir()
        and (folder / "metadata.json").is_file()
    )


def load_metadata(path):
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Metadata root must be a JSON object.")

        return data

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"\n[ERROR] Could not read metadata.json: {error}")
        return None


def load_index(path):
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)

        files = data.get("files", [])

        if not isinstance(files, list):
            raise ValueError("Invalid Packwiz index: 'files' must be a list.")

        return files

    except (OSError, tomllib.TOMLDecodeError, ValueError) as error:
        print(f"\n[ERROR] Could not read index.toml: {error}")
        return None


def normalize_name(name):
    return " ".join(str(name).strip().casefold().split())


def get_category(path):
    parts = Path(path).parts

    if not parts:
        return None

    folder = parts[0].casefold()

    for category, folders in CATEGORY_FOLDERS.items():
        if folder in folders:
            return category

    return None


def read_packwiz_entries(packwiz_root, index_files):
    entries = {
        category: []
        for category in CATEGORIES
    }

    unknown_files = []
    warnings = []

    for item in index_files:
        if not isinstance(item, dict):
            warnings.append("Invalid entry found in index.toml.")
            continue

        relative_path = item.get("file")

        if not isinstance(relative_path, str):
            warnings.append("An index entry has no valid file path.")
            continue

        category = get_category(relative_path)

        if category is None:
            continue

        file_path = packwiz_root / relative_path

        # Packwiz metafiles contain the human-readable content name.
        if item.get("metafile") is True:
            if not file_path.is_file():
                warnings.append(
                    f"Missing Packwiz metafile: {relative_path}"
                )
                continue

            try:
                with file_path.open("rb") as file:
                    metafile = tomllib.load(file)

                name = metafile.get("name")

                if not isinstance(name, str) or not name.strip():
                    warnings.append(
                        f"Missing name in metafile: {relative_path}"
                    )
                    continue

                entries[category].append({
                    "name": name.strip(),
                    "path": relative_path,
                })

            except (OSError, tomllib.TOMLDecodeError) as error:
                warnings.append(
                    f"Could not read {relative_path}: {error}"
                )

        else:
            # A regular file has no guaranteed display name.
            unknown_files.append(relative_path)

    return entries, unknown_files, warnings


def read_metadata_entries(metadata):
    content = metadata.get("content", {})

    if not isinstance(content, dict):
        content = {}

    entries = {
        category: []
        for category in CATEGORIES
    }

    warnings = []

    for category in CATEGORIES:
        items = content.get(category, [])

        if not isinstance(items, list):
            warnings.append(
                f"Metadata category '{category}' is not a list."
            )
            continue

        for index, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                warnings.append(
                    f"{category}: entry #{index} is not an object."
                )
                continue

            name = item.get("name")

            if not isinstance(name, str) or not name.strip():
                warnings.append(
                    f"{category}: entry #{index} has no valid name."
                )
                continue

            entries[category].append(name.strip())

    return entries, warnings


def compare_category(category, metadata_entries, packwiz_entries):
    metadata_map = {
        normalize_name(name): name
        for name in metadata_entries
    }

    packwiz_map = {
        normalize_name(item["name"]): item
        for item in packwiz_entries
    }

    metadata_names = set(metadata_map)
    packwiz_names = set(packwiz_map)

    matching = metadata_names & packwiz_names
    missing = metadata_names - packwiz_names
    extra = packwiz_names - metadata_names

    print(f"\n{CATEGORIES[category].upper()}")
    line()

    print(f"Metadata entries : {len(metadata_entries)}")
    print(f"Packwiz entries  : {len(packwiz_entries)}")
    print(f"Matching         : {len(matching)}")
    print(f"Missing          : {len(missing)}")
    print(f"Extra            : {len(extra)}")

    if matching:
        print("\n[MATCHING]")
        for name in sorted(matching):
            print(f"  [OK] {metadata_map[name]}")

    if missing:
        print("\n[MISSING FROM PACKWIZ]")
        for name in sorted(missing):
            print(f"  [!] {metadata_map[name]}")

    if extra:
        print("\n[MISSING FROM METADATA]")
        for name in sorted(extra):
            item = packwiz_map[name]
            print(f"  [!] {item['name']} ({item['path']})")

    if not missing and not extra:
        print("\n[OK] Metadata and Packwiz are synchronized.")


def run_sync(mc_version, release):
    metadata_path = (
        VERSIONS_DIR / mc_version / release / "metadata.json"
    )

    packwiz_root = PACKWIZ_DIR / mc_version
    index_path = packwiz_root / "index.toml"

    print("\nLoading project data...")

    metadata = load_metadata(metadata_path)

    if metadata is None:
        return

    index_files = load_index(index_path)

    if index_files is None:
        return

    metadata_entries, metadata_warnings = read_metadata_entries(
        metadata
    )

    packwiz_entries, unknown_files, packwiz_warnings = (
        read_packwiz_entries(packwiz_root, index_files)
    )

    line()
    print("             EVERSMOOTH OPTIMIZED - SYNC")
    line()

    print(f"Minecraft Version : {mc_version}")
    print(f"Release           : {release}")
    print(f"Metadata          : {metadata_path.relative_to(PROJECT_ROOT)}")
    print(f"Packwiz           : {packwiz_root.relative_to(PROJECT_ROOT)}")

    for category in CATEGORIES:
        compare_category(
            category,
            metadata_entries[category],
            packwiz_entries[category],
        )

    if unknown_files:
        print("\nUNCLASSIFIED PACKWIZ FILES")
        line()

        for path in unknown_files:
            print(f"  [?] {path}")

        print(
            "\nThese files do not have readable Packwiz metafile names."
        )

    all_warnings = metadata_warnings + packwiz_warnings

    if all_warnings:
        print("\nWARNINGS")
        line()

        for warning in all_warnings:
            print(f"  [!] {warning}")

    line()
    print("SYNC CHECK COMPLETED")
    line()

    print("\nThis operation was read-only.")
    print("No metadata or Packwiz files were modified.")


def main():
    line()
    print("       EVERSMOOTH OPTIMIZED - SYNC CHECKER")
    line()

    versions = get_versions()

    mc_version = select_item(
        versions,
        "Select Minecraft Version",
        "Minecraft versions",
    )

    if mc_version is None:
        return

    releases = get_releases(mc_version)

    release = select_item(
        releases,
        "Select Release",
        "releases",
    )

    if release is None:
        return

    run_sync(mc_version, release)
    pause()


if __name__ == "__main__":
    main()
