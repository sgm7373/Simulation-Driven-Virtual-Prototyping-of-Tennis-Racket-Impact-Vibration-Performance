"""
physics.py
----------
Core physics proxy models for tennis racket impact and vibration simulation.

All models are intentionally simplified (analytical proxies) for fast Monte Carlo
sweep across a large design space. They are NOT full FEM / multi-body dynamics.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def clamp(a, lo, hi):
    """Element-wise clamp of array or scalar to [lo, hi]."""
    return np.minimum(np.maximum(a, lo), hi)


# ---------------------------------------------------------------------------
# Impact mechanics
# ---------------------------------------------------------------------------

def effective_mass_at_impact(m_racket: np.ndarray, x_norm: np.ndarray) -> np.ndarray:
    """
    Compute the effective (apparent) mass of the racket at a given impact location.

    The effective mass felt by the ball increases from handle to tip, modelled
    as a power-law interpolation between a minimum and maximum fraction of total
    racket mass.

    Parameters
    ----------
    m_racket : array-like
        Total racket mass in kg.
    x_norm : array-like
        Normalised impact location along the racket length.
        0 = handle end, 1 = tip end.

    Returns
    -------
    np.ndarray
        Effective mass in kg at the impact point.
    """
    r_min, r_max = 0.12, 0.35
    ratio = r_min + (r_max - r_min) * (np.asarray(x_norm) ** 0.8)
    return ratio * np.asarray(m_racket)


def exit_speed(v_in: float, m_eff: np.ndarray, m_ball: float, e: np.ndarray) -> np.ndarray:
    """
    Estimate ball rebound (exit) speed from a simplified 1-D impact model.

    Uses the coefficient-of-restitution (COR) formulation for a ball impacting
    a free rigid body.

    Parameters
    ----------
    v_in : float
        Incoming ball speed in m/s (scalar).
    m_eff : array-like
        Effective racket mass at the impact point (kg).
    m_ball : float
        Tennis ball mass in kg.
    e : array-like
        Coefficient of restitution (COR), dimensionless, typically 0.35–0.55.

    Returns
    -------
    np.ndarray
        Ball exit speed in m/s.
    """
    m_eff = np.asarray(m_eff)
    e = np.asarray(e)
    return (1.0 + e) * (m_eff / (m_eff + m_ball)) * v_in


def cor_from_string_stiffness(k_string: np.ndarray, e_base: float = 0.45) -> np.ndarray:
    """
    Adjust coefficient of restitution based on string stiffness.

    Stiffer strings produce a slightly more elastic (higher COR) impact.

    Parameters
    ----------
    k_string : array-like
        String stiffness proxy in N/m.
    e_base : float
        Baseline COR value (default 0.45).

    Returns
    -------
    np.ndarray
        Adjusted COR, clamped to [0.35, 0.55].
    """
    e = e_base + 0.08 * (np.asarray(k_string) - 3000.0) / 1200.0
    return clamp(e, 0.35, 0.55)


# ---------------------------------------------------------------------------
# Vibration / modal analysis proxies
# ---------------------------------------------------------------------------

def mode_shape_1(x_norm: np.ndarray) -> np.ndarray:
    """
    First bending mode shape proxy along the normalised racket length.

    Approximated as a half-sine wave (zero near handle, peak near mid-shaft).

    Parameters
    ----------
    x_norm : array-like
        Normalised position, 0 = handle, 1 = tip.

    Returns
    -------
    np.ndarray
        Mode shape amplitude (dimensionless).
    """
    return np.sin(np.pi * np.asarray(x_norm))


def mode_shape_2(x_norm: np.ndarray) -> np.ndarray:
    """
    Second bending mode shape proxy.

    Approximated as a full-sine wave with one interior node.

    Parameters
    ----------
    x_norm : array-like
        Normalised position.

    Returns
    -------
    np.ndarray
        Mode shape amplitude (dimensionless).
    """
    return np.sin(2.0 * np.pi * np.asarray(x_norm))


def vibration_score(
    x_norm: np.ndarray,
    k_string: np.ndarray,
    damping: np.ndarray,
    m_racket: np.ndarray,
) -> np.ndarray:
    """
    Compute a composite vibration / arm-shock proxy for each design.

    Combines modal energy injection, string stiffness amplification, structural
    damping attenuation, and mass-based inertial damping.

    Parameters
    ----------
    x_norm : array-like
        Normalised impact location (0=handle, 1=tip).
    k_string : array-like
        String stiffness proxy (N/m).
    damping : array-like
        Structural damping ratio (dimensionless, e.g. 0.01–0.08).
    m_racket : array-like
        Total racket mass (kg).

    Returns
    -------
    np.ndarray
        Vibration score (arbitrary units, lower is better for player comfort).
    """
    x_norm   = np.asarray(x_norm)
    k_string = np.asarray(k_string)
    damping  = np.asarray(damping)
    m_racket = np.asarray(m_racket)

    phi1 = mode_shape_1(x_norm)
    phi2 = mode_shape_2(x_norm)

    injected         = phi1 ** 2 + 0.6 * phi2 ** 2
    stiffness_factor = (k_string / 3000.0) ** 0.35
    damp_factor      = 1.0 / (1.0 + 8.0 * damping)
    mass_factor      = (0.32 / m_racket) ** 0.25

    return injected * stiffness_factor * damp_factor * mass_factor


def shock_proxy(
    vib: np.ndarray,
    x_norm: np.ndarray,
    k_string: np.ndarray,
    x_handle_norm: float = 0.10 / 0.685,
    noise_std: float = 0.04,
    rng: np.random.Generator = None,
) -> np.ndarray:
    """
    Compute the handle shock proxy experienced by the player.

    Combines vibration amplitude with an impact-location distance factor and
    a small stochastic noise term to represent real-world variability.

    Parameters
    ----------
    vib : array-like
        Vibration score from :func:`vibration_score`.
    x_norm : array-like
        Normalised impact location.
    k_string : array-like
        String stiffness proxy (N/m).
    x_handle_norm : float
        Handle reference position (normalised), default ≈ 0.146.
    noise_std : float
        Standard deviation of additive Gaussian noise (default 0.04).
    rng : np.random.Generator, optional
        Random generator for reproducibility. If None, uses the global state.

    Returns
    -------
    np.ndarray
        Shock proxy values (lower is better for player comfort).
    """
    vib      = np.asarray(vib)
    x_norm   = np.asarray(x_norm)
    k_string = np.asarray(k_string)

    dist_factor = clamp(x_norm - x_handle_norm, 0.0, 1.0)

    if rng is None:
        noise = np.random.normal(0, noise_std, size=vib.shape)
    else:
        noise = rng.normal(0, noise_std, size=vib.shape)

    stiff_boost = 1.0 + 0.12 * (k_string - 3000.0) / 1200.0

    return vib * (0.55 + 0.45 * dist_factor) * stiff_boost + noise
