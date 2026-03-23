from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

try:
    from .config import LOGS_DIR, OUTPUT_DIR
except ImportError:
    from config import LOGS_DIR, OUTPUT_DIR


def setup_logging() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("file_automation")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(LOGS_DIR / "process.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def write_master_file(dataframe: pd.DataFrame, filename: str = "master.csv") -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    dataframe.to_csv(output_path, index=False)
    return output_path


def write_rejected_rows(dataframe: pd.DataFrame, filename: str = "rejected_rows.csv") -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    dataframe.to_csv(output_path, index=False)
    return output_path


def write_summary(summary: dict, filename: str = "summary.json") -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    output_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_path
