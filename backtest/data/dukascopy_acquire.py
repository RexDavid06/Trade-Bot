"""
Dukascopy M5 data acquisition for the research project.

Downloads bid/ask M5 candles via dukascopy-node CLI, converts them to the
project's canonical schema, and computes spread from the bid/ask difference.

Raw Dukascopy schema (CSV produced by dukascopy-node with `-f csv -v -vu units`):

    timestamp  | int64  | Unix epoch, milliseconds, UTC
    open       | float64| bid (or ask) open price
    high       | float64| bid (or ask) high price
    low        | float64| bid (or ask) low price
    close      | float64| bid (or ask) close price
    volume     | int64  | aggregated tick volume for the bar (in units)

Canonical project schema (``data/{symbol}_m5.csv``):

    time        | datetime64[ns] | naive UTC timestamp
    open        | float64        | bid open
    high        | float64        | bid high
    low         | float64        | bid low
    close       | float64        | bid close
    tick_volume | int64          | mapped from Dukascopy ``volume``
    spread      | int64          | observed points = (ask_close - bid_close) / point
    real_volume | int64          | 0 (not provided by Dukascopy; documented, not observed)

Large time ranges are downloaded in small, non-overlapping chunks (default one
month per chunk). Each chunk is a separate dukascopy-node invocation with
artifact-level retries (`-r`) plus whole-command retries, and is verified before
being accepted. Completed chunks are reused on re-runs (the raw chunk CSV is the
resume marker), making the acquisition resumable/idempotent and avoiding
re-downloading already-successful periods. Partial/empty chunk artifacts are
rejected, deleted, and re-downloaded rather than being silently concatenated.

Usage:
    python -m backtest.data.dukascopy_acquire --symbol EURUSD --from 2021-01-01 --to 2026-09-10
    python -m backtest.data.dukascopy_acquire --all --from 2021-01-01 --to 2026-09-10 --chunk-months 1
    python -m backtest.data.dukascopy_acquire --symbol EURJPY --from 2021-01-01 --to 2026-09-10 --chunk-days 7

Requires: Node.js 18+ and dukascopy-node (auto-installed via npx on first run).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from ..instruments import get_instrument

DUKAS_SYMBOLS = {
    "EURUSD": "eurusd",
    "EURGBP": "eurgbp",
    "EURJPY": "eurjpy",
    "GBPUSD": "gbpusd",
}

ALL_SYMBOLS = list(DUKAS_SYMBOLS.keys())

# Columns the raw dukascopy-node CSV is expected to provide.
DUKAS_RAW_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

# Canonical per-symbol output columns (same order as the legacy MT5 CSVs).
CANONICAL_COLUMNS = ["time", "open", "high", "low", "close",
                     "tick_volume", "spread", "real_volume"]

# Per-artifact retries passed to dukascopy-node (-r).
DUKAS_CLI_RETRIES = 3
DUKAS_CLI_RETRY_PAUSE_MS = 2000

# Whole-CLI-command retries and per-call timeout.  The larger budget exists
# because Dukascopy rate-limits bursts (HTTP 429); ``_sleep_before_retry``
# extends the backoff for rate-limited chunks so an unattended run can wait out
# the throttle window, then continue (completed chunks are never re-downloaded).
CALL_ATTEMPTS = 9
CALL_RETRY_SLEEP_SECONDS = 10
CALL_RETRY_MAX_SLEEP_SECONDS = 600
CALL_TIMEOUT_SECONDS = 900

# Pause inserted between chunk pairs to lower the aggregate request rate
# towards Dukascopy's documented/observed limits (HTTP 429 throttling).
CHUNK_SLEEP_SECONDS = 8

# Default chunk span in months. Chunk boundaries are anchored to the first of
# the month, so completed chunks keep stable names for resume/idempotency.
CHUNK_MONTHS = 1

# A chunk is only accepted if its last bar is within this many days of the
# chunk end date. Partial downloads that died part-way leave a truncated CSV;
# this check rejects them so a re-download is triggered.
COMPLETENESS_TOLERANCE_DAYS = 10


def _tail(text: str | None, max_lines: int = 30, max_chars: int = 5000) -> str:
    """Return the last ``max_lines`` lines of *text* for diagnostics."""
    if not text or not text.strip():
        return "<no output>"
    lines = text.strip().splitlines()
    joined = "\n".join(lines[-max_lines:])
    if len(joined) > max_chars:
        joined = joined[-max_chars:]
    return joined


def _chunk_ranges(
    date_from: str,
    date_to: str,
    months: int | None = None,
    days: int | None = None,
) -> list[list[str]]:
    """Split ``[date_from, date_to)`` into non-overlapping chunk date pairs.

    Exactly one of *months* or *days* must be given.  Internal boundaries fall
    on a deterministic absolute grid (month starts for *months*, or every
    *days* calendar days from 1970-01-01 for *days*), so chunks have stable
    names regardless of the requested outer bounds. The first and last chunk
    honour the requested outer bounds exactly, so no extra data is requested
    and no data is skipped.

    Day-grained chunks (``--chunk-days``) are more robust against Dukascopy's
    HTTP 429 request throttling: smaller requests are far more likely to be
    accepted. They produce identical canonical output (results are concatenated
    before normalization), so reproducibility is preserved.

    Returns:
        List of ``[from_str, to_str]`` date strings, each chunk covering
        ``[from, to)``.
    """
    start = date.fromisoformat(date_from)
    end = date.fromisoformat(date_to)
    if end <= start:
        raise ValueError(
            f"date_to ({date_to}) must be after date_from ({date_from})"
        )
    if months is not None and days is not None:
        raise ValueError("only one of months= or days= may be provided")
    if months is None and days is None:
        months = CHUNK_MONTHS

    if months is not None:
        if months < 1:
            raise ValueError(f"chunk months must be >= 1, got {months}")
        boundaries = [start]
        k = 1
        while True:
            total = k * months  # 0-based month index since year 1
            year = total // 12 + 1
            month = total % 12 + 1
            boundary = date(year, month, 1)
            if boundary >= end:
                break
            if boundary > start:
                boundaries.append(boundary)
            k += 1
        boundaries.append(end)
    else:
        if days < 1:
            raise ValueError(f"chunk days must be >= 1, got {days}")
        boundaries = [start]
        k = 1
        epoch = date(1970, 1, 1)
        while True:
            boundary = epoch + timedelta(days=k * days)
            if boundary >= end:
                break
            if boundary > start:
                boundaries.append(boundary)
            k += 1
        boundaries.append(end)

    return [
        [boundaries[i].isoformat(), boundaries[i + 1].isoformat()]
        for i in range(len(boundaries) - 1)
    ]


def _chunk_csv_name(
    instrument: str, date_from: str, date_to: str, price_type: str
) -> str:
    """Name dukascopy-node writes for a given chunk request."""
    return f"{instrument}-m5-{price_type}-{date_from}-{date_to}.csv"


def _last_bar_utc(path: Path) -> pd.Timestamp | None:
    """Return the last bar's naive-UTC timestamp in the raw CSV, or None."""
    df = pd.read_csv(path)
    if df.empty:
        return None
    return pd.to_datetime(
        df["timestamp"].iloc[-1], unit="ms", utc=True
    ).tz_localize(None)


