from __future__ import annotations

import re

import pandas as pd

try:
    from .config import COLUMN_ALIASES, REQUIRED_COLUMNS
except ImportError:
    from config import COLUMN_ALIASES, REQUIRED_COLUMNS


def normalize_header(header: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", str(header).strip().lower())
    return cleaned.strip("_")


def build_column_mapping(columns: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    normalized_columns = {column: normalize_header(column) for column in columns}

    for target, aliases in COLUMN_ALIASES.items():
        valid_aliases = {normalize_header(alias) for alias in aliases}
        for original_column, normalized_column in normalized_columns.items():
            if normalized_column == target or normalized_column in valid_aliases:
                mapping[original_column] = target
                break

    return mapping


def standardize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()
    mapping = build_column_mapping(list(dataframe.columns))
    dataframe = dataframe.rename(columns=mapping)
    dataframe.columns = [normalize_header(column) for column in dataframe.columns]
    return dataframe


def clean_email(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip().lower()
    return text or None


def clean_phone(value: object) -> str | None:
    if pd.isna(value):
        return None
    digits = re.sub(r"\D+", "", str(value))
    return digits or None


def clean_date(value: object) -> str | None:
    if pd.isna(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def apply_cleaning_rules(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()

    for column in REQUIRED_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = None

    dataframe["name"] = dataframe["name"].apply(
        lambda value: None if pd.isna(value) else str(value).strip() or None
    )
    dataframe["email"] = dataframe["email"].apply(clean_email)
    dataframe["phone"] = dataframe["phone"].apply(clean_phone)
    dataframe["date"] = dataframe["date"].apply(clean_date)

    return dataframe


def split_valid_and_invalid_rows(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    dataframe = dataframe.copy()

    def row_error_reason(row: pd.Series) -> str:
        missing_fields = [field for field in REQUIRED_COLUMNS if not row.get(field)]
        if missing_fields:
            return f"missing_required_fields:{','.join(missing_fields)}"
        return ""

    dataframe["_error_reason"] = dataframe.apply(row_error_reason, axis=1)
    invalid_rows = dataframe[dataframe["_error_reason"] != ""].copy()
    valid_rows = dataframe[dataframe["_error_reason"] == ""].copy()

    return valid_rows, invalid_rows


def deduplicate_rows(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    dataframe = dataframe.copy()
    before_count = len(dataframe)

    dataframe = dataframe.drop_duplicates(subset=["email"], keep="first")
    if dataframe["email"].isna().any():
        email_missing = dataframe["email"].isna()
        without_email = dataframe[email_missing].drop_duplicates(
            subset=["name", "phone"], keep="first"
        )
        with_email = dataframe[~email_missing]
        dataframe = pd.concat([with_email, without_email], ignore_index=True)

    removed_count = before_count - len(dataframe)
    return dataframe, removed_count
