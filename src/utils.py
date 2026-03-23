from __future__ import annotations

from pathlib import Path
import shutil

try:
    from .config import ARCHIVE_DIR, INPUT_DIR, LOGS_DIR, OUTPUT_DIR
except ImportError:
    from config import ARCHIVE_DIR, INPUT_DIR, LOGS_DIR, OUTPUT_DIR


def ensure_directories() -> None:
    for directory in (INPUT_DIR, OUTPUT_DIR, ARCHIVE_DIR, LOGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def archive_file(file_path: Path) -> Path:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    destination = ARCHIVE_DIR / file_path.name
    if destination.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        counter = 1
        while destination.exists():
            destination = ARCHIVE_DIR / f"{stem}_{counter}{suffix}"
            counter += 1
    shutil.move(str(file_path), str(destination))
    return destination
