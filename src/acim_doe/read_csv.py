# read_csv.py
from pathlib import Path
import pandas as pd

def read(csv_path) -> pd.DataFrame:
    raw = pd.read_csv(csv_path, skiprows=26)
    df = raw.iloc[3:].dropna(axis=1, how="all").copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    for column in df.columns.drop("Timestamp"):  # convert all columns to numeric except "timestamp"
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.reset_index(drop=True)

    return df