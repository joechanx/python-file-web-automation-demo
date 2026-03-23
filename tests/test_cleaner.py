from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.cleaner import (
    apply_cleaning_rules,
    deduplicate_rows,
    standardize_columns,
)


def test_standardize_columns_maps_aliases() -> None:
    dataframe = pd.DataFrame(
        {
            "Full Name": ["Alice"],
            "E-mail": ["ALICE@example.com"],
            "Mobile": ["0912-345-678"],
            "Signup Date": ["2026/03/20"],
        }
    )

    result = standardize_columns(dataframe)
    assert {"name", "email", "phone", "date"}.issubset(set(result.columns))


def test_apply_cleaning_rules_normalizes_values() -> None:
    dataframe = pd.DataFrame(
        {
            "name": [" Alice "],
            "email": ["ALICE@example.com "],
            "phone": ["0912-345-678"],
            "date": ["2026/03/20"],
        }
    )

    result = apply_cleaning_rules(dataframe)
    row = result.iloc[0]
    assert row["name"] == "Alice"
    assert row["email"] == "alice@example.com"
    assert row["phone"] == "0912345678"
    assert row["date"] == "2026-03-20"


def test_deduplicate_rows_removes_same_email() -> None:
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Alice Duplicate"],
            "email": ["alice@example.com", "alice@example.com"],
            "phone": ["0912345678", "0912345678"],
            "date": ["2026-03-20", "2026-03-20"],
        }
    )

    result, removed = deduplicate_rows(dataframe)
    assert len(result) == 1
    assert removed == 1
