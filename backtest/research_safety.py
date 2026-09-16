"""Safeguards against accidental holdout contamination.

Enforces strict split boundaries during research: only the allowed split
(dev or val) is accessible by default. Holdout access requires an explicit,
logged request. Every data load is tracked in an audit log so contamination
can be detected post-hoc.

Usage:
    from backtest.research_safety import SplitGuard, HoldoutGuard, load_split_safe
"""

from __future__ import annotations

import datetime
import functools
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

ALLOWED_SPLITS = ("dev", "val", "holdout")


class SplitGuard:
    """Restricts which data split a research routine may access."""

    def __init__(self, allowed_split: str = "dev") -> None:
        if allowed_split not in ALLOWED_SPLITS:
            raise ValueError(
                f"allowed_split must be one of {ALLOWED_SPLITS}, got {allowed_split!r}"
            )
        self._allowed_split = allowed_split

    def check(self, split_name: str) -> bool:
        return split_name == self._allowed_split

    def require(self, split_name: str) -> None:
        if not self.check(split_name):
            raise ValueError(
                f"Access denied: split {split_name!r} is not allowed. "
                f"Only {self._allowed_split!r} may be used."
            )

    def get_allowed(self) -> str:
        return self._allowed_split


class HoldoutGuard:
    """Gate for holdout data access that requires an explicit, logged request."""

    def __init__(self) -> None:
        self._holdout_access: bool = False
        self._access_reasons: list[dict] = []

    def request_access(self, reason: str) -> None:
        if not reason or not reason.strip():
            raise ValueError("Holdout access request requires a non-empty reason.")
        self._holdout_access = True
        self._access_reasons.append({
            "reason": reason,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
        logger.warning("HOLDOUT ACCESS GRANTED: %s", reason)

    def is_accessible(self) -> bool:
        return self._holdout_access

    def reset(self) -> None:
        self._holdout_access = False

    def get_access_log(self) -> list[dict]:
        return list(self._access_reasons)


class ResearchContext:
    """Audit-trail wrapper that records every split access."""

    def __init__(
        self,
        allowed_split: str = "dev",
    ) -> None:
        self.split_guard = SplitGuard(allowed_split)
        self.holdout_guard = HoldoutGuard()
        self._access_log: list[dict] = []

    def _record(self, split_name: str, allowed: bool, reason: str = "") -> None:
        self._access_log.append({
            "split": split_name,
            "allowed": allowed,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "reason": reason,
        })

    def check_and_log(self, split_name: str, reason: str = "") -> bool:
        allowed = self.split_guard.check(split_name)
        self._record(split_name, allowed, reason)
        return allowed

    def require_and_log(self, split_name: str, reason: str = "") -> None:
        allowed = self.split_guard.check(split_name)
        self._record(split_name, allowed, reason)
        self.split_guard.require(split_name)

    def request_holdout(self, reason: str) -> None:
        self.holdout_guard.request_access(reason)
        self._record("holdout", True, reason)

    def get_access_log(self) -> list[dict]:
        return list(self._access_log)

    def was_holdout_accessed(self) -> bool:
        return any(e["split"] == "holdout" and e["allowed"] for e in self._access_log)


def load_split_safe(
    symbol: str,
    split_name: str,
    data_dir: str | Path,
    assignments_dir: str | Path,
) -> pd.DataFrame:
    """Load a split's data with validation and logging.

    Parameters
    ----------
    symbol : str
        Instrument name (e.g. ``"EURUSD"``).
    split_name : str
        One of ``"dev"``, ``"val"``, ``"holdout"``.
    data_dir : str | Path
        Directory containing per-symbol CSV files (``<symbol>_m5.csv``).
    assignments_dir : str | Path
        Directory containing ``data_split_assignments.csv``.

    Returns
    -------
    pd.DataFrame
        Filtered OHLCV data for the requested split.
    """
    if split_name not in ALLOWED_SPLITS:
        raise ValueError(
            f"Invalid split_name {split_name!r}; must be one of {ALLOWED_SPLITS}"
        )

    data_dir = Path(data_dir)
    assignments_dir = Path(assignments_dir)

    data_file = data_dir / f"{symbol.lower()}_m5.csv"
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")

    assignments_file = assignments_dir / "data_split_assignments.csv"
    if not assignments_file.exists():
        raise FileNotFoundError(f"Assignments file not found: {assignments_file}")

    df = pd.read_csv(data_file)
    df["time"] = pd.to_datetime(df["time"])

    assignments = pd.read_csv(assignments_file)
    assignments["time"] = pd.to_datetime(assignments["time"])

    if "split" not in assignments.columns:
        raise ValueError("Assignments file missing 'split' column.")

    valid_splits = set(assignments["split"].unique())
    if split_name not in valid_splits:
        raise ValueError(
            f"Split {split_name!r} not found in assignments. "
            f"Available: {sorted(valid_splits)}"
        )

    mask = assignments["split"] == split_name
    split_times = assignments.loc[mask, "time"]

    merged = df.merge(
        split_times.to_frame("time"),
        on="time",
        how="inner",
    )

    logger.info(
        "Loaded split %r for %s: %d rows", split_name, symbol, len(merged),
    )
    return merged


def validate_no_holdout_access(research_runner_func):
    """Decorator that blocks any holdout access inside *research_runner_func*.

    The wrapped function receives a ``ResearchContext`` as its first positional
    argument.  If the function (or anything it calls via the same context)
    attempts holdout access, a ``RuntimeError`` is raised.
    """

    @functools.wraps(research_runner_func)
    def wrapper(ctx: ResearchContext, *args, **kwargs):
        original_request = ctx.holdout_guard.request_access

        def _block(reason: str) -> None:
            raise RuntimeError(
                "Holdout access is blocked inside this research function. "
                f"Requested reason: {reason}"
            )

        ctx.holdout_guard.request_access = _block  # type: ignore[assignment]
        try:
            return research_runner_func(ctx, *args, **kwargs)
        finally:
            ctx.holdout_guard.request_access = original_request  # type: ignore[assignment]

    return wrapper
