# conditions — shared setup

This unit generates four GIFs from one shared transport engine: `baseline`, `cutter`, `motor`, and `permanent`. It preserves the original notebook-comparison artifacts in `../baseline_simulation/plots/` and introduces no summary plots or claims about condition effects.

## Method

- Resolve the scientific variables, numerical settings, and track layout once from `../baseline_simulation/baseline.json`, then apply the common overrides in `config.json`. Each condition receives these same inputs; only its named model-rule switch changes.
- Draw intrinsic fluorescence once for each motor ID and track ID, using a separate random stream. Cache this shared population and use those exact values in all four conditions. These are persistent object properties, not new random drawing styles each frame. No bleaching, optical noise, or fluorescence-dependent chemical kinetics is assumed.
- Simulate with `protein_simulation.engine.simulate`. Every condition keeps exclusion, writing, geometry, encounters, and numerical integration identical unless its named rule changes the relevant mechanism.
- Cache all site-state and motor-position histories. Render the four GIFs from those arrays using one shared renderer, fixed exposure, and matching timestamps. No simulation is executed in `--render-only` mode.

## Variables

All 14 variables are identical between these four runs:

| Variable | Shared value |
| --- | --- |
| Number of motors | 40 transporter objects |
| Number of tracks | 50 |
| Cutter concentration | 1 relative reference unit; erasure coefficient 0.0008 s⁻¹ per unit |
| Brightness of motor | Mean 1 relative fluorescence unit; each motor sampled uniformly from 0.9–1.1 |
| Brightness of track | Mean 0.12 relative fluorescence units; each track sampled uniformly from 0.108–0.132 |
| Length of track | Same 50 first-to-last-site spans from the baseline preset, 7.896–20.398 µm |
| Number of temporary sites | Same per-track counts, 550–1,443; 48,583 total |
| Number of permanent sites | 15 per track; 750 total |
| Motor speed | 0.010 µm/s mean unblocked speed |
| Motor run length | Baseline nominal value 20 µm; unused in the fixed-step condition, whose separate cutoff is below |
| Motor size | 0.400 µm nominal; 29 sites / 0.406 µm after discretization |
| Binding probability at an ON temporary site | 1 |
| Binding probability at a permanent site | 1 |
| Probability of writing an advancing leading site ON | 1 |

The common fluorescence population replaces the prior scalar rendering convention for these four new GIFs only. It does not alter the old comparison GIF or baseline dynamics. The ranges are illustrative assumptions, not measured fluorescence distributions.

Additional model and numerical controls:

| Control | Setting |
| --- | --- |
| `fixed_run_steps` | 357 successful forward steps (4.998 µm at 14 nm/site); used only by `motor` |
| `permanent_position_sd_fraction` | 0.3 of normalized track length; used only by `permanent` |
| Permanent-position mean | Midpoint of each track, normalized position 0.5 |
| Fluorescence fractional half-range | 0.1, shared by the two population brightness distributions |
| Chamber / duration / time step / sample interval | 100 × 100 µm / 16,000 s / 0.5 s / 200 s |
| Dynamics seed and starting layout | Same seed-0 baseline realization and post-layout RNG state |
| Fluorescence RNG / site-placement RNG | Separate deterministic NumPy streams seeded by `[0, 947]` / `[0, 173]` |
| Encounter rate / ON-density floor | 0.2 s⁻¹ / 0.02 |

Each condition starts a separate simulation with the same dynamics RNG state. Different rules can consume different numbers of random draws, so the subsequent stochastic events are not matched event-by-event. The common initialization is not a substitute for later replicated-seed comparisons.

Configuration lives in `config.json`: one `shared_baseline` reference, common variable overrides, population fluorescence settings, common rule defaults, and four minimal condition overrides. There are no copied simulation loops.

Outputs:

- `cache/population.npz`: per-motor and per-track fluorescence, indexed by persistent object ID.
- `cache/population.json`: population-generation inputs and source/version identity.
- `cache/{baseline,cutter,motor,permanent}.npz`: complete state histories, geometry, masks, and completed runs.
- `cache/{name}.json`: each simulation's resolved shared inputs, rule settings, source hashes, and Python/NumPy versions.
- `cache/validation.json`: rule-isolation and state-invariant checks.
- `plots/{name}.gif`: four animations, 81 frames each at 120 ms/frame, looping.
- `plots/{name}_final.png`: final-frame previews for inspecting the renderer.
- `plots/manifest.json`: resolved condition inputs, actual sampled fluorescence arrays, and rendering source hash.
- `plots/validation.json`: published copy of the invariant checks; it is not a condition-effect analysis.

## Statistics

- No statistical hypothesis tests, model fitting, effect-size comparisons, uncertainty estimates, or scientific summary plots are performed.
- Verification requires exact equality of shared track starts/directions/lengths/spacing and snapshot times, equal site counts, equal permanent-site counts, and permanent sites remaining ON in every condition.
- Each variant must differ from the unit baseline in exactly its specified model-rule field. The unchanged baseline must exactly match all arrays in the existing professor-reference cache when that cache is available. This cache was available and the check passed for the committed run; a fresh checkout without that local cache reports the reference check unavailable rather than claiming verification.
- These are deterministic software acceptance checks; null/alternative hypotheses and significance thresholds do not apply. They establish implementation behavior, not scientific or experimental superiority over the reference model.

