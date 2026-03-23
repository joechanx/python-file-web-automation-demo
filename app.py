from __future__ import annotations

import io
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.cleaner import normalize_header
from src.config import INPUT_DIR, load_column_aliases, load_rules
from src.pipeline import process_dataframes


def read_uploaded_dataframe(file_name: str, payload: bytes) -> pd.DataFrame:
    suffix = Path(file_name).suffix.lower()
    if suffix == '.csv':
        dataframe = pd.read_csv(io.BytesIO(payload))
    elif suffix == '.xlsx':
        dataframe = pd.read_excel(io.BytesIO(payload))
    else:
        raise ValueError(f'Unsupported file type: {suffix}')

    dataframe['_source_file'] = file_name
    return dataframe


def load_demo_data() -> tuple[list[pd.DataFrame], list[str]]:
    dataframes: list[pd.DataFrame] = []
    file_names: list[str] = []
    for path in sorted(INPUT_DIR.iterdir()):
        if path.suffix.lower() not in {'.csv', '.xlsx'}:
            continue
        file_names.append(path.name)
        if path.suffix.lower() == '.csv':
            dataframe = pd.read_csv(path)
        else:
            dataframe = pd.read_excel(path)
        dataframe['_source_file'] = path.name
        dataframes.append(dataframe)
    return dataframes, file_names


def build_default_field_mapping(available_columns: list[str], aliases: dict[str, list[str]]) -> dict[str, str | None]:
    normalized_lookup = {normalize_header(column): column for column in available_columns}
    defaults: dict[str, str | None] = {}
    for field, alias_list in aliases.items():
        selected = None
        candidates = [field, *alias_list]
        for candidate in candidates:
            normalized = normalize_header(candidate)
            if normalized in normalized_lookup:
                selected = normalized_lookup[normalized]
                break
        defaults[field] = selected
    return defaults


def build_column_aliases_from_ui(
    selected_mapping: dict[str, str | None],
    base_aliases: dict[str, list[str]],
) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = {}
    for field, alias_list in base_aliases.items():
        selected = selected_mapping.get(field)
        merged = []
        if selected:
            merged.append(selected)
        for alias in alias_list:
            if alias not in merged:
                merged.append(alias)
        if field not in merged:
            merged.append(field)
        aliases[field] = merged
    return aliases


def build_rules_from_ui(
    required_columns: list[str],
    output_columns: list[str],
    dedupe_primary: list[str],
    dedupe_fallback: list[str],
    trim_columns: list[str],
    lowercase_columns: list[str],
    digits_only_columns: list[str],
    amount_columns: list[str],
    date_columns: list[str],
    date_format: str,
) -> dict:
    return {
        'required_columns': required_columns,
        'output_columns': output_columns,
        'drop_columns': [],
        'dedupe_keys_primary': dedupe_primary,
        'dedupe_keys_fallback': dedupe_fallback,
        'cleaning_rules': {
            'trim_whitespace': trim_columns,
            'lowercase': lowercase_columns,
            'digits_only': digits_only_columns,
            'amount_decimal': amount_columns,
            'date_format': {column: date_format for column in date_columns},
        },
    }


def dataframe_to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode('utf-8-sig')


def summary_to_json_bytes(summary: dict) -> bytes:
    return json.dumps(summary, indent=2, ensure_ascii=False).encode('utf-8')


def get_available_input() -> tuple[list[pd.DataFrame], list[str]]:
    source_mode = st.radio(
        'Data source',
        options=['Use bundled demo files', 'Upload my own files'],
        horizontal=True,
    )

    if source_mode == 'Use bundled demo files':
        dataframes, file_names = load_demo_data()
        st.caption('Loaded bundled sample files from the input/ folder for quick demo use.')
        return dataframes, file_names

    uploaded_files = st.file_uploader(
        'Upload CSV or XLSX files',
        type=['csv', 'xlsx'],
        accept_multiple_files=True,
    )
    if not uploaded_files:
        return [], []

    dataframes = [read_uploaded_dataframe(file.name, file.getvalue()) for file in uploaded_files]
    file_names = [file.name for file in uploaded_files]
    return dataframes, file_names


