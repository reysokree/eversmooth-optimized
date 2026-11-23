
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = PROJECT_ROOT / "backups"


def line():
    print("=" * 64)


def pause():
    input("\nPress Enter to continue...")


def collect_files(backup_path):
    files = []

    for root, directories, filenames in os.walk(
        PROJECT_ROOT,
        followlinks=False,
    ):
        root_path = Path(root)

        # Avoid following directory symlinks.
        directories[:] = [
            directory
            for directory in directories
            if not (root_path / directory).is_symlink()
        ]

        for filename in filenames:
            path = root_path / filename

            if path.is_symlink():
                continue

            # Never include the ZIP currently being created.
            if path.resolve() == backup_path.resolve():
                continue

            files.append(path)

    return sorted(files)


def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"EverSmooth-Optimized_Backup_{timestamp}.zip"
    backup_path = BACKUP_DIR / filename

    print("\nScanning entire project root...")

    files = collect_files(backup_path)

    if not files:
        print("\n[ERROR] No project files found.")
        return

    total_size = sum(path.stat().st_size for path in files)

    line()
    print("BACKUP SUMMARY")
    line()

    print(f"Project Root : {PROJECT_ROOT}")
    print(f"Files        : {len(files)}")
    print(f"Total Size   : {total_size:,} bytes")
    print(f"Destination  : {backup_path}")

    print("\nCreating complete backup...")

    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        with ZipFile(
            backup_path,
            mode="w",
            compression=ZIP_DEFLATED,
            compresslevel=6,
        ) as archive:

            for index, path in enumerate(files, start=1):
                relative_path = path.relative_to(PROJECT_ROOT)

                archive.write(
                    path,
                    relative_path.as_posix(),
                )

                print(
                    f"\rProgress: {index}/{len(files)}",
                    end="",
                    flush=True,
                )

        print("\n\nVerifying backup...")

        with ZipFile(backup_path, "r") as archive:
            bad_file = archive.testzip()

        if bad_file:
            raise RuntimeError(
                f"Corrupted archive entry: {bad_file}"
            )

    except (OSError, RuntimeError) as error:
        if backup_path.exists():
            backup_path.unlink()

        print(f"\n[ERROR] Backup failed: {error}")
        return

    compressed_size = backup_path.stat().st_size

    line()
    print("[SUCCESS] COMPLETE BACKUP CREATED")
    line()

    print(f"\nFilename      : {filename}")
    print(f"Files         : {len(files)}")
    print(f"Original Size : {total_size:,} bytes")
    print(f"ZIP Size      : {compressed_size:,} bytes")
    print(f"Location      : {backup_path}")

    print("\nEverything from the project root was included.")
    print("The backup archive itself was excluded from its contents.")


def main():
    line()
    print("       EVERSMOOTH OPTIMIZED - FULL BACKUP")
    line()

    print("\nThis will back up EVERYTHING inside the project root.")
    print("Including hidden files, .git, generated files and backups.")

    choice = input("\nContinue? (y/N): ").strip().lower()

    if choice != "y":
        print("\nBackup cancelled.")
        pause()
        return

    create_backup()
    pause()


if __name__ == "__main__":
    main()
