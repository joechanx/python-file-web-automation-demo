from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from .cleaner import (
        apply_cleaning_rules,
        deduplicate_rows,
        prepare_output_dataframe,
        split_valid_and_invalid_rows,
        standardize_columns,
    )
    from .config import load_column_aliases, load_rules
    from .merger import merge_dataframes
except ImportError:
    from cleaner import (
        apply_cleaning_rules,
        deduplicate_rows,
        prepare_output_dataframe,
        split_valid_and_invalid_rows,
        standardize_columns,
    )
    from config import load_column_aliases, load_rules
    from merger import merge_dataframes


def process_dataframes(
    dataframes: list[pd.DataFrame],
    file_names: list[str] | None = None,
    column_aliases: dict[str, list[str]] | None = None,
    rules: dict | None = None,
) -> dict:
    aliases = column_aliases or load_column_aliases()
    resolved_rules = rules or load_rules()
    source_names = file_names or [f'file_{index + 1}' for index in range(len(dataframes))]

    prepared_frames: list[pd.DataFrame] = []
    for index, dataframe in enumerate(dataframes):
        frame = dataframe.copy()
        if '_source_file' not in frame.columns:
            frame['_source_file'] = source_names[index]
        prepared_frames.append(frame)

    if not prepared_frames:
        empty = pd.DataFrame()
        summary = {
            'files_processed': 0,
            'rows_read': 0,
            'rows_after_cleaning': 0,
            'duplicates_removed': 0,
            'invalid_rows': 0,
            'output_file': 'output/master.csv',
            'config_files': ['config/column_mapping.json', 'config/rules.json'],
        }
        return {
            'merged': empty,
            'cleaned': empty,
            'valid': empty,
            'invalid': empty,
            'output': empty,
            'rejected': empty,
            'summary': summary,
        }

    standardized_frames = [standardize_columns(dataframe, column_aliases=aliases) for dataframe in prepared_frames]
    merged_dataframe = merge_dataframes(standardized_frames)
    cleaned_dataframe = apply_cleaning_rules(merged_dataframe, rules=resolved_rules)

    valid_rows, invalid_rows = split_valid_and_invalid_rows(
        cleaned_dataframe,
        required_columns=resolved_rules.get('required_columns', []),
    )
    deduplicated_rows, duplicates_removed = deduplicate_rows(
        valid_rows,
        primary_keys=resolved_rules.get('dedupe_keys_primary', []),
        fallback_keys=resolved_rules.get('dedupe_keys_fallback', []),
    )

    output_dataframe = prepare_output_dataframe(
        deduplicated_rows,
        output_columns=resolved_rules.get('output_columns', []),
        drop_columns=resolved_rules.get('drop_columns', []),
    )
    rejected_dataframe = prepare_output_dataframe(
        invalid_rows,
        output_columns=resolved_rules.get('output_columns', []) + ['_error_reason'],
        drop_columns=resolved_rules.get('drop_columns', []),
    )

    summary = {
        'files_processed': len(source_names),
        'rows_read': int(len(merged_dataframe)),
        'rows_after_cleaning': int(len(output_dataframe)),
        'duplicates_removed': int(duplicates_removed),
        'invalid_rows': int(len(rejected_dataframe)),
        'output_file': 'output/master.csv',
        'config_files': ['config/column_mapping.json', 'config/rules.json'],
    }

    return {
        'merged': merged_dataframe,
        'cleaned': cleaned_dataframe,
        'valid': deduplicated_rows,
        'invalid': invalid_rows,
        'output': output_dataframe,
        'rejected': rejected_dataframe,
        'summary': summary,
    }
