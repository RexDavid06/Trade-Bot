"""Shared helpers for market-research modules: data loading and output
management.  Keeps every study reproducible (records dataset + date range in
each output) without duplicating boilerplate.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ..config import PathConfig
from .common import PIP, HORIZONS


def load_m5() -> pd.DataFrame:
    """Load the default EURUSD M5 CSV, parse time, sorted chronologically."""
    pcfg = PathConfig()
    df = pd.read_csv(pcfg.data_file)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df


def dataset_header(df: pd.DataFrame) -> str:
    """Markdown header block describing the exact dataset used."""
    return (
        f"- **Dataset**: `{PathConfig().data_file.name}`\n"
        f"- **Date range**: `{df['time'].min()}` .. `{df['time'].max()}`\n"
        f"- **Candles**: `{len(df):,}`\n"
        f"- **Timeframe**: M5 (EURUSD)\n"
    )


def write_study(out_path: Path, title: str, df: pd.DataFrame, body: str,
                extra_meta: dict | None = None) -> None:
    """Write a standard markdown study report with reproducible metadata."""
    L = [f"# {title}", "", "## Dataset", "", dataset_header(df)]
    if extra_meta:
        L.append("## Configuration")
        L.append("")
        for k, v in extra_meta.items():
            L.append(f"- **{k}**: `{v}`")
        L.append("")
    L.append(body)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def write_json(data: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=float)