def _chunk_data_complete(path: Path, date_to: str) -> bool:
    """Whether the raw chunk CSV at *path* covers through (near) *date_to*.

    A chunk that died part-way through the download leaves a truncated file
    whose last bar is many days before the chunk end.
    """
    last = _last_bar_utc(path)
    if last is None:
        return False
    end_ts = pd.Timestamp(date_to)
    return (end_ts - last) <= pd.Timedelta(days=COMPLETENESS_TOLERANCE_DAYS)


def _run_dukascopy_cli(
    instrument: str,
    date_from: str,
    date_to: str,
    price_type: str,
    out_dir: Path,
) -> Path:
    """Run dukascopy-node CLI and return the path to the downloaded CSV.

    Low-level call: one range, one price type. Raises :class:`RuntimeError`
    with the actual exit code and captured stdout/stderr (dukascopy-node prints
    its errors to *stdout* via ``console.log``, so stderr is not sufficient).
    """
    cmd = [
        "powershell", "-ExecutionPolicy", "Bypass", "-Command",
        (
            f"npx dukascopy-node -i {instrument} "
            f"-from {date_from} -to {date_to} "
            f"-t m5 -p {price_type} -f csv -v -vu units "
            f"-r {DUKAS_CLI_RETRIES} -rp {DUKAS_CLI_RETRY_PAUSE_MS} "
            f"-dir '{out_dir}'"
        ),
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=CALL_TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"dukascopy-node timed out after {CALL_TIMEOUT_SECONDS}s for "
            f"{instrument} {price_type} {date_from}..{date_to}"
        )

    expected = out_dir / _chunk_csv_name(instrument, date_from, date_to, price_type)

    if result.returncode != 0:
        raise RuntimeError(
            f"dukascopy-node failed for {instrument} {price_type} "
            f"{date_from}..{date_to}: exit={result.returncode}; "
            f"stderr={_tail(result.stderr)}; stdout={_tail(result.stdout)}"
        )
    if not expected.exists() or expected.stat().st_size == 0:
        raise RuntimeError(
            f"dukascopy-node produced no/empty output for {instrument} "
            f"{price_type} {date_from}..{date_to}: exit={result.returncode}; "
            f"stderr={_tail(result.stderr)}; stdout={_tail(result.stdout)}"
        )
    return expected


