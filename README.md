# nanu_simulations

Research workspace for protein and molecular motor simulations, with reproducible analysis units and figure outputs.

The Python package is **Protein Simulation**: installable as `protein-simulation`, imported as `protein_simulation`. The professor’s DNA-rail transport baseline is implemented in the shared package with 14 scientific controls. See [the baseline unit](parking/baseline_simulation/README.md) for the variable mapping, GIFs, and exact reference comparison. The original notebook remains unchanged in `ref/`. No experimental dataset has been supplied.

## Setup

From the repository root:

```bash
conda env create -f environment.yml
conda activate protein-simulation
```

The environment includes an editable package install, scientific Python dependencies, and JupyterLab. To reinstall after package metadata changes:

```bash
python -m pip install -e .
```

## Running Units

Exploratory compact units live in `parking/`; finalized units graduate to `figs/`. Each unit owns its code, README, local `cache/`, and tracked `plots/` outputs. Caption drafts belong in that unit's `caption.md`.

Reproduce the baseline and its comparison GIF:

```bash
python parking/baseline_simulation/baseline_simulation.py --verify-reference
```

Edit scientific values in `parking/baseline_simulation/baseline.json`. Changed dynamics require `--recompute`; changed values should omit `--verify-reference`, which is reserved for the original preset. See the unit README for concentration calibration, track/site definitions, and cache rules.

An environment diagnostic records installed versions:

```bash
python parking/environment_inventory/environment_inventory.py
```

Existing caches are reused. After changing the environment, refresh the inventory explicitly:

```bash
python parking/environment_inventory/environment_inventory.py --recompute
```

See [the unit README](parking/environment_inventory/README.md) for output columns and limitations. This is a setup diagnostic; it does not run a scientific simulation.

## Data

`data/` holds organized analysis-ready inputs. There are currently no research datasets. See [data/README.md](data/README.md) for inventory and rules for documenting future inputs. Local data and compute caches are ignored by Git; plot and table outputs are tracked.

## Project Docs

- `AGENTS.md`: agent working rules.
- `ORGANIZATION.md`: folder layout, compact units, cache ownership, and documentation conventions.
- `STYLE.md`: matplotlib/seaborn figure standards.
- `DECISIONS.md`: durable project-wide choices.
- `skills/`: local Rudra documentation and debugging workflows.

Initialized from the private [research template](https://github.com/rgs2151/research_template).
