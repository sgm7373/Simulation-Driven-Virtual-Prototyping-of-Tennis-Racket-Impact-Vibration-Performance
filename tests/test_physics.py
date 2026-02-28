"""
tests/test_physics.py
---------------------
Unit tests for the physics proxy models.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest
from src.physics import (
    clamp,
    effective_mass_at_impact,
    exit_speed,
    cor_from_string_stiffness,
    mode_shape_1,
    mode_shape_2,
    vibration_score,
    shock_proxy,
)


# ---------------------------------------------------------------------------
# clamp
# ---------------------------------------------------------------------------

def test_clamp_scalar():
    assert clamp(5.0, 0.0, 3.0) == 3.0
    assert clamp(-1.0, 0.0, 3.0) == 0.0
    assert clamp(2.0, 0.0, 3.0) == 2.0


def test_clamp_array():
    arr = np.array([-1.0, 0.5, 2.0])
    result = clamp(arr, 0.0, 1.0)
    np.testing.assert_array_equal(result, [0.0, 0.5, 1.0])


# ---------------------------------------------------------------------------
# effective_mass_at_impact
# ---------------------------------------------------------------------------

def test_effective_mass_handle():
    """Effective mass at handle (x_norm=0) should be r_min fraction of total."""
    m = effective_mass_at_impact(0.300, 0.0)
    assert abs(m - 0.12 * 0.300) < 1e-9


def test_effective_mass_tip():
    """Effective mass at tip (x_norm=1) should be r_max fraction of total."""
    m = effective_mass_at_impact(0.300, 1.0)
    assert abs(m - 0.35 * 0.300) < 1e-9


def test_effective_mass_monotone():
    """Effective mass should increase monotonically from handle to tip."""
    x = np.linspace(0, 1, 50)
    m = effective_mass_at_impact(0.310, x)
    assert np.all(np.diff(m) >= 0)


# ---------------------------------------------------------------------------
# exit_speed
# ---------------------------------------------------------------------------

def test_exit_speed_positive():
    """Ball must always leave the racket faster than zero."""
    m_eff = np.array([0.040, 0.070, 0.100])
    e = np.array([0.40, 0.45, 0.50])
    v = exit_speed(30.0, m_eff, 0.058, e)
    assert np.all(v > 0)


def test_exit_speed_increases_with_mass():
    """Higher effective mass → faster exit speed (more racket dominance)."""
    v_low  = exit_speed(30.0, 0.030, 0.058, 0.45)
    v_high = exit_speed(30.0, 0.100, 0.058, 0.45)
    assert v_high > v_low


def test_exit_speed_increases_with_cor():
    """Higher COR → faster exit speed."""
    v_low  = exit_speed(30.0, 0.060, 0.058, 0.35)
    v_high = exit_speed(30.0, 0.060, 0.058, 0.55)
    assert v_high > v_low


# ---------------------------------------------------------------------------
# cor_from_string_stiffness
# ---------------------------------------------------------------------------

def test_cor_clamped():
    """COR must stay within [0.35, 0.55] regardless of extreme stiffness values."""
    e_low  = cor_from_string_stiffness(np.array([100.0]))
    e_high = cor_from_string_stiffness(np.array([10000.0]))
    assert e_low  >= 0.35
    assert e_high <= 0.55


def test_cor_increases_with_stiffness():
    """Stiffer strings → higher COR (within design range)."""
    e_soft = cor_from_string_stiffness(np.array([2200.0]))
    e_stiff = cor_from_string_stiffness(np.array([4200.0]))
    assert e_stiff > e_soft


# ---------------------------------------------------------------------------
# mode shapes
# ---------------------------------------------------------------------------

def test_mode_shape_1_range():
    """1st mode shape values must be in [-1, 1]."""
    x = np.linspace(0, 1, 100)
    phi = mode_shape_1(x)
    assert np.all(phi >= -1.0) and np.all(phi <= 1.0)


def test_mode_shape_2_range():
    x = np.linspace(0, 1, 100)
    phi = mode_shape_2(x)
    assert np.all(phi >= -1.0) and np.all(phi <= 1.0)


# ---------------------------------------------------------------------------
# vibration_score
# ---------------------------------------------------------------------------

def test_vibration_score_positive():
    """Vibration score must be non-negative."""
    x = np.linspace(0.1, 0.9, 20)
    v = vibration_score(x, 3000.0, 0.04, 0.310)
    assert np.all(v >= 0)


def test_vibration_decreases_with_damping():
    """Higher damping → lower vibration score."""
    x = np.array([0.5])
    v_low  = vibration_score(x, 3000.0, 0.01, 0.310)
    v_high = vibration_score(x, 3000.0, 0.08, 0.310)
    assert v_high < v_low


def test_vibration_increases_with_stiffness():
    """Stiffer strings → higher vibration (impulse-like transfer)."""
    x = np.array([0.5])
    v_soft  = vibration_score(x, 2200.0, 0.04, 0.310)
    v_stiff = vibration_score(x, 4200.0, 0.04, 0.310)
    assert v_stiff > v_soft


# ---------------------------------------------------------------------------
# shock_proxy
# ---------------------------------------------------------------------------

def test_shock_proxy_shape():
    """Output shape should match input shape."""
    n = 100
    x = np.random.uniform(0.15, 0.95, n)
    k = np.random.uniform(2200, 4200, n)
    d = np.random.uniform(0.01, 0.08, n)
    m = np.random.uniform(0.285, 0.340, n)
    vib = vibration_score(x, k, d, m)
    shock = shock_proxy(vib, x, k)
    assert shock.shape == (n,)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
