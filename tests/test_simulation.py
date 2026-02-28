"""
tests/test_simulation.py
------------------------
Unit tests for the simulation orchestration layer.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import pytest
from src.simulation import (
    sample_design_space,
    run_simulation,
    compute_sweet_score,
    top_designs,
    DESIGN_BOUNDS,
)


# ---------------------------------------------------------------------------
# sample_design_space
# ---------------------------------------------------------------------------

def test_sample_returns_correct_shape():
    df = sample_design_space(n=500, seed=0)
    assert df.shape == (500, 4)
    assert set(df.columns) == {"m_racket", "k_string", "damping", "x_norm"}


def test_sample_within_bounds():
    df = sample_design_space(n=1000, seed=1)
    for var, (lo, hi) in DESIGN_BOUNDS.items():
        assert df[var].min() >= lo - 1e-9, f"{var} below lower bound"
        assert df[var].max() <= hi + 1e-9, f"{var} above upper bound"


def test_sample_reproducible():
    df1 = sample_design_space(n=200, seed=42)
    df2 = sample_design_space(n=200, seed=42)
    pd.testing.assert_frame_equal(df1, df2)


# ---------------------------------------------------------------------------
# run_simulation
# ---------------------------------------------------------------------------

def test_run_simulation_columns():
    designs = sample_design_space(n=100, seed=5)
    results = run_simulation(designs)
    expected = {"m_racket", "k_string", "damping", "x_norm", "e", "m_eff", "v_exit", "vib_score", "shock_proxy"}
    assert expected.issubset(set(results.columns))


def test_run_simulation_no_nans():
    designs = sample_design_space(n=200, seed=6)
    results = run_simulation(designs)
    assert not results[["v_exit", "shock_proxy"]].isna().any().any()


def test_run_simulation_exit_speed_reasonable():
    """Exit speeds should be in the range ~15–35 m/s for a 30 m/s incoming ball."""
    designs = sample_design_space(n=500, seed=7)
    results = run_simulation(designs)
    assert results["v_exit"].between(10.0, 40.0).all()


# ---------------------------------------------------------------------------
# compute_sweet_score
# ---------------------------------------------------------------------------

def test_sweet_score_column_added():
    designs = sample_design_space(n=200, seed=8)
    results = run_simulation(designs)
    results = compute_sweet_score(results)
    assert "sweet_score" in results.columns


def test_sweet_score_finite():
    designs = sample_design_space(n=200, seed=9)
    results = run_simulation(designs)
    results = compute_sweet_score(results)
    assert np.isfinite(results["sweet_score"]).all()


def test_sweet_score_weight_effect():
    """Higher speed weight should push best designs toward high exit speed."""
    designs = sample_design_space(n=500, seed=10)
    results = run_simulation(designs)

    df_speed = compute_sweet_score(results.copy(), w_speed=0.90, w_shock=0.10)
    df_shock = compute_sweet_score(results.copy(), w_speed=0.10, w_shock=0.90)

    best_speed = df_speed.sort_values("sweet_score", ascending=False).head(10)["v_exit"].mean()
    best_shock = df_shock.sort_values("sweet_score", ascending=False).head(10)["v_exit"].mean()

    assert best_speed >= best_shock


# ---------------------------------------------------------------------------
# top_designs
# ---------------------------------------------------------------------------

def test_top_designs_length():
    designs = sample_design_space(n=300, seed=11)
    results = run_simulation(designs)
    results = compute_sweet_score(results)
    best = top_designs(results, n=20)
    assert len(best) == 20


def test_top_designs_sorted():
    designs = sample_design_space(n=300, seed=12)
    results = run_simulation(designs)
    results = compute_sweet_score(results)
    best = top_designs(results, n=15)
    assert (best["sweet_score"].diff().dropna() <= 0).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
