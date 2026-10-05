# Decisions

Record only durable choices shared across analyses here. Unit-specific parameters, paths, thresholds, and tests belong in the owning unit README.

## Project and package identity

- Repository: `Nano_Simulations`.
- Package display name: Protein Simulation.
- Python distribution and Conda environment: `protein-simulation`.
- Python import: `protein_simulation`.
- Shared, analysis-neutral helpers belong in the package; simulation-specific code belongs in its compact unit.

## Scientific scope

- The workspace supports protein and molecular motor simulation research.
- No model, physical parameter values, simulation engine, dataset, or scientific hypothesis has been selected. Define these in the appropriate unit before scientific work begins.
