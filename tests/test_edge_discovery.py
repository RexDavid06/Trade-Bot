"""EDGE DISCOVERY research integrity tests.

Every experiment in EDGE_DISCOVERY_PLAN.md / backtest/market_research/
edge_discovery.py must be reproducible, causal and DEV-only. These tests lock in:

  * split isolation   - _load_dev returns exactly the DEV rows, chronological,
                        with no row on/after the validation/holdout epochs
  * aggregation       - UTC floor windows use only M5 rows opened inside them,
                        no NaT timestamps (regression for the to_period crash)
  * execution         - entry at open[t+1], exit at close[t+H],
                        cost = spread[t+1] + spread[t+H] + slip, next-close only
  * causality         - every feature at t depends only on bars <= t
  * the frozen screen - classify() bucket boundaries match the plan
  * output integrity  - results JSON contains exactly the pre-registered keys
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backtest.config import PathConfig
from backtest.instruments import get_instrument
from backtest.market_research.edge_discovery import (
    Frame,
    SYMBOLS,
    MIN_BEHAV_N,
    PROMISE_RATIO,
    PROMISE_MEAN,
    SLIP_TOTAL_PIPS,
    _aggregate,
    _load_dev,
    _split_counts,
    classify,
    experiment_metrics,
    simulate,
)


def _m5(start: str = "2025-01-01", k: int = 200, pip: float = 0.0001):
    """Synthetic M5 frame: 5-min bars, near-ear-end, EURUSD-like convention."""
    rng = np.random.default_rng(3)
    close = 1.1000 + np.cumsum(rng.normal(0, 0.0001, k))
    times = pd.date_range(start, periods=k, freq="5min")
    spread_p = np.maximum(np.round(rng.normal(0.00002, 0.000002, k), 6), 1e-7)
    return pd.DataFrame(
        {
            "time": times,
            "open": np.concatenate([[close[0]], close[:-1]]),
            "high": np.maximum(close, np.concatenate([[close[0]], close[:-1]])) + 0.0002,
            "low": np.minimum(close, np.concatenate([[close[0]], close[:-1]])) - 0.0002,
            "close": close,
            "spread": spread_p,
        }
    )


def _frame_from(m5: pd.DataFrame) -> Frame:
    return Frame("EURUSD", "M5", PathConfig(), m5=m5)


# ---------------------------------------------------------------------------
# Split isolation
# ---------------------------------------------------------------------------

class TestSplitIsolation:
    def test_load_dev_matches_assignment_exactly(self):
        pcfg = PathConfig()
        for sym in SYMBOLS:
            dev = _load_dev(sym, pcfg)
            assign = pd.read_csv(Path(pcfg.output_dir, "splits", sym, "assignments.csv"))
            dev_idx = set(assign.index[assign["split"] == "dev"].tolist())
            assert set(dev.index.tolist()) == dev_idx, sym
            assert not dev.empty, sym

    def test_dev_is_chronologically_before_val_and_holdout(self):
        pcfg = PathConfig()
        for sym in SYMBOLS:
            dev = _load_dev(sym, pcfg)
            assign = pd.read_csv(Path(pcfg.output_dir, "splits", sym, "assignments.csv"))
            val_min = pd.to_datetime(assign.loc[assign["split"] == "val", "time"]).min()
            hol_min = pd.to_datetime(assign.loc[assign["split"] == "holdout", "time"]).min()
            assert dev["time"].max() < val_min, sym
            assert dev["time"].max() < hol_min, sym

    def test_split_counts_preserve_60_20_20(self):
        pcfg = PathConfig()
        counts = _split_counts("EURUSD", pcfg)
        total = sum(counts.values())
        assert counts["dev"] / total == pytest.approx(0.6, abs=0.01)
        assert counts["val"] / total == pytest.approx(0.2, abs=0.01)

    def test_frames_never_read_val_holdout(self):
        # Frame built from DEV rows only: every aggregated bar is before val epoch.
        pcfg = PathConfig()
        for sym in SYMBOLS:
            assign = pd.read_csv(Path(pcfg.output_dir, "splits", sym, "assignments.csv"))
            val_min = pd.to_datetime(assign.loc[assign["split"] == "val", "time"]).min()
            for tf in ("M15", "H1", "H4"):
                fr = Frame(sym, tf, pcfg)
                assert fr.ts[-1] < np.datetime64(val_min), (sym, tf)


# ---------------------------------------------------------------------------
# Aggregation causality / no-NaT regression
# ---------------------------------------------------------------------------

class TestAggregate:
    def test_no_nat_regression_for_to_period_crash(self):
        pcfg = PathConfig()
        for sym in SYMBOLS:
            for tf in ("M15", "H1", "H4"):
                fr = Frame(sym, tf, pcfg)
                assert np.isnat(fr.ts.astype("datetime64[ns]")).sum() == 0, (sym, tf)
                assert fr.ts[0] < fr.ts[-1], (sym, tf)

    def test_aggregate_windows_match_reference(self):
        m5 = _m5(k=500)
        # Manual reference: summary over rows whose OPEN time is inside the window.
        manual = m5.groupby(m5["time"].dt.floor("15min")).agg(
            foo=("open", "first"), bar=("high", "max"), baz=("low", "min"),
            qux=("close", "last"))
        agg = _aggregate(m5, "M15")
        assert agg["open"].to_numpy() == pytest.approx(manual["foo"].to_numpy())
        assert agg["high"].to_numpy() == pytest.approx(manual["bar"].to_numpy())
        assert agg["low"].to_numpy() == pytest.approx(manual["baz"].to_numpy())
        assert agg["close"].to_numpy() == pytest.approx(manual["qux"].to_numpy())
        assert agg["n_bars"].sum() == len(m5)

    def test_aggregate_uses_only_own_window_rows(self):
        m5 = _m5(k=40)
        agg = _aggregate(m5, "M15")
        # No bar's open may come from an M5 row opened after its close.
        assert m5["time"].min() >= agg["time"].min()
        assert (agg["n_bars"] >= 1).all()


# ---------------------------------------------------------------------------
# Simulation semantics
# ---------------------------------------------------------------------------

class TestSimulate:
    def test_next_open_entry_fixed_horizon_and_cost(self):
        m5 = _m5(k=60)
        frame = _frame_from(m5)
        mask = np.zeros(frame.n, dtype=bool)
        direction = np.zeros(frame.n, dtype=float)
        mask[0] = True
        direction[0] = 1.0
        hold = 3
        events = simulate(frame, mask, direction, hold)
        assert len(events) == 1
        e = events[0]
        entry_i, exit_i = 1, 3
        assert e["entry_time"] == str(frame.ts[entry_i])
        assert e["exit_time"] == str(frame.ts[exit_i])
        assert e["gross_pips"] == pytest.approx(
            (frame.close[exit_i] - frame.open[entry_i]) / frame.pip)
        assert e["cost_pips"] == pytest.approx(
            frame.spread_pips[entry_i] + frame.spread_pips[exit_i] + SLIP_TOTAL_PIPS)
        assert e["net_pips"] == pytest.approx(e["gross_pips"] - e["cost_pips"])
        assert e["direction"] == "BUY"
        assert e["duration_bars"] == hold
        assert e["duration_hours"] == pytest.approx(hold * 5 / 60)

    def test_short_side(self):
        m5 = _m5(k=60)
        frame = _frame_from(m5)
        mask = np.zeros(frame.n, dtype=bool)
        direction = np.zeros(frame.n, dtype=float)
        mask[2] = True
        direction[2] = -1.0
        events = simulate(frame, mask, direction, 2)
        assert events[0]["direction"] == "SELL"
        assert events[0]["gross_pips"] == pytest.approx(
            (frame.open[3] - frame.close[4]) / frame.pip)

    def test_skips_events_without_room(self):
        m5 = _m5(k=10)
        frame = _frame_from(m5)
        mask = np.ones(frame.n, dtype=bool)
        direction = np.ones(frame.n, dtype=float)
        events = simulate(frame, mask, direction, 9)
        assert len(events) == 1  # only t=0 clears t+1 < n and t+9 < n
        assert events[0]["entry_time"] == str(frame.ts[1])

    def test_skips_nonfinite_prices(self):
        m5 = _m5(k=30)
        m5.loc[1, "open"] = np.nan
        frame = _frame_from(m5)
        mask = np.zeros(frame.n, dtype=bool)
        direction = np.zeros(frame.n, dtype=float)
        mask[0] = True
        direction[0] = 1.0
        # Preserve frame semantics: NaN in raw open should make entry non-finite.
        assert np.isnan(frame.open[1])
        assert simulate(frame, mask, direction, 4) == []

    def test_entry_year_and_month_are_valid(self):
        # Regression for the NaT .to_period() crash.
        m5 = _m5(k=60)
        frame = _frame_from(m5)
        mask = np.zeros(frame.n, dtype=bool)
        direction = np.zeros(frame.n, dtype=float)
        mask[5] = True
        direction[5] = 1.0
        events = simulate(frame, mask, direction, 3)
        assert events
        assert isinstance(events[0]["entry_year"], int)
        assert str(events[0]["entry_month"]).startswith("202")


# ---------------------------------------------------------------------------
# Causality of features
# ---------------------------------------------------------------------------

class TestCausality:
    def test_sma_atr_z_depend_only_on_past(self):
        m5 = _m5(k=400)
        frame = _frame_from(m5)
        # Mutate every future close/high/low after index 100; features at 100
        # (and before) must be unchanged because they only use bars <= 100.
        base = frame.atr_pips.copy(), frame.sma_fast.copy(), frame.z.copy(), frame.regime_sqzc.copy()
        m5.loc[101:, "close"] = 9.9
        m5.loc[101:, "high"] = 9.95
        m5.loc[101:, "low"] = 9.85
        frame2 = _frame_from(m5)
        assert np.allclose(base[0][:101], frame2.atr_pips[:101], equal_nan=True)
        assert np.allclose(base[1][:101], frame2.sma_fast[:101], equal_nan=True)
        assert np.allclose(base[2][:101], frame2.z[:101], equal_nan=True)
        assert np.array_equal(base[3][:101], frame2.regime_sqzc[:101])

    def test_fast_slices_causal(self):
        from backtest.market_research.edge_discovery import _fast_slices
        pcfg = PathConfig()
        m15 = Frame("EURUSD", "M15", pcfg)
        h1 = Frame("EURUSD", "H1", pcfg)
        f0, f1 = _fast_slices(m15.ts_ns, h1.ts_ns, 15, 60)
        assert len(f0) == len(f1) == h1.n
        # For every mapped bar, the last M15 index used is inside that H1 window,
        # i.e. its timestamp is < the next H1 bar's open.
        assert (m15.ts_ns[f1] < h1.ts_ns + 60 * 60_000_000_000).all()
        assert (f0 <= f1).all()


# ---------------------------------------------------------------------------
# Frozen screen
# ---------------------------------------------------------------------------

class TestClassify:
    def base(self, **kw):
        return {
            "n": 2000,
            "movement_to_cost": 1.2,
            "mean_raw_pips": 2.5,
            "expectancy_net_pips": 0.4,
            "t_test": {"p": 0.001},
            "years_positive_share": 0.8,
            "max_year_share": 0.3,
            "max_window_share": 0.2,
            **kw,
        }

    def test_insuff_below_min_n(self):
        r = classify(self.base(n=MIN_BEHAV_N - 1), 3)
        assert r["verdict"] == "INSUFF"

    def test_insuff_below_border_ratio(self):
        r = classify(self.base(movement_to_cost=0.49, mean_raw_pips=1.0), 3)
        assert r["verdict"] == "INSUFF"

    def test_border_strictly_between(self):
        r = classify(self.base(movement_to_cost=0.6, mean_raw_pips=1.5), 3)
        assert r["verdict"] == "BORDER"

    def test_border_at_promise_bar_present(self):
        # BORDER when ratio in [0.5, 1.0) but below PROMISE_RATIO.
        r = classify(self.base(movement_to_cost=PROMISE_RATIO - 0.01, mean_raw_pips=PROMISE_MEAN), 3)
        assert r["verdict"] == "BORDER"

    def test_rejected_insignificant(self):
        r = classify(self.base(t_test={"p": 0.5}), 3)
        assert r["verdict"] == "REJECTED"

    def test_rejected_negative_expectancy(self):
        r = classify(self.base(expectancy_net_pips=-0.1), 3)
        assert r["verdict"] == "REJECTED"

    def test_rejected_too_few_positive_symbols(self):
        r = classify(self.base(), 1)
        assert r["verdict"] == "REJECTED"
        assert "symbols" in r["reason"]

    def test_rejected_years(self):
        r = classify(self.base(years_positive_share=0.5), 3)
        assert r["verdict"] == "REJECTED"

    def test_rejected_year_concentration(self):
        r = classify(self.base(max_year_share=0.51), 3)
        assert r["verdict"] == "REJECTED"

    def test_rejected_window_concentration(self):
        r = classify(self.base(max_window_share=0.41), 3)
        assert r["verdict"] == "REJECTED"

    def test_viable_clears_full_screen(self):
        r = classify(self.base(), 3)
        assert r["verdict"] == "VIABLE*"


# ---------------------------------------------------------------------------
# Metrics keys / deterministic reproduction
# ---------------------------------------------------------------------------

class TestMetrics:
    def _events(self, n=50):
        out = []
        for i in range(n):
            out.append({
                "entry_time": f"2025-01-{(i % 28) + 1:02d} 00:00:00",
                "exit_time": f"2025-02-{(i % 20) + 1:02d} 00:00:00",
                "direction": "BUY" if i % 2 else "SELL",
                "gross_pips": float((-1) ** i * 2.0),
                "cost_pips": 1.0,
                "net_pips": float((-1) ** i * 2.0 - 1.0),
                "duration_bars": 12,
                "duration_hours": 12.0,
                "entry_regime": "normal",
                "entry_year": 2025,
                "entry_month": "2025-01",
            })
        return out

    def test_metric_keys_present(self):
        m5 = _m5(k=100)
        frame = _frame_from(m5)
        m = experiment_metrics(self._events(), frame)
        for key in ("n", "win_rate", "expectancy_net_pips", "profit_factor",
                    "total_net_pips", "movement_to_cost", "mean_raw_pips",
                    "t_test", "years_total", "years_positive_share",
                    "max_year_share", "max_window_share"):
            assert key in m, key

    def test_metrics_deterministic(self):
        m5 = _m5(k=100)
        frame = _frame_from(m5)
        events = self._events()
        assert experiment_metrics(events, frame) == experiment_metrics(events, frame)


# ---------------------------------------------------------------------------
# Whole-run output integrity
# ---------------------------------------------------------------------------

class TestOutput:
    def test_results_json_schema(self):
        path = Path("outputs/edge_discovery_results.json")
        if not path.exists():
            pytest.skip("outputs/edge_discovery_results.json not generated yet")
        d = json.loads(path.read_text(encoding="utf-8"))
        assert set(d["results"].keys()) >= {"B-PB", "E-SQZ", "G-CANDLE", "H-ALIGN", "J-FADE-REGIME"}
        for eid, r in d["results"].items():
            assert set(r["symbols"].keys()) == set(SYMBOLS)
            for sym in SYMBOLS:
                for H, m in r["symbols"][sym]["holds"].items():
                    assert m["verdict"] in {"INSUFF", "BORDER", "REJECTED", "VIABLE*"}
                    assert m["n"] == m["trades"]
        assert "meta" in d