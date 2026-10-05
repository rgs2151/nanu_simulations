# baseline_simulation

## Method

- Recreate the professor's default DNA-rail transport model with the 14 user-facing scientific controls in `baseline.json`. One motor denotes one moving transporter object. Individual constituent DNA motors/polymerases are not resolved.
- Initialize 50 tracks with the original seed-0 geometry. Store first-to-last-site length and site counts for each track explicitly. The original rail length includes a terminal remainder shorter than one site spacing; that remainder is not used by its dynamics or renderer. Our length is the site-covered span, so the rendered geometry and dynamics remain identical.
- Put each track's permanent sites in one upstream cluster. All temporary sites begin OFF. Free motors encounter tracks in proportion to total site count and sample uniformly from valid footprint positions.
- Reject overlapping footprints. Within a valid footprint, combine ON-site binding opportunities as `1 - (1-p_temp)^n_temp_ON * (1-p_perm)^n_perm`. This independent-opportunity convention is the chosen interpretation of the new probability controls. At the baseline both probabilities are 1, exactly recovering the professor's any-ON-site capture rule without an extra random draw. OFF temporary sites cannot bind.
- Process motors in fixed index order. A bound motor attempts one forward site step with probability `speed * time_step / site_spacing`. An obstructed motor stalls; a motor attempting to leave the track detaches. On an unblocked step, it writes the new leading site with the specified writing probability, then undergoes a detachment trial.
- Preserve ON-dependent retention: detachment probability per successful step is `site_spacing / (motor_run_length * max(footprint_ON_fraction, 0.02))`, evaluated after writing. No separate unbinding clock runs while a motor stalls.
- After all motor updates, erase unoccupied temporary ON sites with probability `cutter_concentration * erasure_rate_per_concentration_s * time_step_s`. Permanent and motor-covered sites are protected. The baseline concentration is 1 relative reference unit and its calibration is 0.0008 s⁻¹ per reference unit, reproducing the professor's `K_OFF=0.0008` and per-step erasure probability 0.0004.
- Capture site states and motor track/position arrays at the specified sampling interval. Record distances only for completed runs, including end-truncated runs; still-bound runs are not included.
- Render a baseline GIF and final snapshot. With `--verify-reference`, execute only the original notebook's parameter assignments and simulation function definitions, compare every result array exactly, and render a synchronized comparison GIF from the two independent engine results. The two panels use the same rendering code so geometry and state differences would be visible without stylistic confounds.

## Variables

Edit `baseline.json` → `variables` for scientific controls. Scalar track lengths/site counts apply to every track; lists give one value per track in track-ID order. The baseline lists preserve the professor's heterogeneous realization rather than silently making all tracks identical.

| User variable | Python / JSON control | Baseline value and meaning |
| --- | --- | --- |
| # motors | `number_motors` | 40 moving transporter objects |
| # tracks | `number_tracks` | 50 tracks |
| Cutter concentration | `cutter_concentration` | 1 relative reference unit; experimentally uncalibrated |
| Brightness of motor | `motor_brightness` | 1 relative intensity, display only |
| Brightness of track | `track_brightness` | 1 relative background intensity, display only |
| Length of track | `track_length_um` | Explicit per-track spans, 7.896–20.398 µm; mean 13.79924 µm in this realization |
| # temporary sites | `number_temporary_sites` | Explicit per-track counts, 550–1,443; total 48,583; all initially OFF |
| # permanent sites | `number_permanent_sites` | 15 per track; total 750; initially and permanently ON |
| Motor speed | `motor_speed_um_s` | 0.010 µm/s, unblocked mean stepping speed |
| Motor run length | `motor_run_length_um` | 20 µm nominal distance scale at fully ON footprint, before track-end truncation |
| Motor size | `motor_size_um` | 0.400 µm, rounded to 29 sites; discrete footprint length 0.406 µm |
| p(binding given temp) | `binding_probability_temporary` | 1 per temporary ON-site opportunity within an encounter |
| p(binding given permanent) | `binding_probability_permanent` | 1 per permanent-site opportunity within an encounter |
| p(motor switches temp ON) | `writing_probability` | 1 per newly covered leading site during a successful step |

Site spacing is derived per track as `track_length_um / (temporary_sites + permanent_sites - 1)`, rounded to 12 decimal places in µm to remove floating-point inversion noise. At baseline it is exactly 0.014 µm. Changing site counts at fixed length therefore changes spacing, the discretized motor footprint, and per-step probabilities; those quantities are not independent physical controls.

`run` holds fixed calibration and numerical settings, separately from the 14 scientific handles:

- Chamber: 100 × 100 µm, a 2D geometry. No physical chamber depth or volume is modeled.
- Duration: 16,000 s; time step: 0.5 s; snapshots: every 200 s, giving 81 snapshots including time zero.
- Random seed: 0; free-motor encounter attempt rate: 0.2 s⁻¹.
- Concentration-to-erasure coefficient: 0.0008 s⁻¹ per relative concentration unit. The assumed linear response at other concentrations is not experimentally validated. A value in nM cannot be inferred from this notebook alone.
- Minimum ON fraction for retention: 0.02.
- `layout` stores original track starts, polarities, and the RNG state after original geometry generation. This preserves the professor's exact random-number sequence. Set `layout` to `null` to draw a new layout when changing track count, seed, or geometry so the stored layout no longer applies; update per-track vectors to the requested track count or use scalars. Shared settings remain centralized, not copied into alternative engines.
- Time settings must be integer multiples of the integration step. As in the notebook, the last snapshot is the last sampling multiple, which can precede the requested end for other duration/sampling combinations.

