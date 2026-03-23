from __future__ import annotations

import pandas as pd


def merge_dataframes(dataframes: list[pd.DataFrame]) -> pd.DataFrame:
    if not dataframes:
        return pd.DataFrame()
    return pd.concat(dataframes, ignore_index=True)
