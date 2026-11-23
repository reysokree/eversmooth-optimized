
from pathlib import Path
from datetime import datetime
import json
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERSIONS_DIR = PROJECT_ROOT / "versions"
PACKWIZ_DIR = PROJECT_ROOT / "packwiz"
REPORTS_DIR = PROJECT_ROOT / "reports"

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


def normalize_name(name):
    return " ".join(str(name).strip().casefold().split())


def markdown_escape(value):
    """Escape basic Markdown table characters."""
    return str(value).replace("|", "\\|").replace("\n", " ")


def get_content(metadata):
    content = metadata.get("content", {})

    if not isinstance(content, dict):
        content = {}

    result = {}
    warnings = []

    for category in CATEGORIES:
        items = content.get(category, [])

        if not isinstance(items, list):
            warnings.append(
                f"'{category}' must be a list in metadata.json."
            )
            result[category] = []
            continue

        valid_items = []

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

            valid_items.append(item)

        result[category] = valid_items

    return result, warnings


def get_packwiz_data(mc_version):
    packwiz_root = PACKWIZ_DIR / mc_version
    index_path = packwiz_root / "index.toml"

    result = {
        "available": False,
        "entries": {category: [] for category in CATEGORIES},
        "warnings": [],
        "unknown_files": [],
    }

    if not index_path.is_file():
        result["warnings"].append("Packwiz index.toml was not found.")
        return result

    try:
        with index_path.open("rb") as file:
            index = tomllib.load(file)

    except (OSError, tomllib.TOMLDecodeError) as error:
        result["warnings"].append(
            f"Could not read Packwiz index.toml: {error}"
        )
        return result

    files = index.get("files", [])

    if not isinstance(files, list):
        result["warnings"].append(
            "Packwiz index has an invalid 'files' section."
        )
        return result

    result["available"] = True

    for item in files:
        if not isinstance(item, dict):
            result["warnings"].append(
                "Invalid entry found in Packwiz index."
            )
            continue

        relative_path = item.get("file")

        if not isinstance(relative_path, str):
            result["warnings"].append(
                "An index entry has no valid file path."
            )
            continue

        parts = Path(relative_path).parts

        if not parts:
            continue

        folder = parts[0].casefold()
        category = None

        for key, folders in CATEGORY_FOLDERS.items():
            if folder in folders:
                category = key
                break

        if category is None:
            continue

        file_path = packwiz_root / relative_path

        if item.get("metafile") is not True:
            result["unknown_files"].append(relative_path)
            continue

        if not file_path.is_file():
            result["warnings"].append(
                f"Missing Packwiz metafile: {relative_path}"
            )
            continue

        try:
            with file_path.open("rb") as file:
                metafile = tomllib.load(file)

            name = metafile.get("name")

            if not isinstance(name, str) or not name.strip():
                result["warnings"].append(
                    f"Missing name in metafile: {relative_path}"
                )
                continue

            result["entries"][category].append({
                "name": name.strip(),
                "path": relative_path,
            })

        except (OSError, tomllib.TOMLDecodeError) as error:
            result["warnings"].append(
                f"Could not read {relative_path}: {error}"
            )

    return result


def get_sync_results(content, packwiz_data):
    results = {}

    for category in CATEGORIES:
        metadata_names = {
            normalize_name(item["name"])
            for item in content[category]
        }

        packwiz_names = {
            normalize_name(item["name"])
            for item in packwiz_data["entries"][category]
        }

        results[category] = {
            "matching": len(metadata_names & packwiz_names),
            "missing": sorted(metadata_names - packwiz_names),
            "extra": sorted(packwiz_names - metadata_names),
        }

    return results


def get_url_warnings(content):
    warnings = []

    for category, items in content.items():
        for item in items:
            name = item.get("name", "Unknown")

            for field in ("modrinthUrl", "curseforgeUrl"):
                url = item.get(field)

                if not isinstance(url, str) or not url.strip():
                    warnings.append(
                        f"{name}: missing {field}."
                    )
                elif "example-mod" in url.casefold():
                    warnings.append(
                        f"{name}: placeholder {field}."
                    )

    return warnings


def get_mod_counts(mods):
    required = sum(
        1 for mod in mods
        if mod.get("required") is True
    )

    optional = sum(
        1 for mod in mods
        if mod.get("required") is False
    )

    unspecified = len(mods) - required - optional

    return required, optional, unspecified


def build_content_section(category, items):
    title = CATEGORIES[category]
    output = [f"## {title}", ""]

    if not items:
        output.append("_No entries._")
        output.append("")
        return output

    output.append(
        "| Name | Author | Version | Modrinth | CurseForge |"
    )
    output.append(
        "|---|---|---|---|---|"
    )

    for item in items:
        name = markdown_escape(item.get("name", "Unknown"))
        author = markdown_escape(item.get("author", "Unknown"))
        version = markdown_escape(item.get("version", "Unknown"))

        modrinth = item.get("modrinthUrl", "")
        curseforge = item.get("curseforgeUrl", "")

        if isinstance(modrinth, str) and modrinth.strip():
            modrinth_cell = f"[Open]({modrinth})"
        else:
            modrinth_cell = "Not provided"

        if isinstance(curseforge, str) and curseforge.strip():
            curseforge_cell = f"[Open]({curseforge})"
        else:
            curseforge_cell = "Not provided"

        output.append(
            f"| {name} | {author} | {version} "
            f"| {modrinth_cell} | {curseforge_cell} |"
        )

    output.append("")
    return output


