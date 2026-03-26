from __future__ import annotations

import io
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.cleaner import normalize_header
from src.config import INPUT_DIR, load_column_aliases, load_rules
from src.pipeline import process_dataframes, process_urls
from src.url_loader import load_urls_from_file, parse_pasted_urls

WEB_FIELDS = [
    'source_url',
    'page_title',
    'meta_description',
    'h1',
    'emails_found',
    'phones_found',
    'fetch_status',
    'fetch_error',
]
WEB_EXTRACTABLE_FIELDS = ['page_title', 'meta_description', 'h1', 'emails_found', 'phones_found']


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


def format_multivalue_text(value: object) -> str:
    if value is None or pd.isna(value):
        return '(none)'
    text_value = str(value).strip()
    if not text_value:
        return '(none)'
    parts = [part.strip() for part in text_value.split(';') if part.strip()]
    return '\n'.join(parts) if parts else text_value


def build_extracted_preview_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    preview = dataframe.copy()
    for column in ('emails_found', 'phones_found'):
        if column in preview.columns:
            preview[column] = preview[column].apply(format_multivalue_text)
    return preview.fillna('')


def get_available_input() -> dict:
    source_mode = st.radio(
        'Data source',
        options=[
            'Use bundled demo files',
            'Upload my own files',
            'Enter a single URL',
            'Upload a URL list',
            'Paste a URL list',
        ],
    )

    if source_mode == 'Use bundled demo files':
        dataframes, file_names = load_demo_data()
        st.caption('Loaded bundled sample files from the input/ folder for quick demo use.')
        return {'kind': 'files', 'dataframes': dataframes, 'file_names': file_names}

    if source_mode == 'Upload my own files':
        uploaded_files = st.file_uploader(
            'Upload CSV or XLSX files',
            type=['csv', 'xlsx'],
            accept_multiple_files=True,
        )
        if not uploaded_files:
            return {'kind': 'files', 'dataframes': [], 'file_names': []}

        dataframes = [read_uploaded_dataframe(file.name, file.getvalue()) for file in uploaded_files]
        file_names = [file.name for file in uploaded_files]
        return {'kind': 'files', 'dataframes': dataframes, 'file_names': file_names}

    if source_mode == 'Enter a single URL':
        url = st.text_input('Public webpage URL', placeholder='https://example.com')
        urls = [url] if url else []
        return {'kind': 'web', 'urls': urls, 'labels': urls}

    if source_mode == 'Upload a URL list':
        uploaded_url_file = st.file_uploader('Upload a CSV or TXT URL list', type=['csv', 'txt', 'md'])
        if not uploaded_url_file:
            return {'kind': 'web', 'urls': [], 'labels': []}
        try:
            urls = load_urls_from_file(uploaded_url_file.name, uploaded_url_file.getvalue())
        except ValueError as exc:
            st.error(str(exc))
            return {'kind': 'web', 'urls': [], 'labels': []}
        return {'kind': 'web', 'urls': urls, 'labels': [uploaded_url_file.name]}

    pasted_urls = st.text_area('Paste one URL per line', placeholder='https://example.com\nhttps://www.python.org')
    urls = parse_pasted_urls(pasted_urls) if pasted_urls else []
    return {'kind': 'web', 'urls': urls, 'labels': ['pasted_url_list'] if urls else []}