def main() -> None:
    st.set_page_config(page_title='Python File Automation Demo', page_icon='📁', layout='wide')
    st.title('Python File Automation Demo UI')
    st.write(
        'Configure field mapping and cleanup rules through a simple interface instead of editing raw JSON files.'
    )

    base_aliases = load_column_aliases()
    base_rules = load_rules()

    dataframes, file_names = get_available_input()
    if not dataframes:
        st.info('Add files or use the bundled demo files to start.')
        return

    source_dataframe = pd.concat(dataframes, ignore_index=True)
    available_columns = [column for column in source_dataframe.columns if column != '_source_file']
    default_mapping = build_default_field_mapping(available_columns, base_aliases)

    st.subheader('1) Source files')
    st.write(', '.join(file_names))
    with st.expander('Preview raw data', expanded=False):
        st.dataframe(source_dataframe.head(20), use_container_width=True)

    st.subheader('2) Field mapping')
    select_options = ['— Not mapped —', *available_columns]
    selected_mapping: dict[str, str | None] = {}
    columns = st.columns(2)
    standard_fields = list(base_aliases.keys())
    for index, field in enumerate(standard_fields):
        default_value = default_mapping.get(field)
        if default_value and default_value in select_options:
            default_index = select_options.index(default_value)
        else:
            default_index = 0
        with columns[index % 2]:
            selection = st.selectbox(
                f'{field} column',
                options=select_options,
                index=default_index,
                key=f'map_{field}',
            )
            selected_mapping[field] = None if selection == '— Not mapped —' else selection

    mapped_fields = [field for field, value in selected_mapping.items() if value]
    default_required = [field for field in base_rules.get('required_columns', []) if field in standard_fields]
    default_output = [field for field in base_rules.get('output_columns', []) if field in standard_fields]
    if '_source_file' in base_rules.get('output_columns', []):
        include_source_file_default = True
    else:
        include_source_file_default = False

    st.subheader('3) Processing rules')
    left, right = st.columns(2)
    with left:
        required_columns = st.multiselect(
            'Required fields',
            options=standard_fields,
            default=default_required,
        )
        output_columns = st.multiselect(
            'Output fields',
            options=standard_fields,
            default=default_output,
        )
        include_source_file = st.checkbox('Include source file in output', value=include_source_file_default)
        dedupe_primary = st.multiselect(
            'Primary dedupe keys',
            options=standard_fields,
            default=base_rules.get('dedupe_keys_primary', []),
        )
        dedupe_fallback = st.multiselect(
            'Fallback dedupe keys',
            options=standard_fields,
            default=base_rules.get('dedupe_keys_fallback', []),
        )

    cleaning_rules = base_rules.get('cleaning_rules', {})
    with right:
        trim_columns = st.multiselect(
            'Trim whitespace',
            options=standard_fields,
            default=cleaning_rules.get('trim_whitespace', []),
        )
        lowercase_columns = st.multiselect(
            'Lowercase text',
            options=standard_fields,
            default=cleaning_rules.get('lowercase', []),
        )
        digits_only_columns = st.multiselect(
            'Digits only',
            options=standard_fields,
            default=cleaning_rules.get('digits_only', []),
        )
        amount_columns = st.multiselect(
            'Normalize amount fields',
            options=standard_fields,
            default=cleaning_rules.get('amount_decimal', []),
        )
        default_date_columns = list(cleaning_rules.get('date_format', {}).keys())
        date_columns = st.multiselect(
            'Normalize date fields',
            options=standard_fields,
            default=default_date_columns,
        )
        date_format = st.text_input('Date output format', value='%Y-%m-%d')

    generated_aliases = build_column_aliases_from_ui(selected_mapping, base_aliases)
    final_output_columns = output_columns.copy()
    if include_source_file and '_source_file' not in final_output_columns:
        final_output_columns.append('_source_file')

    generated_rules = build_rules_from_ui(
        required_columns=required_columns,
        output_columns=final_output_columns,
        dedupe_primary=dedupe_primary,
        dedupe_fallback=dedupe_fallback,
        trim_columns=trim_columns,
        lowercase_columns=lowercase_columns,
        digits_only_columns=digits_only_columns,
        amount_columns=amount_columns,
        date_columns=date_columns,
        date_format=date_format,
    )

    with st.expander('Generated config preview', expanded=False):
        preview_left, preview_right = st.columns(2)
        with preview_left:
            st.code(json.dumps(generated_aliases, indent=2, ensure_ascii=False), language='json')
        with preview_right:
            st.code(json.dumps(generated_rules, indent=2, ensure_ascii=False), language='json')

    if st.button('Run automation', type='primary', use_container_width=True):
        result = process_dataframes(
            dataframes=dataframes,
            file_names=file_names,
            column_aliases=generated_aliases,
            rules=generated_rules,
        )
        st.session_state['automation_result'] = {
            'output': result['output'],
            'rejected': result['rejected'],
            'summary': result['summary'],
            'column_aliases': generated_aliases,
            'rules': generated_rules,
        }

    if 'automation_result' not in st.session_state:
        return

    result = st.session_state['automation_result']
    summary = result['summary']

    st.subheader('4) Results')
    metrics = st.columns(4)
    metrics[0].metric('Files processed', summary['files_processed'])
    metrics[1].metric('Rows read', summary['rows_read'])
    metrics[2].metric('Rows after cleaning', summary['rows_after_cleaning'])
    metrics[3].metric('Invalid rows', summary['invalid_rows'])

    output_tab, rejected_tab, summary_tab = st.tabs(['Clean output', 'Rejected rows', 'Summary'])
    with output_tab:
        st.dataframe(result['output'], use_container_width=True)
    with rejected_tab:
        st.dataframe(result['rejected'], use_container_width=True)
    with summary_tab:
        st.json(summary)

    download_left, download_right, download_third = st.columns(3)
    with download_left:
        st.download_button(
            'Download master.csv',
            data=dataframe_to_csv_bytes(result['output']),
            file_name='master.csv',
            mime='text/csv',
            use_container_width=True,
        )
    with download_right:
        st.download_button(
            'Download rejected_rows.csv',
            data=dataframe_to_csv_bytes(result['rejected']),
            file_name='rejected_rows.csv',
            mime='text/csv',
            use_container_width=True,
        )
    with download_third:
        st.download_button(
            'Download summary.json',
            data=summary_to_json_bytes(summary),
            file_name='summary.json',
            mime='application/json',
            use_container_width=True,
        )

    with st.expander('Download generated config', expanded=False):
        config_left, config_right = st.columns(2)
        with config_left:
            st.download_button(
                'Download column_mapping.json',
                data=summary_to_json_bytes(result['column_aliases']),
                file_name='column_mapping.json',
                mime='application/json',
                use_container_width=True,
            )
        with config_right:
            st.download_button(
                'Download rules.json',
                data=summary_to_json_bytes(result['rules']),
                file_name='rules.json',
                mime='application/json',
                use_container_width=True,
            )


if __name__ == '__main__':
    main()