def build_report(mc_version, release, metadata):
    content, metadata_warnings = get_content(metadata)
    packwiz_data = get_packwiz_data(mc_version)

    minecraft = metadata.get("minecraft", {})
    loader = metadata.get("loader", {})

    if not isinstance(minecraft, dict):
        minecraft = {}

    if not isinstance(loader, dict):
        loader = {}

    mods = content["mods"]
    resourcepacks = content["resourcepacks"]
    shaders = content["shaders"]

    required, optional, unspecified = get_mod_counts(mods)

    sync_results = get_sync_results(content, packwiz_data)
    url_warnings = get_url_warnings(content)

    generated_at = datetime.now().astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )

    output = []

    output.extend([
        "# EverSmooth Optimized - Release Report",
        "",
        f"**Release:** `{release}`",
        f"**Minecraft:** `{minecraft.get('version', mc_version)}`",
        f"**Loader:** `{loader.get('type', 'Unknown')}` "
        f"`{loader.get('version', 'Unknown')}`",
        f"**Release Type:** `{minecraft.get('releaseType', 'Unknown')}`",
        f"**Generated:** {generated_at}",
        "",
        "---",
        "",
        "## Release Summary",
        "",
        "| Category | Count |",
        "|---|---:|",
        f"| Mods | {len(mods)} |",
        f"| Resource Packs | {len(resourcepacks)} |",
        f"| Shaders | {len(shaders)} |",
        f"| **Total** | **{len(mods) + len(resourcepacks) + len(shaders)}** |",
        "",
        "### Mod Requirements",
        "",
        f"- Required mods: **{required}**",
        f"- Optional mods: **{optional}**",
        f"- Unspecified requirement: **{unspecified}**",
        "",
        "---",
        "",
    ])

    for category in CATEGORIES:
        output.extend(build_content_section(
            category,
            content[category],
        ))

    output.extend([
        "---",
        "",
        "## Packwiz Synchronization",
        "",
    ])

    if not packwiz_data["available"]:
        output.append(
            "**Status:** Could not check Packwiz synchronization."
        )
        output.append("")
    else:
        output.append(
            "| Category | Matching | Missing | Extra |"
        )
        output.append(
            "|---|---:|---:|---:|"
        )

        for category, title in CATEGORIES.items():
            result = sync_results[category]

            output.append(
                f"| {title} | {result['matching']} "
                f"| {len(result['missing'])} "
                f"| {len(result['extra'])} |"
            )

        output.append("")

        for category, title in CATEGORIES.items():
            result = sync_results[category]

            if result["missing"]:
                output.append(f"### Missing from Packwiz: {title}")
                output.append("")

                for name in result["missing"]:
                    output.append(f"- `{name}`")

                output.append("")

            if result["extra"]:
                output.append(f"### Missing from Metadata: {title}")
                output.append("")

                for name in result["extra"]:
                    output.append(f"- `{name}`")

                output.append("")

    output.extend([
        "---",
        "",
        "## Validation Warnings",
        "",
    ])

    all_warnings = (
        metadata_warnings
        + packwiz_data["warnings"]
        + url_warnings
    )

    if all_warnings:
        for warning in all_warnings:
            output.append(f"- [!] {warning}")
    else:
        output.append("No warnings detected by this report.")

    output.append("")

    if packwiz_data["unknown_files"]:
        output.extend([
            "### Packwiz Files Without Metafiles",
            "",
            "These files could not be matched by display name:",
            "",
        ])

        for path in packwiz_data["unknown_files"]:
            output.append(f"- `{path}`")

        output.append("")

    output.extend([
        "---",
        "",
        "_Generated automatically by EverSmooth Optimized report.py._",
        "",
    ])

    return "\n".join(output)


def main():
    line()
    print("       EVERSMOOTH OPTIMIZED - REPORT GENERATOR")
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

    metadata_path = (
        VERSIONS_DIR / mc_version / release / "metadata.json"
    )

    metadata = load_metadata(metadata_path)

    if metadata is None:
        pause()
        return

    print("\nGenerating release report...")

    report = build_report(mc_version, release, metadata)

    output_dir = REPORTS_DIR / mc_version / release
    output_path = output_dir / "release-report.md"

    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            overwrite = input(
                "\nA report already exists. Overwrite it? (y/N): "
            ).strip().lower()

            if overwrite != "y":
                print("\nReport generation cancelled.")
                pause()
                return

        output_path.write_text(report, encoding="utf-8")

    except OSError as error:
        print(f"\n[ERROR] Could not save report: {error}")
        pause()
        return

    line()
    print("[SUCCESS] Report generated.")
    line()

    print(f"\nMinecraft : {mc_version}")
    print(f"Release   : {release}")
    print(f"Output    : {output_path.relative_to(PROJECT_ROOT)}")

    pause()


if __name__ == "__main__":
    main()