def main() -> None:
    st.set_page_config(page_title='Python File + Web Data Automation Demo', page_icon='📁', layout='wide')
    st.title('Python File + Web Data Automation Demo')
    st.write(
        'Combine file processing with lightweight public webpage data extraction, then clean, deduplicate, and export the results through a simple interface.'
    )

    base_aliases = load_column_aliases()
    base_rules = load_rules()

    source = get_available_input()
    source_kind = source['kind']

    if source_kind == 'files' and not source.get('dataframes'):
        st.info('Add files or use the bundled demo files to start.')
        return
    if source_kind == 'web' and not source.get('urls'):
        st.info('Enter a URL or provide a URL list to start.')
        return

    generated_aliases = base_aliases.copy()
    selected_web_fields = WEB_EXTRACTABLE_FIELDS.copy()

    if source_kind == 'files':
        dataframes = source['dataframes']
        file_names = source['file_names']
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
            default_index = select_options.index(default_value) if default_value in select_options else 0
            with columns[index % 2]:
                selection = st.selectbox(
                    f'{field} column',
                    options=select_options,
                    index=default_index,
                    key=f'map_{field}',
                )
                selected_mapping[field] = None if selection == '— Not mapped —' else selection

        generated_aliases = build_column_aliases_from_ui(selected_mapping, base_aliases)
        processing_fields = list(base_aliases.keys())
        default_required = [field for field in base_rules.get('required_columns', []) if field in processing_fields]
        default_output = [field for field in base_rules.get('output_columns', []) if field in processing_fields]
        include_source_file_default = '_source_file' in base_rules.get('output_columns', [])
        default_dedupe_primary = base_rules.get('dedupe_keys_primary', [])
        default_dedupe_fallback = base_rules.get('dedupe_keys_fallback', [])
    else:
        urls = source['urls']
        st.subheader('1) URL intake')
        st.write(f'{len(urls)} URL(s) ready for extraction.')
        with st.expander('Preview URLs', expanded=False):
            st.write(urls)

        st.subheader('2) Web extraction fields')
        selected_web_fields = st.multiselect(
            'Select fields to extract from public webpages',
            options=WEB_EXTRACTABLE_FIELDS,
            default=WEB_EXTRACTABLE_FIELDS,
        )
        st.caption('The extractor always includes source_url, fetch_status, and fetch_error for traceability.')
        processing_fields = WEB_FIELDS
        default_required = ['source_url']
        default_output = ['source_url', *selected_web_fields, 'fetch_status', 'fetch_error']
        include_source_file_default = False
        default_dedupe_primary = ['source_url']
        default_dedupe_fallback = ['page_title']

    st.subheader('3) Processing rules')
    left, right = st.columns(2)
    with left:
        required_columns = st.multiselect(
            'Required fields',
            options=processing_fields,
            default=default_required,
        )
        output_columns = st.multiselect(
            'Output fields',
            options=processing_fields,
            default=default_output,
        )
        include_source_file = st.checkbox('Include source file in output', value=include_source_file_default)
        dedupe_primary = st.multiselect(
            'Primary dedupe keys',
            options=processing_fields,
            default=[field for field in default_dedupe_primary if field in processing_fields],
        )
        dedupe_fallback = st.multiselect(
            'Fallback dedupe keys',
            options=processing_fields,
            default=[field for field in default_dedupe_fallback if field in processing_fields],
        )

    cleaning_rules = base_rules.get('cleaning_rules', {})
    with right:
        trim_default = [field for field in cleaning_rules.get('trim_whitespace', []) if field in processing_fields]
        lower_default = [field for field in cleaning_rules.get('lowercase', []) if field in processing_fields]
        digits_default = [field for field in cleaning_rules.get('digits_only', []) if field in processing_fields]
        amount_default = [field for field in cleaning_rules.get('amount_decimal', []) if field in processing_fields]
        date_default = [field for field in cleaning_rules.get('date_format', {}).keys() if field in processing_fields]

        trim_columns = st.multiselect('Trim whitespace', options=processing_fields, default=trim_default)
        lowercase_columns = st.multiselect('Lowercase text', options=processing_fields, default=lower_default)
        digits_only_columns = st.multiselect('Digits only', options=processing_fields, default=digits_default)
        amount_columns = st.multiselect('Normalize amount fields', options=processing_fields, default=amount_default)
        date_columns = st.multiselect('Normalize date fields', options=processing_fields, default=date_default)
        date_format = st.text_input('Date output format', value='%Y-%m-%d')

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

    button_label = 'Run file automation' if source_kind == 'files' else 'Fetch and process URLs'
    if st.button(button_label, type='primary', use_container_width=True):
        if source_kind == 'files':
            result = process_dataframes(
                dataframes=source['dataframes'],
                file_names=source['file_names'],
                column_aliases=generated_aliases,
                rules=generated_rules,
            )
        else:
            result = process_urls(
                urls=source['urls'],
                extract_fields=selected_web_fields,
                column_aliases=generated_aliases,
                rules=generated_rules,
            )
        st.session_state['automation_result'] = {
            'output': result['output'],
            'rejected': result['rejected'],
            'summary': result['summary'],
            'column_aliases': generated_aliases,
            'rules': generated_rules,
            'extracted': result.get('extracted'),
        }

    if 'automation_result' not in st.session_state:
        return

    result = st.session_state['automation_result']
    summary = result['summary']

    st.subheader('4) Results')
    metrics = st.columns(4)
    metric_label = 'Sources processed' if summary.get('source_mode') == 'web' else 'Files processed'
    metric_value = summary.get('urls_processed', summary.get('files_processed', 0))
    metrics[0].metric(metric_label, metric_value)
    metrics[1].metric('Rows read', summary['rows_read'])
    metrics[2].metric('Rows after cleaning', summary['rows_after_cleaning'])
    metrics[3].metric('Invalid rows', summary['invalid_rows'])
    if summary.get('source_mode') == 'web':
        web_metrics = st.columns(2)
        web_metrics[0].metric('Successful fetches', summary.get('successful_fetches', 0))
        web_metrics[1].metric('Failed fetches', summary.get('failed_fetches', 0))

    tab_names = ['Clean output', 'Rejected rows', 'Summary']
    if result.get('extracted') is not None:
        tab_names.insert(0, 'Extracted raw data')
    tabs = st.tabs(tab_names)
    tab_lookup = dict(zip(tab_names, tabs))

    if 'Extracted raw data' in tab_lookup:
        with tab_lookup['Extracted raw data']:
            extracted = result['extracted'].copy()
            st.caption('Preview of the raw extracted webpage fields before the final output step.')
            st.dataframe(build_extracted_preview_dataframe(extracted), use_container_width=True, hide_index=True)

            if not extracted.empty:
                st.markdown('#### Full extracted contact values')
                for index, row in extracted.iterrows():
                    label = row.get('source_url') or f'Record {index + 1}'
                    with st.expander(str(label), expanded=False):
                        if 'page_title' in extracted.columns:
                            st.write(f"**Page title:** {row.get('page_title') or '(none)'}")
                        st.write('**Emails found**')
                        st.code(format_multivalue_text(row.get('emails_found')))
                        st.write('**Phones found**')
                        st.code(format_multivalue_text(row.get('phones_found')))
                        st.write(f"**Fetch status:** {row.get('fetch_status') or '(none)'}")
                        if row.get('fetch_error'):
                            st.write(f"**Fetch error:** {row.get('fetch_error')}")
    with tab_lookup['Clean output']:
        st.dataframe(result['output'], use_container_width=True)
    with tab_lookup['Rejected rows']:
        st.dataframe(result['rejected'], use_container_width=True)
    with tab_lookup['Summary']:
        st.json(summary)

    download_columns = st.columns(4 if result.get('extracted') is not None else 3)
    with download_columns[0]:
        st.download_button('Download master.csv', data=dataframe_to_csv_bytes(result['output']), file_name='master.csv', mime='text/csv', use_container_width=True)
    with download_columns[1]:
        st.download_button('Download rejected_rows.csv', data=dataframe_to_csv_bytes(result['rejected']), file_name='rejected_rows.csv', mime='text/csv', use_container_width=True)
    with download_columns[2]:
        st.download_button('Download summary.json', data=summary_to_json_bytes(summary), file_name='summary.json', mime='application/json', use_container_width=True)
    if result.get('extracted') is not None:
        with download_columns[3]:
            st.download_button('Download extracted_web_records.csv', data=dataframe_to_csv_bytes(result['extracted']), file_name='extracted_web_records.csv', mime='text/csv', use_container_width=True)

    with st.expander('Download generated config', expanded=False):
        config_left, config_right = st.columns(2)
        with config_left:
            st.download_button('Download column_mapping.json', data=summary_to_json_bytes(result['column_aliases']), file_name='column_mapping.json', mime='application/json', use_container_width=True)
        with config_right:
            st.download_button('Download rules.json', data=summary_to_json_bytes(result['rules']), file_name='rules.json', mime='application/json', use_container_width=True)


if __name__ == '__main__':
    main()