## Legends

- Gray line: track background fluorescence. Each track retains its own sampled brightness throughout all frames and conditions.
- Red line opacity: number of temporary ON sites divided by all sites in a spatial bin, approximately 40 sites wide. Permanent sites are excluded from the numerator; this explicitly differs from the original comparison renderer's total-ON density. OFF temporary sites have no red signal.
- Gold outlined diamonds: permanent ON sites, offset 1.1 µm perpendicular to the track on the opposite side from the motors. Faint connectors mark their original track coordinates. At this scale upstream clusters overlap into a compact gold glyph; scattered sites are drawn individually and close sites may also overlap.
- Blue bars: bound motors, offset 0.9 µm perpendicular to the track. Opacity follows the stored motor-specific fluorescence. Free motors are not displayed.
- Exposure: the same transfer `sqrt(clip(brightness / 1.1, 0, 1))` is used for motor and track alpha in all GIFs. It improves visibility of dim tracks while preserving their lower relative signal; it is not a calibrated optical acquisition model. Geometric marker widths and offsets are display aids, not altered physical footprints.
- Chamber outline and 10 µm scale bar are identical between conditions. The sidebar shows the rule, conventional artist-based legend, time in seconds, bound-motor count, temporary-ON count, and permanent-ON count.
- No sorting or frame-wise/condition-wise intensity normalization is applied. Each frame corresponds to the same sampled physical time across all conditions.

## Interpretation

- The GIFs allow qualitative inspection of implementation and readability. The shared population and renderer make optical differences less likely to be mistaken for model differences.
- The deterministic run condition intentionally introduces a 357-step cutoff instead of the baseline's 20 µm full-ON stochastic run scale. This requested new cutoff is an explicit additional control. Differences cannot yet be attributed to deterministic versus stochastic release independently of the chosen cutoff magnitude; that requires the planned parameter sweep.
- Normal-weighted placement is center-biased, not uniform along a track. It maintains exact counts while changing only the placement mechanism.

## Notes

From the repository root:

```bash
conda activate protein-simulation
# Simulate missing caches, then render; reject stale caches.
python parking/conditions/conditions.py
# Iterate on GIF appearance without running simulations.
python parking/conditions/conditions.py --render-only
# Explicitly refresh numerical results after changing inputs/rules.
python parking/conditions/conditions.py --recompute
# Cache numerical results without rendering.
python parking/conditions/conditions.py --simulate-only
```

A renderer-only code edit does not invalidate simulation caches. Changed shared inputs, model settings, or numerical source identity require `--recompute`. Rendering clears and replaces only this unit's `plots/` iteration. Caches remain ignored by Git; GIFs, previews, configuration, manifests, and documentation are tracked.

The reference-comparison unit and its existing outputs are untouched. The core engine defaults retain its baseline behavior. No manuscript captions are drafted yet; future caption drafts belong in this unit's `caption.md`.

## References

- `../../protein_simulation/engine.py` and `../../protein_simulation/parameters.py`: shared dynamics, rule switches, and population properties.
- `../baseline_simulation/baseline.json`: shared scientific variables and original geometry.
- `../../ref/dna_rail_transport_sim_en__1_.ipynb`: original baseline reference.

# baseline

## Method

- Run the shared engine with protected occupied sites, ON-density-dependent stochastic detachment, and upstream permanent clusters.
- Render this unchanged baseline dynamics realization with the new common fluorescence population and renderer.

## Variables

- All 14 scientific variables, starting geometry, timing, and object fluorescence are defined in the shared setup above.
- Rule overrides: none.
- Cache: `cache/baseline.npz`; outputs: `plots/baseline.gif` and `plots/baseline_final.png`.

## Statistics

- No inferential test. Every result array is compared exactly with the preserved professor-reference cache when available; all comparisons passed for this run. No null/alternative hypothesis or significance threshold applies.

## Legends

- Gray: per-track fluorescence; red opacity: temporary ON sites per bin divided by total sites; gold diamonds: permanent ON sites offset opposite blue bound-motor bars. Blue brightness is fixed per motor ID. Time and counts are shown in the sidebar. Scale and exposure match the other three GIFs.

## Interpretation

- This is the control condition for the three new model-rule variants. The appearance differs from the archived comparison GIF; the numerical baseline trajectory does not.

## Notes

- The 15 permanent sites per track are contiguous at its upstream end. They may appear as one compact gold glyph at chamber scale.

## References

- `../baseline_simulation/README.md`; shared setup and rendering definitions above.

# cutter

## Method

- Set `protect_occupied_sites=False` and retain the other baseline rules.
- After motor updates, every temporary ON site is eligible for erasure, including sites under bound motors. Per-step erasure probability remains 0.0004.
- Cutting turns sites OFF; it does not directly detach motors. On later successful steps, the unchanged ON-density-dependent detachment rule can respond to reduced footprint ON density.

