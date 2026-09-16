"""Tests for the Dukascopy → canonical-schema acquisition adapter.

These tests exercise parsing and normalization in isolation (no network).
Synthetic frames use the exact raw Dukascopy schema produced by dukascopy-node:

    timestamp,open,high,low,close,volume
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backtest.data.dukascopy_acquire import (
    CALL_ATTEMPTS,
    CANONICAL_COLUMNS,
    DUKAS_RAW_COLUMNS,
    _chunk_data_complete,
    _chunk_ranges,
    _chunk_csv_name,
    _download_chunk,
    _sleep_before_retry,
    dukascopy_to_canonical,
    read_dukascopy_csv,
)

POINT_VALUES = {
    "EURUSD": 0.00001,
    "EURGBP": 0.00001,
    "EURJPY": 0.001,
    "GBPUSD": 0.00001,
}


def _raw_frame(
    symbol: str,
    n: int = 3,
    bid_close: float | None = None,
    ask_close: float | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build synthetic raw-schema bid/ask frames for *symbol*.

    Prices are chosen to give a round-point spread for the symbol's point size.
    """
    point = POINT_VALUES[symbol]
    base = bid_close if bid_close is not None else 1.2345
    ask = ask_close if ask_close is not None else base + 8.0 * point

    start_ms = 1748811600000  # 2025-06-01 21:00:00 UTC
    bid_data = {
        "timestamp": [start_ms + i * 300_000 for i in range(n)],
        "open": [base for _ in range(n)],
        "high": [base + 1.0 * point for _ in range(n)],
        "low": [base - 1.0 * point for _ in range(n)],
        "close": [base + i * 0.5 * point for i in range(n)],
        "volume": [i * 1_000_000 + 1 for i in range(n)],
    }
    ask_data = {
        "timestamp": [start_ms + i * 300_000 for i in range(n)],
        "open": [ask for _ in range(n)],
        "high": [ask + 1.0 * point for _ in range(n)],
        "low": [ask - 1.0 * point for _ in range(n)],
        "close": [ask + i * 0.5 * point for i in range(n)],
        "volume": [i * 900_000 + 1 for i in range(n)],
    }
    return pd.DataFrame(bid_data), pd.DataFrame(ask_data)


