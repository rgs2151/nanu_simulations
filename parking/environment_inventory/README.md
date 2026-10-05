# environment_inventory

## Method

- Read the current Python interpreter version and installed Python distribution metadata from the active environment.
- Represent each installed distribution as its declared name and version; add one row for the Python interpreter.
- Sort rows by case-insensitive component name, then version. No research data, record alignment, filtering of scientific observations, or aggregation is involved.
- Write the version inventory as a two-column CSV table.

## Variables

- Data/input: `platform.python_version()` and `importlib.metadata.distributions()` in the active environment.
- Sessions/groups: one environment snapshot; one row per discoverable distribution plus Python.
- Labels/targets: `component` names the interpreter or installed distribution.
- Signals/features/measures: `version` is the declared software version string.
- Parameters/thresholds: no numerical thresholds; `--recompute` refreshes the snapshot.
- Cache: `cache/environment_inventory.json`, relative to this unit.
- Output: `plots/environment_inventory.csv`, relative to this unit.

## Statistics

- None; this output is descriptive. It lists versions without numerical summaries, fitted models, or statistical tests.
- Null hypothesis, alternative hypothesis, and decision threshold: not applicable; there is no inferential comparison.
- Version strings identify installed software; they do not measure simulation accuracy or numerical reproducibility.

## Legends

- Table columns: `component` is the installed software name; `version` is its version string.
- Ordering: ascending case-insensitive component name, then version.
- Grouping: each row is an interpreter or distribution entry; duplicate names remain separate if discoverable more than once.
- Axes, colors, lines, markers, and panels: not applicable; the output is a CSV table.

## Interpretation

- The inventory records which Python software versions were visible when the snapshot was collected.
- Use it to document the initial research environment. It does not validate a scientific model, check numerical results, or capture operating-system libraries and hardware.

## Notes

- Run from the repository root with `python parking/environment_inventory/environment_inventory.py` after activating `protein-simulation`.
- Existing cache contents are reused even if installed software has changed. Pass `--recompute` to capture the current environment.
- Each invocation replaces only this unit's previous CSV output. The cache is ignored by Git; the CSV is tracked.
- This setup diagnostic has no manuscript caption draft. Future figure captions belong in the owning unit's `caption.md`.

## References

- `../../ORGANIZATION.md`: compact-unit and output-ownership rules.
- `../../environment.yml` and `../../pyproject.toml`: declared environment and package dependencies.
