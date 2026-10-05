# Decisions

Record only durable choices shared across analyses here. Unit-specific parameters, paths, thresholds, and tests belong in the owning unit README.

## Project and package identity

- Repository: `nanu_simulations`.
- Package display name: Protein Simulation.
- Python distribution and Conda environment: `protein-simulation`.
- Python import: `protein_simulation`.
- Shared, analysis-neutral helpers belong in the package; simulation-specific code belongs in its compact unit.

## Scientific scope

- The workspace supports protein and molecular motor simulation research.
- The professor’s DNA-rail transport notebook is preserved as reference material under `ref/`. Its model and defaults are a starting point for discussion, not validated project-wide scientific choices.
- No research dataset has been supplied. Record adopted model assumptions and parameters in the appropriate compact unit before scientific work begins.