def _parse_raw(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the same transformation as ``read_dukascopy_csv`` (no file)."""
    parsed = df.rename(columns={"volume": "tick_volume"}).copy()
    parsed["time"] = pd.to_datetime(parsed["timestamp"], unit="ms", utc=True).dt.tz_localize(None)
    return parsed[["time", "open", "high", "low", "close", "tick_volume"]].copy()


def _parsed_frames(symbol: str, **kwargs) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Raw-schema bid/ask frames converted to parsed schema for *symbol*."""
    bid_raw, ask_raw = _raw_frame(symbol, **kwargs)
    return _parse_raw(bid_raw), _parse_raw(ask_raw)


# --- Raw-schema parsing ---------------------------------------------------

def test_read_dukascopy_csv_maps_raw_schema(tmp_path):
    """Raw volume → tick_volume, timestamp → naive-UTC time, OHLC preserved."""
    raw = pd.DataFrame({
        "timestamp": [1748811600000, 1748811900000],
        "open": [1.13439, 1.13435],
        "high": [1.13439, 1.13453],
        "low": [1.13436, 1.13435],
        "close": [1.13436, 1.13443],
        "volume": [6400000, 41100000],
    })
    path = tmp_path / "eurusd-m5-bid.csv"
    raw.to_csv(path, index=False)

    parsed = read_dukascopy_csv(path)

    assert list(parsed.columns) == ["time", "open", "high", "low", "close", "tick_volume"]
    assert parsed["time"].tolist() == pd.to_datetime(
        ["2025-06-01 21:00:00", "2025-06-01 21:05:00"]
    ).tolist()
    assert parsed["tick_volume"].tolist() == [6400000, 41100000]
    assert parsed["open"].tolist() == [1.13439, 1.13435]
    assert parsed["close"].tolist() == [1.13436, 1.13443]


def test_read_dukascopy_csv_timestamp_is_naive_utc(tmp_path):
    raw = pd.DataFrame({
        "timestamp": [1748811600000],
        "open": [1.0], "high": [1.1], "low": [0.9], "close": [1.05], "volume": [5],
    })
    path = tmp_path / "row.csv"
    raw.to_csv(path, index=False)
    parsed = read_dukascopy_csv(path)
    assert parsed["time"].dt.tz is None  # naive UTC, no tzinfo
    assert parsed["time"].iloc[0] == pd.Timestamp("2025-06-01 21:00:00")


def test_read_dukascopy_csv_missing_column_raises(tmp_path):
    raw = pd.DataFrame({"timestamp": [1], "open": [1.0], "high": [1.1],
                        "low": [0.9], "close": [1.05]})  # no volume
    path = tmp_path / "bad.csv"
    raw.to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing expected columns"):
        read_dukascopy_csv(path)


def test_read_dukascopy_csv_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_dukascopy_csv(tmp_path / "none.csv")


# --- Canonical normalization ----------------------------------------------

@pytest.mark.parametrize("symbol", POINT_VALUES)
def test_canonical_output_columns_and_alignment(symbol):
    bid, ask = _parsed_frames(symbol)
    canon = dukascopy_to_canonical(bid, ask, symbol)

    assert list(canon.columns) == CANONICAL_COLUMNS
    assert len(canon) == len(bid)  # all timestamps aligned


@pytest.mark.parametrize(
    ("symbol", "bid_close", "ask_close", "expected_spread_points"),
    [
        ("EURUSD", 1.23450, 1.23458, 8),   # point 1e-5 → 8 points
        ("EURGBP", 0.84226, 0.84236, 10),  # point 1e-5 → 10 points
        ("EURJPY", 163.450, 163.452, 2),   # point 1e-3 → 2 points
        ("GBPUSD", 1.34625, 1.34631, 6),   # point 1e-5 → 6 points
    ],
)
def test_spread_computed_from_bid_ask(symbol, bid_close, ask_close, expected_spread_points):
    bid, ask = _parsed_frames(symbol, bid_close=bid_close, ask_close=ask_close)
    canon = dukascopy_to_canonical(bid, ask, symbol)
    assert int(canon["spread"].iloc[0]) == expected_spread_points
    assert (canon["spread"] > 0).all()


def test_ohlc_taken_from_bid_side():
    bid, ask = _parsed_frames("EURUSD")
    bid.loc[0, "close"] = 9.99999  # distinctive bid-only value
    canon = dukascopy_to_canonical(bid, ask, "EURUSD")
    assert canon["close"].iloc[0] == 9.99999


def test_tick_volume_preserved_not_fabricated():
    bid, ask = _parsed_frames("EURUSD")
    canon = dukascopy_to_canonical(bid, ask, "EURUSD")
    assert canon["tick_volume"].tolist() == [1, 1_000_001, 2_000_001]
    assert (canon["tick_volume"] > 0).all()


def test_real_volume_is_zero_unavailable():
    """Dukascopy does not provide real volume → 0, documented, not observed."""
    bid, ask = _parsed_frames("EURUSD")
    canon = dukascopy_to_canonical(bid, ask, "EURUSD")
    assert (canon["real_volume"] == 0).all()


def test_no_overlap_raises():
    bid, ask = _parsed_frames("EURUSD", n=2)
    ask["time"] = ask["time"] + pd.Timedelta(days=1)  # shift out of overlap
    with pytest.raises(ValueError, match="No overlapping bid/ask timestamps"):
        dukascopy_to_canonical(bid, ask, "EURUSD")


def test_empty_frames_raise():
    parsed_columns = ["time", "open", "high", "low", "close", "tick_volume"]
    empty = pd.DataFrame(columns=parsed_columns)
    with pytest.raises(ValueError, match="Empty Dukascopy data"):
        dukascopy_to_canonical(empty.copy(), empty.copy(), "EURUSD")


def test_duplicate_timestamps_deduplicated():
    bid, ask = _parsed_frames("EURUSD", n=2)
    dup = pd.concat([bid, bid.iloc[[0]]], ignore_index=True)
    canon = dukascopy_to_canonical(dup, ask, "EURUSD")
    assert canon["time"].is_unique


@pytest.mark.parametrize("symbol", POINT_VALUES)
def test_all_four_symbols_e2e(tmp_path, symbol):
    """End-to-end: raw CSV on disk → canonical DataFrame for each symbol."""
    bid, ask = _raw_frame(symbol, n=4)
    bid_path = tmp_path / f"{symbol.lower()}-m5-bid.csv"
    ask_path = tmp_path / f"{symbol.lower()}-m5-ask.csv"
    bid.to_csv(bid_path, index=False)
    ask.to_csv(ask_path, index=False)

    canon = dukascopy_to_canonical(
        read_dukascopy_csv(bid_path),
        read_dukascopy_csv(ask_path),
        symbol,
    )
    assert len(canon) == 4
    assert (canon["high"] >= canon["low"]).all()
    assert (canon["high"] >= canon["low"]).all()
    assert canon["time"].is_monotonic_increasing
    assert (canon["spread"] > 0).all()


# --- Chunking / resumability ----------------------------------------------

def test_chunk_ranges_monthly_covers_full_range_without_overlap():
    chunks = _chunk_ranges("2021-01-01", "2021-04-01", months=1)
    # Non-overlapping, sequential, exact outer bounds.
    prev_start = pd.Timestamp("2021-01-01")
    prev_end = None
    for from_str, to_str in chunks:
        assert from_str < to_str
        if prev_end is not None:
            assert from_str == prev_end  # contiguous, no gap and no overlap
        prev_end = to_str
    assert chunks[0][0] == "2021-01-01"
    assert chunks[-1][1] == "2021-04-01"
    assert len(chunks) == 3  # Jan, Feb, Mar


def test_chunk_ranges_respects_requested_bounds():
    chunks = _chunk_ranges("2021-01-15", "2021-03-20", months=1)
    assert chunks[0] == ["2021-01-15", "2021-02-01"]
    assert chunks[-1] == ["2021-03-01", "2021-03-20"]
    assert len(chunks) == 3


def test_chunk_ranges_quarter_grid():
    chunks = _chunk_ranges("2021-01-01", "2022-01-01", months=3)
    # Boundaries fall on Jan/Apr/Jul/Oct starts.
    assert chunks[0] == ["2021-01-01", "2021-04-01"]
    assert chunks[1] == ["2021-04-01", "2021-07-01"]
    assert chunks[-1] == ["2021-10-01", "2022-01-01"]
    assert len(chunks) == 4


def test_chunk_ranges_invalid_month_argument():
    with pytest.raises(ValueError, match=">= 1"):
        _chunk_ranges("2021-01-01", "2021-04-01", months=0)


def test_chunk_ranges_rejects_inverted_and_zero_ranges():
    with pytest.raises(ValueError, match="must be after"):
        _chunk_ranges("2021-04-01", "2021-01-01")


def test_chunk_ranges_daily_grid():
    chunks = _chunk_ranges("2021-01-01", "2021-01-04", months=None, days=1)
    assert chunks == [
        ["2021-01-01", "2021-01-02"],
        ["2021-01-02", "2021-01-03"],
        ["2021-01-03", "2021-01-04"],
    ]


def test_chunk_ranges_weekly_grid_contiguous_with_boundaries_honored():
    chunks = _chunk_ranges("2021-01-01", "2021-01-25", months=None, days=7)
    assert chunks[0] == ["2021-01-01", "2021-01-07"]
    assert chunks[-1][1] == "2021-01-25"
    # Contiguous: each chunk starts where the previous ended, no overlap/gap.
    for prev, cur in zip(chunks, chunks[1:]):
        assert prev[1] == cur[0]
    # Boundary dates are deterministic (fixed absolute grid, not range-relative).
    assert chunks == [
        ["2021-01-01", "2021-01-07"],
        ["2021-01-07", "2021-01-14"],
        ["2021-01-14", "2021-01-21"],
        ["2021-01-21", "2021-01-25"],
    ]


def test_chunk_ranges_rejects_both_month_and_days():
    with pytest.raises(ValueError, match="only one of months= or days"):
        _chunk_ranges("2021-01-01", "2021-04-01", months=1, days=7)


def test_chunk_ranges_rejects_invalid_day_argument():
    with pytest.raises(ValueError, match="chunk days must be >= 1"):
        _chunk_ranges("2021-01-01", "2021-04-01", months=None, days=0)


def test_main_rejects_both_chunk_options():
    from backtest.data.dukascopy_acquire import main
    argv = [
        "--symbol", "EURGBP", "--from", "2021-01-01", "--to", "2021-01-08",
        "--chunk-months", "1", "--chunk-days", "7",
    ]
    with pytest.raises(SystemExit):
        main(argv)


def test_download_m5_passes_day_chunks_to_chunk_ranges(tmp_path, monkeypatch):
    """chunk_days is wired through to _chunk_ranges with months=None."""
    from backtest.data import dukascopy_acquire as mod

    captured = {}

    def fake_chunk_ranges(date_from, date_to, months=None, days=None):
        captured["months"] = months
        captured["days"] = days
        return [["2021-01-01", "2021-07-01"]]

    monkeypatch.setattr(mod, "_chunk_ranges", fake_chunk_ranges)

    def fake_download(inst, date_from, date_to, price_type, out_dir):
        return out_dir / f"{inst}-m5-{price_type}-{date_from}-{date_to}.csv"

    monkeypatch.setattr(mod, "_download_chunk", fake_download)
    raw = pd.DataFrame({
        "timestamp": [1748811600000, 1748811900000],
        "open": [1.0, 1.0], "high": [1.1, 1.1], "low": [0.9, 0.9],
        "close": [1.05, 1.05], "volume": [100, 200],
    })
    raw.to_csv(tmp_path / "eurgbp-m5-bid-2021-01-01-2021-07-01.csv", index=False)
    raw.to_csv(tmp_path / "eurgbp-m5-ask-2021-01-01-2021-07-01.csv", index=False)

    df = mod.download_m5("EURGBP", "2021-01-01", "2021-07-01",
                         out_dir=tmp_path, chunk_days=7)
    assert captured == {"months": None, "days": 7}
    assert len(df) == 2


def test_download_m5_defaults_to_month_chunks(tmp_path, monkeypatch):
    """chunk_days=None keeps the existing monthly-chunk behavior."""
    from backtest.data import dukascopy_acquire as mod

    captured = {}

    def fake_chunk_ranges(date_from, date_to, months=None, days=None):
        captured["months"] = months
        captured["days"] = days
        return [["2021-01-01", "2021-02-01"]]

    monkeypatch.setattr(mod, "_chunk_ranges", fake_chunk_ranges)
    monkeypatch.setattr(mod, "_download_chunk",
                        lambda inst, df, dt, pt, out: out / f"{inst}-m5-{pt}-{df}-{dt}.csv")
    raw = pd.DataFrame({
        "timestamp": [1748811600000, 1748811900000],
        "open": [1.0, 1.0], "high": [1.1, 1.1], "low": [0.9, 0.9],
        "close": [1.05, 1.05], "volume": [100, 200],
    })
    raw.to_csv(tmp_path / "eurgbp-m5-bid-2021-01-01-2021-02-01.csv", index=False)
    raw.to_csv(tmp_path / "eurgbp-m5-ask-2021-01-01-2021-02-01.csv", index=False)

    df = mod.download_m5("EURGBP", "2021-01-01", "2021-02-01", out_dir=tmp_path)
    assert captured == {"months": mod.CHUNK_MONTHS, "days": None}
    assert len(df) == 2


def test_download_chunk_labels_rate_limited_failure(tmp_path, monkeypatch):
    """a persistent HTTP 429 failure is surfaced with an explicit explanation."""
    from backtest.data import dukascopy_acquire as mod

    def failing_cli(*args, **kwargs):
        raise RuntimeError("dukascopy-node failed for eurgbp bid ... "
                           "Something went wrong: Request failed with status 429")

    monkeypatch.setattr(mod, "_run_dukascopy_cli", failing_cli)
    monkeypatch.setattr(mod, "_sleep_before_retry", lambda *a, **k: 0)

    with pytest.raises(RuntimeError) as ei:
        _download_chunk("eurgbp", "2021-01-01", "2021-02-01", "bid", tmp_path)
    assert "429" in str(ei.value)
    assert "rate-limited" in str(ei.value).lower()


def test_chunk_csv_name_is_deterministic():
    assert _chunk_csv_name("eurgbp", "2021-01-01", "2021-02-01", "bid") == \
        "eurgbp-m5-bid-2021-01-01-2021-02-01.csv"


def _write_raw_chunk_csv(path: Path, last_ms: int):
    raw = pd.DataFrame({
        "timestamp": [1748811600000, last_ms],
        "open": [1.0, 1.0],
        "high": [1.1, 1.1],
        "low": [0.9, 0.9],
        "close": [1.05, 1.05],
        "volume": [100, 200],
    })
    raw.to_csv(path, index=False)


@pytest.mark.parametrize(
    ("last_ms", "date_to", "expected"),
    [
        # UTC 2021-03-26 (Fri) → within 10 days of 2021-04-01 → complete
        (1616784000000, "2021-04-01", True),
        # UTC 2021-03-01 → 31 days before 2021-04-01 → partial
        (1614556800000, "2021-04-01", False),
    ],
)
def test_chunk_data_complete(tmp_path, last_ms, date_to, expected):
    p = tmp_path / "chunk.csv"
    _write_raw_chunk_csv(p, last_ms)
    assert _chunk_data_complete(p, date_to) is expected


def test_chunk_data_complete_empty_file(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("timestamp,open,high,low,close,volume\n")
    assert _chunk_data_complete(p, "2021-04-01") is False


def test_download_chunk_reuses_complete_artifact(tmp_path, monkeypatch):
    """Completed chunk CSVs are reused; the CLI is not re-invoked."""
    from backtest.data import dukascopy_acquire as mod

    monkeypatch.setattr(mod, "_run_dukascopy_cli", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("CLI must not be called when chunk is complete")
    ))
    chunk_path = tmp_path / _chunk_csv_name("eurgbp", "2021-01-01", "2021-02-01", "bid")
    _write_raw_chunk_csv(chunk_path, 1612044000000)  # 2021-01-30 → close to end

    result = _download_chunk("eurgbp", "2021-01-01", "2021-02-01", "bid", tmp_path)
    assert result == chunk_path


def test_download_chunk_redownloads_partial_artifact(tmp_path, monkeypatch):
    """A partial file is deleted and re-downloaded, then reused on resume."""
    from backtest.data import dukascopy_acquire as mod

    calls = {"n": 0}
    chunk_path = tmp_path / _chunk_csv_name("eurgbp", "2021-01-01", "2021-02-01", "bid")

    def fake_cli(*args, **kwargs):
        calls["n"] += 1
        # Success: write a complete chunk this time.
        _write_raw_chunk_csv(chunk_path, 1612044000000)
        return chunk_path

    monkeypatch.setattr(mod, "_run_dukascopy_cli", fake_cli)

    _write_raw_chunk_csv(chunk_path, 1611014400000)  # partial: last bar 2021-01-19
    result = _download_chunk("eurgbp", "2021-01-01", "2021-02-01", "bid", tmp_path)
    assert result == chunk_path
    assert calls["n"] == 1
    assert _chunk_data_complete(chunk_path, "2021-02-01")


def test_download_chunk_retries_then_raises(tmp_path, monkeypatch):
    """Persistent CLI failure raises after CALL_ATTEMPTS attempts."""
    from backtest.data import dukascopy_acquire as mod

    calls = {"n": 0}

    def failing_cli(*args, **kwargs):
        calls["n"] += 1
        raise RuntimeError("dukascopy-node failed (simulated)")

    monkeypatch.setattr(mod, "_run_dukascopy_cli", failing_cli)
    monkeypatch.setattr(mod, "_sleep_before_retry", lambda *a, **k: 0)

    with pytest.raises(RuntimeError, match="failed after"):
        _download_chunk("eurgbp", "2021-01-01", "2021-02-01", "bid", tmp_path)
    assert calls["n"] == CALL_ATTEMPTS


def test_sleep_before_retry_uses_longer_backoff_for_429(monkeypatch):
    from backtest.data import dukascopy_acquire as mod

    sleeps = []
    monkeypatch.setattr(mod.time, "sleep", lambda s: sleeps.append(s))

    mod._sleep_before_retry(1, "Request failed with status 429")
    mod._sleep_before_retry(2, "Some other error")
    assert sleeps[0] >= 30  # rate limits start with a longer backoff
    assert sleeps[1] >= mod.CALL_RETRY_SLEEP_SECONDS * 2  # exponential growth