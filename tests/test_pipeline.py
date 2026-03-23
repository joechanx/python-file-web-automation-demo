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