## Variables

- All 14 scientific variables, starting geometry, timing, and sampled object fluorescence match the control.
- Only rule change: `protect_occupied_sites=False`.
- Cache: `cache/cutter.npz`; outputs: `plots/cutter.gif` and `plots/cutter_final.png`.

## Statistics

- No inferential test. Shared-input invariants pass. A mechanistic test sets the erasure probability to 1 and verifies that temporary ON sites do not survive a completed step even when a motor is bound; permanent sites remain ON. This acceptance check has no statistical null/alternative hypothesis.

## Legends

- Gray: per-track fluorescence; red opacity: temporary ON sites per bin divided by total sites; gold: permanent ON sites; blue: bound motors with persistent per-ID fluorescence. Gold and blue occupy opposite display offsets; geometry, scale, and exposure match the control.

## Interpretation

- This condition examines removing motor shielding while retaining the same concentration-to-erasure conversion. Scientific comparisons and uncertainty estimation are deferred.

## Notes

- The cutter never turns permanent sites OFF. It does not erase the motor object itself.

## References

- `../../protein_simulation/engine.py`: erasure eligibility branch; shared setup above.

# motor

## Method

- Set `run_length_mode='fixed_steps'` and retain protection, upstream clusters, exclusion, and writing.
- Count successful forward steps since each motor's latest binding event. Release immediately after step 357, or earlier at a track end. Stalled attempts do not consume steps. Rebinding starts a new step count.
- Do not perform ON-density-dependent stochastic detachment trials in this mode. A motor remains free to bind again after release.

## Variables

- The same 14 scientific inputs are supplied, but the nominal `motor_run_length_um=20` is intentionally unused in this mode.
- Additional condition control: `fixed_run_steps=357`, equivalent to 4.998 µm at the shared 0.014 µm site spacing. For future unequal spacings, this rule fixes steps, so the physical distance is track-specific.
- All other scientific inputs, geometry, timing, and object fluorescence match the control.
- Cache: `cache/motor.npz`; outputs: `plots/motor.gif` and `plots/motor_final.png`.

## Statistics

- No inferential test. Completed run lengths must not exceed the fixed step limit converted to distance; the check passes. Separate unit tests verify exact cutoff release without track-end interference and earlier release at boundaries.
- No null/alternative hypothesis or statistical decision threshold applies. The 357-step limit is a mechanistic threshold, not a significance threshold.

## Legends

- Gray track fluorescence, red temporary-ON density, gold permanent-site diamonds, and blue motor bars use the same scale/exposure as the other conditions. The sidebar explicitly states the cutoff and track-end exception.

## Interpretation

- This is deterministic distance-limited release, not a constant detachment probability with an exponentially distributed run length. The illustrative cutoff differs from the baseline's nominal scale by request; later sweeps are needed to study cutoff effects separately.

## Notes

- Fixed distance does not mean fixed travel time: stepping is stochastic and exclusion can cause stalls. Motors release at the cutoff instead of becoming permanent obstacles.

## References


# permanent

## Method

- Set `permanent_site_placement='random_normal'` and retain baseline protection and ON-dependent detachment.
- For each track with `N` sites, assign position weights proportional to `exp(-0.5 * ((i/(N-1) - 0.5)/0.3)^2)` for indices `i=0,...,N-1`. Sample 15 distinct indices without replacement from those normalized weights.
- This is a discretized normal distribution restricted to the available track sites, followed by sampling without replacement. All selected sites begin permanently ON; every other site remains a temporary site initially OFF.
- Use a separate site-placement RNG so sampling positions does not advance the dynamics stream. The stored permanent mask is fixed for the entire run.

## Variables

- All 14 scientific variables, track geometry, total/permanent/temporary counts, timing, and object fluorescence match the control.
- Only rule change: `permanent_site_placement='random_normal'`; position mean 0.5 and SD 0.3 in normalized track coordinates.
- Cache: `cache/permanent.npz`; outputs: `plots/permanent.gif` and `plots/permanent_final.png`.

## Statistics

- No inferential test. Exactly 15 unique permanent sites per track are required, and those sites must remain ON at every snapshot; both checks pass. No statistical null/alternative hypothesis or p-value threshold applies.

## Legends

- Gold diamonds show the actual scattered permanent positions on the side opposite the blue motors; close markers can overlap, but they are not connected into a false contiguous permanent segment.
- Gray per-track fluorescence and red temporary-ON density use the shared definitions, fixed exposure, and scale. Motor-specific fluorescence stays fixed across frames and conditions.

## Interpretation

- This condition changes where capture-supporting permanent sites lie, preserving how many there are. The selected distribution favors the center; it should not be interpreted as uniform placement.

## Notes

- Sampling without replacement prevents duplicate selections from reducing the permanent-site count, unlike the professor's optional scattered-seed implementation. Spatial positions are chosen once at initialization, not resampled over time.

## References

- `../../protein_simulation/engine.py`: permanent-site placement branch; shared setup above.
