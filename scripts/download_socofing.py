#!/usr/bin/env python3
"""
Download the SOCOFing dataset via kagglehub and link/copy it under ./data/.

Usage:
  python scripts/download_socofing.py               # symlink to ./data/socofing
  python scripts/download_socofing.py --copy        # copy files into ./data/socofing (disk heavy)
  python scripts/download_socofing.py --force       # overwrite existing link/dir
  python scripts/download_socofing.py --target ./data/my-socofing

Notes:
  - Requires: python -m pip install --upgrade kagglehub
  - Kaggle authentication may be needed. If prompted, follow kagglehub instructions.
"""

from __future__ import annotations
import argparse
import os
import shutil
from pathlib import Path

DATASET = "ruizgara/socofing"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copy", action="store_true", help="Copy dataset instead of symlink")
    parser.add_argument("--force", action="store_true", help="Overwrite existing target")
    parser.add_argument("--target", type=Path, default=None, help="Custom target dir (default: ./data/socofing)")
    args = parser.parse_args()

    try:
        import kagglehub  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "kagglehub is not installed. Run:\n\n"
            "  python -m pip install --upgrade kagglehub\n"
        ) from e

    print(f"Downloading dataset: {DATASET} ...")
    cache_path = Path(kagglehub.dataset_download(DATASET)).resolve()
    print(f"Downloaded to cache: {cache_path}")

    # Determine repo root (two levels up from this script: scripts/ -> repo)
    repo_root = Path(__file__).resolve().parents[1]
    data_root = repo_root / "data"
    data_root.mkdir(parents=True, exist_ok=True)

    target_dir = args.target if args.target else (data_root / "socofing")
    target_dir = target_dir.resolve()
    print(f"Preparing target: {target_dir}")

    if target_dir.exists() or target_dir.is_symlink():
        if args.force:
            if target_dir.is_symlink() or target_dir.is_file():
                target_dir.unlink()
            else:
                shutil.rmtree(target_dir)
        else:
            print(f"Target already exists: {target_dir} (use --force to overwrite)")
            print("Done.")
            return

    if args.copy:
        print("Copying dataset into repo (this may take a while)...")
        shutil.copytree(cache_path, target_dir, dirs_exist_ok=True)
    else:
        print("Linking cached dataset into repo (fast, uses minimal disk)...")
        target_dir.symlink_to(cache_path, target_is_directory=True)

    print("Done.")
    print(f"Dataset available at: {target_dir}")
    print("Remember: ./data/ is git-ignored, so large files stay out of commits.")


if __name__ == "__main__":
    main()
