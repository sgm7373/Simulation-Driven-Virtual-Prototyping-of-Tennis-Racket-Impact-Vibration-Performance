#!/usr/bin/env python3
"""
main.py
-------
Command-line entry point for the Tennis Racket Virtual Prototyping simulation.

Usage examples
--------------
# Run default simulation (7000 samples) and save outputs
    python main.py

# Custom sample count and seed
    python main.py --n 5000 --seed 42

# Custom score weights (speed/shock)
    python main.py --w-speed 0.70 --w-shock 0.30

# Save dashboard figure
    python main.py --save-fig outputs/dashboard.png
"""

import argparse
import os
import sys

import pandas as pd

# Allow running from the repo root without installing the package
sys.path.insert(0, os.path.dirname(__file__))

from src.simulation import sample_design_space, run_simulation, compute_sweet_score, top_designs
from src.visualisation import plot_full_dashboard


def parse_args():
    p = argparse.ArgumentParser(
        description="Tennis Racket Impact & Vibration Virtual Prototyping"
    )
    p.add_argument("--n",        type=int,   default=7000,  help="Number of Monte Carlo samples")
    p.add_argument("--seed",     type=int,   default=7,     help="Random seed")
    p.add_argument("--w-speed",  type=float, default=0.65,  help="Weight for exit speed in sweet score")
    p.add_argument("--w-shock",  type=float, default=0.35,  help="Weight for shock proxy in sweet score")
    p.add_argument("--top",      type=int,   default=15,    help="Number of top designs to display")
    p.add_argument("--save-csv", type=str,   default=None,  help="Save full results to CSV (path)")
    p.add_argument("--save-fig", type=str,   default=None,  help="Save dashboard figure (path)")
    p.add_argument("--no-plot",  action="store_true",       help="Skip plotting entirely")
    return p.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("  Tennis Racket Virtual Prototyping — Simulation Engine")
    print("=" * 60)
    print(f"  Samples  : {args.n:,}")
    print(f"  Seed     : {args.seed}")
    print(f"  Weights  : speed={args.w_speed:.2f}, shock={args.w_shock:.2f}")
    print()

    # 1. Sample design space
    print("▶  Sampling design space ...")
    designs = sample_design_space(n=args.n, seed=args.seed)

    # 2. Run simulation
    print("▶  Running simulation ...")
    results = run_simulation(designs)

    # 3. Compute sweet score
    results = compute_sweet_score(results, w_speed=args.w_speed, w_shock=args.w_shock)

    # 4. Summary stats
    print("\n── Summary Statistics ──────────────────────────────────────")
    print(results[["v_exit", "shock_proxy", "sweet_score"]].describe().round(4).to_string())

    # 5. Top designs
    best = top_designs(results, n=args.top)
    print(f"\n── Top {args.top} Designs ───────────────────────────────────────")
    print(best.to_string(index=False))

    # 6. Optional CSV export
    if args.save_csv:
        os.makedirs(os.path.dirname(args.save_csv) or ".", exist_ok=True)
        results.to_csv(args.save_csv, index=False)
        print(f"\n✔  Full results saved → {args.save_csv}")

    # 7. Optional plotting
    if not args.no_plot:
        import matplotlib
        if args.save_fig:
            matplotlib.use("Agg")  # headless rendering when saving
        import matplotlib.pyplot as plt

        save_path = args.save_fig
        if save_path:
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

        plot_full_dashboard(results, best, save_path=save_path)

        if not args.save_fig:
            plt.show()

    print("\n✔  Done.\n")


if __name__ == "__main__":
    main()
