"""
Tennis Racket Virtual Prototyping Package
=========================================

Sub-modules
-----------
physics        — Core impact and vibration proxy models
simulation     — Monte Carlo design-space sampling & output computation
visualisation  — Plotting utilities for analysis and reporting
"""

from .physics import (
    clamp,
    effective_mass_at_impact,
    exit_speed,
    cor_from_string_stiffness,
    mode_shape_1,
    mode_shape_2,
    vibration_score,
    shock_proxy,
)

from .simulation import (
    DEFAULTS,
    DESIGN_BOUNDS,
    sample_design_space,
    run_simulation,
    compute_sweet_score,
    top_designs,
)

from .visualisation import plot_full_dashboard

__version__ = "1.0.0"
__author__ = "Tennis Racket Sim Contributors"