Outputs:

- `cache/baseline.npz`: simulation arrays, reused by default.
- `cache/manifest.json`: exact dynamics inputs, engine/parameter source hashes, NumPy and Python versions.
- `cache/reference.npz` and `cache/reference_manifest.json`: original-engine results and source/environment provenance when verification is requested.
- `plots/baseline.gif`: 81 baseline frames at 120 ms/frame, approximately 9.72 s per loop.
- `plots/comparison.gif`: original engine left, translated engine right; produced with `--verify-reference`.
- `plots/baseline_final.png`: final baseline frame.
- `plots/verification.json`: exact-array checks and descriptive baseline summaries.
- `plots/run_manifest.json`: full scientific controls, run settings, initialization, and source/environment identity for the displayed output.

## Statistics

- Model: discrete-time stochastic site-state and motor transport process, preserving the professor's baseline transition order and random draws.
- Numerical verification: exact array equality for track starts/directions, site-covered lengths, site counts/offsets/spacing, motor footprint sizes, permanent mask, snapshot times, every ON/OFF state, every motor track/position, and all completed-run distances. Pass only if every comparison is true; no numerical tolerance is used.
- This is software equivalence verification, not a statistical hypothesis test; null/alternative hypotheses and significance thresholds do not apply. It is appropriate because identical pseudorandom initialization and transition rules should produce identical trajectories.
- Descriptive summaries: number of sites, snapshots, completed runs, mean and median completed-run distance, and final track counts with ON fraction below 5%, above 40%, or between those boundaries inclusive. ON fraction includes permanent sites, exactly as in the notebook.
- Verified baseline: 49,333 sites, 81 snapshots, 1,030 completed runs, mean 5.81002718446602 µm, median 5.194 µm; final groups 18 low, 9 intermediate, 23 high.
- No uncertainty intervals, replicated-seed inference, formal bimodality test, or claim of experimentally validated bistability is made. Equivalence here covers this baseline realization; it does not prove equivalence of unimplemented alternative conditions.

## Legends

- Geometry: x/y positions in a 100 × 100 µm square; axis ticks hidden to match the professor's animation.
- Gray thin lines: tracks; the gray background contrast is proportional to `track_brightness` up to display saturation at 1.
- Orange thick segments: permanently ON upstream seed clusters, plotted in front of ON-site density.
- Red segments: total ON fraction within each spatial bin, encoded as opacity from 0 to 1. Bins are approximately 40 sites wide; permanent sites are included in that fraction.
- Blue thick bars: bound motors. Free motors are invisible. Bars are offset 0.7 µm perpendicular to the track for visibility, with nominal 0.400 µm size discretized to 29 sites. Opacity is `motor_brightness` clipped at display saturation 1.
- Relative brightness values are nonnegative, use fixed display exposure, and do not rescale each frame. This is a schematic display, not measured fluorescence, camera noise, or an optical point-spread model. Changing brightness does not change dynamics.
- Title: simulation time, total ON-site count, and bound-motor count.
- Comparison panels: professor's unchanged engine rerun on the left; shared translated engine on the right. Both use the same snapshot times and rendering conventions.
- Animation frames are uniformly spaced by 200 simulated seconds and displayed every 120 ms.

## Interpretation

- The GIF reproduces the professor's baseline dynamics with the requested scientific controls. Exact array equality supports fidelity more strongly than visual similarity alone.
- The active/inactive pattern is a property of this simulation and parameter realization; it is not by itself evidence of experimentally observed bistability.
- Motor run length is a nominal model parameter, distinct from realized completed-run distances. Cutter concentration is a calibrated relative handle, distinct from an absolute experimental concentration.

## Notes

Run from the repository root:

```bash
conda activate protein-simulation
python parking/baseline_simulation/baseline_simulation.py --verify-reference
```

The first run calculates and caches both engines. Later runs reuse matching caches and regenerate the unit's owned GIFs, snapshot, and reports. If a dynamics input, engine source, or recorded numerical environment changes, the runner refuses stale cache reuse and requires an explicit refresh:

```bash
python parking/baseline_simulation/baseline_simulation.py --recompute --verify-reference
```

For deliberately changed scientific values use `--recompute` without `--verify-reference`; exact reference comparison is reserved for the unchanged baseline preset. Brightness-only edits reuse the dynamics cache without recomputation. Cache files are ignored; plots and manifests are tracked. Each rendering run clears this unit's previous plot/report iteration.

- `protein_simulation/engine.py` is the single shared engine. No alternate permanent-site distributions or unprotected-cutting model has been implemented.
- `reference.py` is a baseline-only verification/initialization adapter. Normal translated simulations do not execute notebook code; `--verify-reference` and initial preset creation do.
- `reference.py` can recreate the preset only when `baseline.json` is absent, preventing accidental replacement of user edits.
- `render.py` owns this unit's rendering. Its style deliberately matches the professor's schematic rather than the project's later manuscript-figure style.
- Meaningful control checks live in `tests/test_engine.py`; run with `python -m unittest discover -s tests -v`.
- No manuscript caption is drafted yet. Future caption text belongs in this unit's `caption.md`.

## References

- `../../ref/dna_rail_transport_sim_en__1_.ipynb`, cells 1–4 for parameters, dynamics, and rendering; cells 7–8 for saved descriptive summaries.
- `../../ref/README.md`: source review and known limitations retained from the professor's baseline.
- `../../DECISIONS.md`: shared scientific parameter conventions.
