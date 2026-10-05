# Decisions

Record only durable choices shared across analyses here. Unit-specific parameters, paths, thresholds, and tests belong in the owning unit README.

## Project and package identity

- Repository: `nanu_simulations`.
- Package display name: Protein Simulation.
- Python distribution and Conda environment: `protein-simulation`.
- Python import: `protein_simulation`.
- The shared simulation engine and scientific controls belong in the package. Experiment runners, parameter presets, and figure-specific code belong in compact units.

## Scientific scope

- The workspace supports protein and molecular motor simulation research.
- The professor’s DNA-rail transport notebook is preserved as reference material under `ref/`. Its model and defaults are a starting point for discussion, not validated project-wide scientific choices.
- No research dataset has been supplied. Record adopted model assumptions and parameters in the appropriate compact unit before scientific work begins.

## Baseline engine and scientific controls

- Use a single engine for all future conditions. The initial implementation follows the professor’s baseline: upstream permanent-site clusters, excluded motor footprints, protection of occupied temporary sites, and ON-dependent retention. Other conditions require explicit requests.
- “Motor” in the simulation API denotes one moving transporter object in the reference model, not an independently modeled constituent enzyme.
- Track lengths and permanent/temporary site counts are specified per track; either a scalar shared across tracks or a vector ordered by track ID is accepted.
- Track length in the discrete model is the first-to-last-site distance. Temporary and permanent counts partition all sites and determine spacing together with that length.
- Motor run length is the nominal run distance at full ON density, before track-end truncation. Report realized completed-run distances separately.
- Cutter concentration is currently a relative concentration, with 1 reference unit mapped to the professor’s erasure rate. The linear concentration-to-rate conversion is an explicit calibration assumption, not an experimentally measured kinetic law.
- Brightness controls define mean intrinsic fluorescence of the motor and track populations in relative units. Sample persistent per-object values once on a separate RNG stream, cache them, and share the same values across compared conditions. Optical readout uses these attributes; no unrequested coupling to binding, movement, or cleavage is assumed. This is not a calibrated microscope or photon-counting model.
- For a footprint containing multiple ON sites, binding probability is one minus the product of per-site failure probabilities, with separate probabilities for permanent and temporary sites. This is the chosen extension of the professor’s “any ON site binds” rule; the two probabilities equal 1 in the baseline.

## Isolated model comparisons

- Conditions use the shared engine and a shared resolved configuration. Change only the specified rule; record any intentionally changed numerical control alongside it.
- Unprotected cutting erases temporary ON sites even inside motor footprints; it does not directly remove motors or erase permanent sites. Motor detachment still follows the selected run rule.
- Fixed-step runs release a motor after the specified number of successful forward steps since binding, or at the track end if reached earlier. Stalling consumes time but not the step budget; rebinding starts a new run.
- Random permanent-site placement samples unique site indices without replacement, maintaining the specified per-track count. Placement randomness is separate from dynamics and fluorescence randomness.
- The original baseline comparison artifacts are preserved. New conditions use their own cached results and renderer.
