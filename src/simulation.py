"""
simulation.py
-------------
Monte Carlo design-space sampling and output computation for the
tennis racket virtual prototyping framework.
"""

import numpy as np
import pandas as pd

from .physics import (
    clamp,
    effective_mass_at_impact,
    exit_speed,
    cor_from_string_stiffness,
    vibration_score,
    shock_proxy,
)


# ---------------------------------------------------------------------------
# Default physical constants
# ---------------------------------------------------------------------------

DEFAULTS = dict(
    m_ball=0.058,      # kg  — ITF-regulation tennis ball
    v_in=30.0,         # m/s — incoming ball speed
    e_base=0.45,       # —   — baseline coefficient of restitution
    L=0.685,           # m   — racket length
    x_handle=0.10,     # m   — handle reference point for shock calculation
)


# ---------------------------------------------------------------------------
# Design space bounds
# ---------------------------------------------------------------------------

DESIGN_BOUNDS = dict(
    m_racket=(0.285, 0.340),   # kg
    k_string=(2200.0, 4200.0), # N/m
    damping=(0.01, 0.08),      # dimensionless
    x_norm=(0.15, 0.95),       # normalised impact location
)


def sample_design_space(
    n: int = 7000,
    bounds: dict = None,
    seed: int = 7,
) -> pd.DataFrame:
    """
    Draw a random Latin-uniform sample of the racket design space.

    Parameters
    ----------
    n : int
        Number of design points to sample.
    bounds : dict, optional
        Override ``DESIGN_BOUNDS`` with custom (lo, hi) tuples keyed by
        variable name.
    seed : int
        NumPy random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Columns: m_racket, k_string, damping, x_norm.
    """
    rng = np.random.default_rng(seed)
    b = {**DESIGN_BOUNDS, **(bounds or {})}

    data = {
        var: rng.uniform(lo, hi, size=n)
        for var, (lo, hi) in b.items()
    }
    return pd.DataFrame(data)


def run_simulation(
    designs: pd.DataFrame,
    constants: dict = None,
) -> pd.DataFrame:
    """
    Evaluate impact and vibration performance for a batch of racket designs.

    Parameters
    ----------
    designs : pd.DataFrame
        Design parameters — must contain columns: m_racket, k_string,
        damping, x_norm.
    constants : dict, optional
        Override ``DEFAULTS`` with custom physical constants.

    Returns
    -------
    pd.DataFrame
        Input designs extended with computed outputs:
        v_exit, vib_score, shock_proxy.
    """
    c = {**DEFAULTS, **(constants or {})}

    df = designs.copy()

    # Coefficient of restitution (mildly string-stiffness dependent)
    df["e"] = cor_from_string_stiffness(df["k_string"], e_base=c["e_base"])

    # Effective mass at the impact point
    df["m_eff"] = effective_mass_at_impact(df["m_racket"], df["x_norm"])

    # Ball exit speed
    df["v_exit"] = exit_speed(c["v_in"], df["m_eff"], c["m_ball"], df["e"])

    # Vibration score at the impact point
    df["vib_score"] = vibration_score(
        df["x_norm"], df["k_string"], df["damping"], df["m_racket"]
    )

    # Handle shock proxy
    x_handle_norm = c["x_handle"] / c["L"]
    df["shock_proxy"] = shock_proxy(
        df["vib_score"],
        df["x_norm"],
        df["k_string"],
        x_handle_norm=x_handle_norm,
    )

    return df


def compute_sweet_score(
    df: pd.DataFrame,
    w_speed: float = 0.65,
    w_shock: float = 0.35,
) -> pd.DataFrame:
    """
    Add a composite 'sweet_score' column to the results DataFrame.

    The score normalises both exit speed (higher = better) and shock proxy
    (lower = better) to [0, 1] and combines them linearly:

        sweet_score = w_speed * v_norm  -  w_shock * s_norm

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: v_exit, shock_proxy.
    w_speed : float
        Weight for normalised exit speed (default 0.65).
    w_shock : float
        Weight for normalised shock proxy (default 0.35).

    Returns
    -------
    pd.DataFrame
        Input DataFrame with added column: sweet_score.
    """
    df = df.copy()
    eps = 1e-9

    v_norm = (df["v_exit"] - df["v_exit"].min()) / (df["v_exit"].max() - df["v_exit"].min() + eps)
    s_norm = (df["shock_proxy"] - df["shock_proxy"].min()) / (df["shock_proxy"].max() - df["shock_proxy"].min() + eps)

    df["sweet_score"] = w_speed * v_norm - w_shock * s_norm
    return df


def top_designs(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """
    Return the top-n designs ranked by sweet_score.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain column: sweet_score.
    n : int
        Number of top designs to return.

    Returns
    -------
    pd.DataFrame
        Sorted subset with the highest sweet_score values.
    """
    cols = ["sweet_score", "v_exit", "shock_proxy", "m_racket", "k_string", "damping", "x_norm"]
    available = [c for c in cols if c in df.columns]
    return df.sort_values("sweet_score", ascending=False).head(n)[available].reset_index(drop=True)
