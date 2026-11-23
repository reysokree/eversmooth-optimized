
from pathlib import Path
import shutil


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    PROJECT_ROOT / "releases",
    PROJECT_ROOT / "metadata-exports",
    PROJECT_ROOT / "reports",
    PROJECT_ROOT / "backups"
]


# ============================================================
# Terminal UI
# ============================================================

def print_header():
    print("\n" + "=" * 52)
    print("             EverSmooth Optimized")
    print("                  CLI Cleaner")
    print("=" * 52)


def main():
    print_header()

    print("\nThe following directories will be permanently deleted:\n")

    for target in TARGETS:
        status = "FOUND" if target.is_dir() else "NOT FOUND"
        print(f"  [{status}] {target.relative_to(PROJECT_ROOT)}")

    print("\nThis operation cannot be undone.")

    confirm = input("\nContinue? [y/N]: ").strip().lower()

    if confirm != "y":
        print("\n[CANCELLED] No files were deleted.")
        return 0

    deleted = 0
    missing = 0
    failed = 0

    for target in TARGETS:
        if not target.exists():
            missing += 1
            continue

        try:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()

            print(f"[DELETED] {target.relative_to(PROJECT_ROOT)}")
            deleted += 1

        except OSError as error:
            print(f"[FAILED] {target.name}: {error}")
            failed += 1

    print("\n" + "=" * 52)
    print("                  CLEANUP SUMMARY")
    print("=" * 52)

    print(f"Deleted: {deleted}")
    print(f"Missing: {missing}")
    print(f"Failed:  {failed}")

    print("=" * 52)

    return 1 if failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Cleanup interrupted.")
        raise SystemExit(130)