def _sleep_before_retry(attempt: int, error_text: str) -> float:
    """Exponential backoff before retrying attempt *attempt*+1.

    HTTP 429 (rate limit) gets a longer initial sleep because Dukascopy's
    throttle window typically outlasts the regular backoff.
    """
    text = (error_text or "").lower()
    base = CALL_RETRY_SLEEP_SECONDS
    if "429" in text or "too many requests" in text:
        base = max(base, 30)
    sleep = min(base * (2 ** (attempt - 1)), CALL_RETRY_MAX_SLEEP_SECONDS)
    time.sleep(sleep)
    return sleep


def _download_chunk(
    instrument: str,
    date_from: str,
    date_to: str,
    price_type: str,
    out_dir: Path,
) -> Path:
    """Download one chunk with retries; idempotent on complete artifacts.

    If a complete raw chunk CSV already exists it is reused (resume). Completed
    chunks are never re-downloaded. Partial/empty artifacts are deleted and the
    chunk re-downloaded, up to :data:`CALL_ATTEMPTS` times with exponential
    backoff (longer for HTTP 429 rate limits).
    """
    expected = out_dir / _chunk_csv_name(instrument, date_from, date_to, price_type)

    if expected.exists() and expected.stat().st_size > 0:
        if _chunk_data_complete(expected, date_to):
            return expected
        print(
            f"    [chunk {date_from}..{date_to} {price_type}] partial file "
            f"found ({expected.stat().st_size} bytes) — will re-download",
            file=sys.stderr,
        )

    last_error: Exception | None = None
    for attempt in range(1, CALL_ATTEMPTS + 1):
        if expected.exists():
            try:
                expected.unlink()
            except OSError:
                pass
        try:
            path = _run_dukascopy_cli(instrument, date_from, date_to, price_type, out_dir)
            if _chunk_data_complete(path, date_to):
                return path
            last_error = RuntimeError(
                f"incomplete chunk data for {instrument} {price_type} "
                f"{date_from}..{date_to}: last bar too far before {date_to}"
            )
        except Exception as exc:  # noqa: BLE001 - surface the raw CLI failure
            last_error = exc
        if attempt < CALL_ATTEMPTS:
            slept = _sleep_before_retry(attempt, str(last_error))
            print(
                f"    [chunk {date_from}..{date_to} {price_type}] attempt "
                f"{attempt}/{CALL_ATTEMPTS} failed ({last_error}); retrying in "
                f"{slept:.0f}s",
                file=sys.stderr,
            )

    if "429" in (exc_text := str(last_error)) or "too many requests" in exc_text.lower():
        last_error = RuntimeError(
            f"{exc_text} — Dukascopy rate-limited the request (HTTP 429 Too Many "
            f"Requests). Waiting longer between attempts and/or using smaller chunks "
            f"(--chunk-days 7) makes this far less likely; the run can simply be "
            f"repeated later because completed chunks are reused."
        )
    raise RuntimeError(
        f"chunk {instrument} {price_type} {date_from}..{date_to} failed after "
        f"{CALL_ATTEMPTS} attempts: {last_error}"
    )


