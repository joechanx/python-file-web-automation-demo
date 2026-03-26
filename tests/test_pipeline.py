from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import process_dataframes  # noqa: E402
from src.config import load_column_aliases, load_rules  # noqa: E402


def test_process_dataframes_returns_summary_and_output() -> None:
    dataframes = [
        pd.DataFrame(
            {
                'Email Address': ['Alice@Example.com', 'Alice@Example.com'],
                'Full Name': [' Alice ', 'Alice'],
                'Mobile': ['0912-345-678', '0912345678'],
                'Signup Date': ['2026/03/01', '2026/03/01'],
                'Price': ['$1,000', '$1,000'],
            }
        )
    ]

    result = process_dataframes(
        dataframes=dataframes,
        file_names=['sample.csv'],
        column_aliases=load_column_aliases(),
        rules=load_rules(),
    )

    assert result['summary']['files_processed'] == 1
    assert result['summary']['duplicates_removed'] == 1
    assert list(result['output'].columns) == load_rules()['output_columns']
    assert result['output'].iloc[0]['amount'] == '1000.00'



def test_process_urls_extracts_and_processes_web_records() -> None:
    from src.pipeline import process_urls

    def fake_fetch(url: str) -> str:
        if 'bad' in url:
            raise ValueError('fetch failed')
        return """
        <html>
          <head><title>Example Title</title><meta name="description" content="Demo description"></head>
          <body><h1>Example Heading</h1><p>Email contact@example.com and sales@example.com</p></body>
        </html>
        """

    web_rules = {
        'required_columns': ['source_url'],
        'output_columns': ['source_url', 'page_title', 'meta_description', 'h1', 'emails_found', 'fetch_status', 'fetch_error'],
        'drop_columns': [],
        'dedupe_keys_primary': ['source_url'],
        'dedupe_keys_fallback': ['page_title'],
        'cleaning_rules': {
            'trim_whitespace': ['source_url', 'page_title', 'meta_description', 'h1', 'emails_found', 'fetch_status', 'fetch_error'],
            'lowercase': [],
            'digits_only': [],
            'amount_decimal': [],
            'date_format': {},
        },
    }

    result = process_urls(
        urls=['https://example.com', 'https://bad.example.com'],
        extract_fields=['page_title', 'meta_description', 'h1', 'emails_found'],
        fetch_html_func=fake_fetch,
        rules=web_rules,
    )

    assert result['summary']['source_mode'] == 'web'
    assert result['summary']['urls_processed'] == 2
    assert result['summary']['failed_fetches'] == 1
    assert 'source_url' in result['output'].columns
    assert result['output'].iloc[0]['source_url'] == 'https://example.com'
    assert len(result['extracted']) == 2
    assert result['extracted'].iloc[0]['emails_found'] == 'contact@example.com; sales@example.com'
    assert result['output'].iloc[0]['emails_found'] == 'contact@example.com; sales@example.com'
