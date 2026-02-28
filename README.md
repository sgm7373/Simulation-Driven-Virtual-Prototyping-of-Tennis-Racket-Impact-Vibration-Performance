# 🎾 Tennis Racket Virtual Prototyping
### Simulation-Driven Impact & Vibration Performance Analysis

[(https://github.com/sgm7373/tennis-racket-sim/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/tennis-racket-sim/actions)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

---

## 📌 Overview

This project implements a **physics-based Monte Carlo virtual prototyping framework** for evaluating and optimising tennis racket design. Rather than manufacturing multiple physical prototypes, this tool simulates thousands of design configurations in seconds — exploring the trade-off between **ball exit speed** (power) and **handle shock** (player comfort/injury risk).

The methodology is inspired by simulation-driven design practices used in sports engineering, where analytical proxy models enable rapid exploration of a high-dimensional design space before committing to expensive manufacturing.

### Key capabilities

- **7,000+ design point Monte Carlo sweep** across 4 independent design variables
- **Physics-based proxy models** for impact mechanics and structural vibration
- **Sweet-spot scoring** — a configurable weighted composite metric
- **Pareto trade-off visualisation** between power and comfort
- **Correlation analysis** to identify which parameters drive performance
- Full modular Python package with unit tests and CI/CD pipeline

---

## 🔬 Physics Background

### Impact Mechanics

Ball–racket impact is modelled as a **1D rigid-body collision** using the coefficient-of-restitution (COR) framework:

```
v_exit = (1 + e) × (m_eff / (m_eff + m_ball)) × v_in
```

where:
- `v_in`   = incoming ball speed (30 m/s)
- `e`      = coefficient of restitution (0.35–0.55, mildly stiffness-dependent)
- `m_eff`  = effective racket mass at the impact point
- `m_ball` = tennis ball mass (58 g)

The **effective mass** increases from handle to tip via a power-law interpolation, reflecting the rotational inertia distribution of the frame.

### Vibration Model

Post-impact vibration is estimated using a **two-mode proxy model**:

```
V = (φ₁² + 0.6φ₂²) × k_factor × damp_factor × mass_factor
```

where `φ₁`, `φ₂` are sine-wave bending mode shapes evaluated at the impact location. This captures the core physics of modal energy injection without requiring full FEM simulation.

### Handle Shock Proxy

The shock felt at the grip is a function of:
1. Vibration amplitude at the impact location
2. Distance of the impact point from the handle (torque/shock transmission)
3. String stiffness (stiffer strings transmit more impulse)
4. A small stochastic noise term representing real-world variability

### Sweet Spot Score

A single composite metric combining both objectives:

```
sweet_score = 0.65 × norm(v_exit)  −  0.35 × norm(shock_proxy)
```

Weights are configurable. Higher scores represent designs that are both powerful and comfortable.

---

## 📁 Project Structure

```
tennis-racket-sim/
│
├── notebooks/
│   └── tennis_racket_simulation.ipynb   # Original interactive Jupyter notebook
│
├── src/
│   ├── __init__.py                      # Package init / public API
│   ├── physics.py                       # Core impact & vibration proxy models
│   ├── simulation.py                    # Monte Carlo sampling & output computation
│   └── visualisation.py                 # Publication-quality plotting utilities
│
├── tests/
│   ├── __init__.py
│   ├── test_physics.py                  # Unit tests for physics functions
│   └── test_simulation.py               # Unit tests for simulation pipeline
│
├── outputs/                             # Generated figures and CSV exports (gitignored)
│   └── .gitkeep
│
├── .github/
│   └── workflows/
│       └── ci.yml                       # GitHub Actions CI pipeline
│
├── main.py                              # CLI entry point
├── requirements.txt                     # Python dependencies
├── setup.py                             # Package installation config
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/tennis-racket-sim.git
cd tennis-racket-sim
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the simulation

```bash
python main.py
```

This runs 7,000 Monte Carlo samples with default settings and displays the full performance dashboard.

---

## 🖥️ Command-Line Usage

```bash
python main.py [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--n` | 7000 | Number of Monte Carlo design samples |
| `--seed` | 7 | Random seed for reproducibility |
| `--w-speed` | 0.65 | Sweet score weight for exit speed |
| `--w-shock` | 0.35 | Sweet score weight for shock proxy |
| `--top` | 15 | Number of top designs to print |
| `--save-csv PATH` | None | Export full results to CSV |
| `--save-fig PATH` | None | Save dashboard figure to PNG/PDF |
| `--no-plot` | False | Skip all plotting (useful for CI/batch) |

### Examples

```bash
# Default run — 7000 samples, show plot
python main.py

# Larger sweep, save outputs
python main.py --n 20000 --seed 123 --save-csv outputs/results.csv --save-fig outputs/dashboard.png

# Comfort-biased scoring (70% shock weight)
python main.py --w-speed 0.30 --w-shock 0.70

# Headless batch run (no matplotlib window)
python main.py --n 5000 --no-plot --save-csv outputs/batch.csv
```

---

## 📓 Jupyter Notebook

The original exploratory analysis is preserved in `notebooks/tennis_racket_simulation.ipynb`. To run it:

```bash
pip install jupyter
jupyter notebook notebooks/tennis_racket_simulation.ipynb
```

Or open it in JupyterLab:

```bash
pip install jupyterlab
jupyter lab
```

The notebook walks through the same physics, sampling, and visualisation steps interactively, cell by cell.

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pip install pytest-cov
pytest tests/ -v --cov=src --cov-report=term-missing

# Run a specific test file
pytest tests/test_physics.py -v
```

All tests are located in `tests/` and cover:
- Physics function correctness (monotonicity, bounds, expected relationships)
- Simulation pipeline (column completeness, NaN-free outputs, reproducibility)
- Score computation (weight effects, sorting correctness)

---

## 🔧 Using as a Python Package

You can import the `src` package directly in your own scripts:

```python
from src.simulation import sample_design_space, run_simulation, compute_sweet_score, top_designs
from src.visualisation import plot_full_dashboard
import matplotlib.pyplot as plt

# Sample 10,000 designs
designs = sample_design_space(n=10_000, seed=42)

# Run physics simulation
results = run_simulation(designs)

# Compute composite score
results = compute_sweet_score(results, w_speed=0.70, w_shock=0.30)

# Show top designs
print(top_designs(results, n=10))

# Plot dashboard
fig = plot_full_dashboard(results, top_designs(results))
plt.show()
```

### Custom design bounds

```python
from src.simulation import sample_design_space, run_simulation

# Override default bounds
my_bounds = {
    "m_racket": (0.270, 0.360),   # lighter/heavier range
    "k_string": (1800.0, 5000.0), # wider stiffness sweep
    "damping":  (0.005, 0.12),
    "x_norm":   (0.10, 0.98),
}

designs = sample_design_space(n=5000, bounds=my_bounds, seed=0)
results = run_simulation(designs)
```

### Custom physical constants

```python
from src.simulation import run_simulation

# Simulate a harder-hit ball (serve speed ~50 m/s)
results = run_simulation(designs, constants={"v_in": 50.0, "m_ball": 0.058})
```

---

## 📊 Output Variables

| Column | Description | Units |
|---|---|---|
| `m_racket` | Total racket mass | kg |
| `k_string` | String stiffness proxy | N/m |
| `damping` | Structural damping ratio | — |
| `x_norm` | Impact location (0=handle, 1=tip) | — |
| `e` | Coefficient of restitution | — |
| `m_eff` | Effective mass at impact point | kg |
| `v_exit` | Ball rebound speed | m/s |
| `vib_score` | Vibration proxy at impact location | a.u. |
| `shock_proxy` | Handle shock experienced by player | a.u. |
| `sweet_score` | Composite sweet-spot score (higher = better) | — |

---

## 📈 Key Findings (Default Run)

From the 7,000-sample sweep with default parameters:

- **Best impact zone**: approximately 55–75% along the racket length from the handle — aligns with the classical sweet spot in racket mechanics literature.
- **Exit speed range**: ~19–30 m/s (mean ~25 m/s), driven primarily by impact location and racket mass.
- **Dominant parameters** (by correlation magnitude): impact location (`x_norm`) has the strongest influence on both exit speed and shock; damping ratio is the primary driver for vibration reduction.
- **String stiffness trade-off**: stiffer strings increase exit speed (via COR) but also increase handle shock — demonstrating a clear Pareto tension.

---

## 🛠️ Extending the Project

Some directions to take this further:

- **Smarter sampling**: Replace uniform random sampling with Latin Hypercube Sampling (LHS) or Sobol sequences for better design-space coverage at lower N.
- **Formal Pareto extraction**: Implement NSGA-II or DEAP-based multi-objective optimisation instead of scalar weighting.
- **Sensitivity analysis**: Replace correlation with variance-based Sobol sensitivity indices (e.g. using the `SALib` library).
- **Higher-fidelity physics**: Couple with a beam FEM solver (e.g. via `scipy` sparse methods) for more accurate mode shapes and natural frequencies.
- **String plane model**: Add a 2D string-bed model to simulate off-centre impacts.
- **Player arm model**: Include a coupled arm impedance model for more realistic shock transmission estimation.

---

## 📚 References

1. Cross, R. (2011). *Physics of Baseball & Softball*. Springer.
2. Brody, H., Cross, R., & Lindsey, C. (2002). *The Physics and Technology of Tennis*. USRSA.
3. Hatze, H. (1993). The relationship between the coefficient of restitution and energy losses in tennis rackets. *Journal of Applied Biomechanics*, 9(2), 124–142.
4. ITF Technical Centre — [Tennis ball specifications](https://www.itftennis.com/technical).

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add: your feature description"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request against `main`

Please ensure all tests pass (`pytest tests/ -v`) before submitting a PR.

---

## 👤 Author

Built and maintained by **Sourabh More**
📧 more.sourabh7373.com
🔗 [github.com/sgm7373](https://github.com/sgm7373)

---

*If you find this project useful, please consider giving it a ⭐ on GitHub!*