def read_dukascopy_csv(path: Path) -> pd.DataFrame:
    """Parse a raw dukascopy-node CSV into a DataFrame with canonical names.

    Maps the raw ``volume`` column to ``tick_volume`` and converts the raw
    millisecond ``timestamp`` into a naive-UTC ``time`` column.  No other
    transformation is applied here; OHLC prices are preserved verbatim.
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"Dukascopy raw file not found: {path}")

    df = pd.read_csv(path)

    missing = [c for c in DUKAS_RAW_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Dukascopy CSV {path} is missing expected columns: {missing}; "
            f"got {list(df.columns)}"
        )

    df = df.rename(columns={"volume": "tick_volume"})
    df["time"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_localize(None)

    return df[["time", "open", "high", "low", "close", "tick_volume"]].copy()


def dukascopy_to_canonical(
    bid_df: pd.DataFrame,
    ask_df: pd.DataFrame,
    symbol: str,
) -> pd.DataFrame:
    """Normalize parsed bid/ask Dukascopy frames into the canonical schema.

    Alignment is on the ``time`` index (common timestamps only).  OHLC values
    are taken from the **bid** side (the backtester treats prices as bid).
    ``tick_volume`` is preserved from Dukascopy's ``volume`` column.  ``spread``
    is the observed difference ``(ask_close - bid_close) / point`` in points.
    ``real_volume`` is set to 0 because Dukascopy does not provide it; this is
    documented as unavailable, never fabricated.

    Args:
        bid_df: Parsed Dukascopy bid frame (see :func:`read_dukascopy_csv`).
        ask_df: Parsed Dukascopy ask frame.
        symbol: Project symbol (e.g. "EURUSD").

    Returns:
        Canonical DataFrame with columns ``CANONICAL_COLUMNS``.
    """
    symbol_upper = symbol.upper()
    inst = get_instrument(symbol_upper)

    bid = bid_df.set_index("time").sort_index()
    ask = ask_df.set_index("time").sort_index()

    if bid.empty or ask.empty:
        raise ValueError(
            f"Empty Dukascopy data for {symbol_upper}: bid={len(bid)} ask={len(ask)} bars"
        )

    common_idx = bid.index.intersection(ask.index)
    if len(common_idx) == 0:
        raise ValueError(
            f"No overlapping bid/ask timestamps for {symbol_upper} "
            f"(bid {len(bid)} bars, ask {len(ask)} bars)"
        )

    bid = bid.loc[common_idx]
    ask = ask.loc[common_idx]
    bid = bid[~bid.index.duplicated(keep="first")]
    ask = ask[~ask.index.duplicated(keep="first")]

    spread_raw = ask["close"].values - bid["close"].values
    spread_points = (spread_raw / inst.point).round(0).astype(int)

    canonical = pd.DataFrame({
        "time": bid.index,
        "open": bid["open"].to_numpy(dtype=float),
        "high": bid["high"].to_numpy(dtype=float),
        "low": bid["low"].to_numpy(dtype=float),
        "close": bid["close"].to_numpy(dtype=float),
        "tick_volume": bid["tick_volume"].to_numpy(dtype=int),
        "spread": spread_points,
        "real_volume": 0,
    })

    return (
        canonical.reset_index(drop=True)[CANONICAL_COLUMNS]
        .sort_values("time")
        .reset_index(drop=True)
    )


def download_m5(
    symbol: str,
    date_from: str,
    date_to: str,
    out_dir: Path | None = None,
    chunk_months: int = CHUNK_MONTHS,
    chunk_days: int | None = None,
) -> pd.DataFrame:
    """Download M5 bid+ask data from Dukascopy and return canonical DataFrame.

    The requested ``[date_from, date_to)`` range is split into chunks (monthly
    by default, or ``chunk_days``-day steps), each downloaded independently (see
    module docstring for the resumable design), then concatenated and
    normalized. Day-grained chunks are more tolerant of Dukascopy's HTTP 429
    request throttling and produce identical canonical output.

    Args:
        symbol: Trading symbol (e.g. "EURUSD").
        date_from: Start date "YYYY-MM-DD".
        date_to: End date "YYYY-MM-DD" (exclusive).
        out_dir: Directory for temporary CLI downloads. Uses a system temp dir
            if None.
        chunk_months: Number of months per download chunk (used when
            *chunk_days* is None).
        chunk_days: If given, number of calendar days per download chunk
            instead of months.

    Returns:
        Canonical DataFrame with columns ``CANONICAL_COLUMNS``.
    """
    dukas_sym = DUKAS_SYMBOLS.get(symbol.upper())
    if dukas_sym is None:
        raise ValueError(f"Unknown symbol: {symbol}. Supported: {ALL_SYMBOLS}")

    tmp_dir = Path(tempfile.mkdtemp(prefix="dukascopy_")) if out_dir is None else out_dir
    tmp_dir.mkdir(parents=True, exist_ok=True)

    if chunk_days is not None and chunk_days >= 1:
        chunks = _chunk_ranges(date_from, date_to, months=None, days=chunk_days)
    else:
        chunks = _chunk_ranges(date_from, date_to, months=chunk_months, days=None)
    bid_frames: list[pd.DataFrame] = []
    ask_frames: list[pd.DataFrame] = []

    for chunk_idx, (chunk_from, chunk_to) in enumerate(chunks):
        bid_path = _download_chunk(dukas_sym, chunk_from, chunk_to, "bid", tmp_dir)
        ask_path = _download_chunk(dukas_sym, chunk_from, chunk_to, "ask", tmp_dir)
        bid_frames.append(read_dukascopy_csv(bid_path))
        ask_frames.append(read_dukascopy_csv(ask_path))
        print(f"    chunk {chunk_from}..{chunk_to}: bid+ask OK")
        if chunk_idx < len(chunks) - 1 and CHUNK_SLEEP_SECONDS:
            time.sleep(CHUNK_SLEEP_SECONDS)

    bid_df = pd.concat(bid_frames, ignore_index=True)
    ask_df = pd.concat(ask_frames, ignore_index=True)

    return dukascopy_to_canonical(bid_df, ask_df, symbol)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download M5 data from Dukascopy"
    )
    parser.add_argument(
        "--symbol", type=str, default=None,
        help="Single symbol (e.g. EURUSD)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Download all supported symbols",
    )
    parser.add_argument("--from", dest="date_from", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--to", dest="date_to", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--out-dir", type=Path, default=Path("data"), help="Output directory")
    parser.add_argument(
        "--chunk-months", type=int, default=CHUNK_MONTHS,
        help="Months per download chunk (default 1)",
    )
    parser.add_argument(
        "--chunk-days", type=int, default=None,
        help="Days per download chunk instead of months (e.g. 7). Smaller "
             "chunks are far more robust against Dukascopy HTTP 429 "
             "rate-limiting and remain fully resumable.",
    )
    args = parser.parse_args(argv)

    raw_argv = argv if argv is not None else sys.argv[1:]
    if args.chunk_days is not None and "--chunk-months" in raw_argv:
        parser.error("--chunk-months and --chunk-days are mutually exclusive")

    if args.all:
        symbols = ALL_SYMBOLS
    elif args.symbol:
        symbols = [args.symbol.upper()]
    else:
        parser.error("either --symbol or --all is required")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    failed = []
    for sym in symbols:
        print(f"Downloading {sym} from Dukascopy ({args.date_from} to {args.date_to})...")
        try:
            df = download_m5(
                sym, args.date_from, args.date_to,
                out_dir=args.out_dir, chunk_months=args.chunk_months,
                chunk_days=args.chunk_days,
            )
            out_path = args.out_dir / f"{sym.lower()}_m5.csv"
            df.to_csv(out_path, index=False)
            print(f"  Saved {len(df)} bars to {out_path}")
            print(f"  Range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
            print(f"  Columns: {list(df.columns)}")
        except Exception as e:  # noqa: BLE001 - per-symbol failure reporting
            print(f"  FAILED: {e}", file=sys.stderr)
            failed.append(sym)

    if failed:
        print(f"\nFAILED symbols: {failed}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())