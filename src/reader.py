from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from .config import INPUT_DIR
except ImportError:
    from config import INPUT_DIR


SUPPORTED_SUFFIXES = {".csv", ".xlsx"}


def find_input_files() -> list[Path]:
    return sorted(
        [
            path
            for path in INPUT_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        ]
    )


def read_single_file(file_path: Path) -> pd.DataFrame:
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        dataframe = pd.read_csv(file_path)
    elif suffix == ".xlsx":
        dataframe = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    dataframe["_source_file"] = file_path.name
    return dataframe


def load_input_data() -> tuple[list[pd.DataFrame], list[Path]]:
    file_paths = find_input_files()
    dataframes = [read_single_file(file_path) for file_path in file_paths]
    return dataframes, file_paths
