# Reference

## Professor's DNA-rail transport notebook

[dna_rail_transport_sim_en__1_.ipynb](dna_rail_transport_sim_en__1_.ipynb) is the original user-supplied notebook, preserved byte-for-byte with its saved figures, animation, text outputs, and narrative. The notebook was read, not executed, during import. Its suggested sweeps and parameter changes are reference content, not instructions to run them.

## Model and purpose

The notebook explores whether a shared, limited pool of transporters can produce rails with different levels of binding-site activation through positive feedback between capture, retention, and writing. It is a stochastic discrete-site model, not an atomistic simulation. The stated 15 motors and 15 polymerases per transporter are descriptive context; individual motors and enzymes are not separately simulated.

- Straight rails have randomly sampled lengths, positions, and polarities and lie fully inside a square chamber. Rail lengths are sampled from a normal distribution with geometric rejection.
- Each rail is a sequence of ON/OFF binding sites. At the defaults every rail begins with 15 permanent ON sites at its upstream end.
- Free transporters make probabilistic encounter attempts. Rails are chosen proportional to their number of sites, then a valid footprint position is chosen uniformly. Binding requires at least one ON site under the footprint and, with exclusion enabled, no overlapping transporter.
- Bound transporters advance one site in the rail's polarity direction on a successful step attempt. A newly covered leading site is switched ON with probability `P_WRITE`.
- After an unblocked step, detachment probability is `SITE_SPACING / (RUN_LENGTH * max(f, ON_FLOOR))`, where `f` is the ON fraction in the updated footprint. Reaching the rail end also causes detachment.
- Nonpermanent ON sites are erased probabilistically. Occupied sites are protected when `PROTECT=True`.
- All rails compete for the same transporter pool. Chamber coordinates are used for placement and display; free-solution diffusion trajectories, rail-junction transfers, and inter-rail spatial collisions are not modeled.

The feedback is built into the transition rules: more ON sites can increase capture opportunities and reduce detachment probability; retained transporters can write and protect more sites.

## Default parameters

| Quantity | Default |
| --- | --- |
| Chamber edge / number of rails | 100 µm / 50 |
| Rail length distribution before geometric rejection | Normal, mean 15 µm, SD 3 µm |
| Site spacing / permanent seed sites | 0.014 µm / 15 per rail |
| Seed configuration | All rails seeded; contiguous cluster at upstream end |
| Transporter count / footprint | 40 / nominally 0.400 µm, rounded to 29 sites |
| Walking speed | 0.010 µm/s |
| Nominal run length at fully ON footprint | 20 µm |
| Encounter attempt rate | 0.2 s⁻¹ per free transporter |
| Write probability / erasure rate | 1.0 / 0.0008 s⁻¹ |
| Footprint protection / exclusion / ON-dependent retention | Enabled |
| ON-density floor | 0.02 |
| Time step / total duration / snapshot interval | 0.5 s / 16,000 s / 200 s |
| Random seed | 0 |

With these defaults, per-step walking, search, and erasure probabilities are approximately 0.3571, 0.1, and 0.0004 respectively. These are linear rate-times-step probabilities, not exact exponential waiting-time probabilities.

## Notebook map

Cell indices below are zero-based, as stored in the notebook JSON.

| Cells | Content |
| --- | --- |
| 0–1 | Model narrative and adjustable parameters |
| 2 | Imports, rail construction, site coordinates, simulation loop |
| 3 | Simulation invocation and run-length summary |
| 4 | Rendering helpers, density bins, seed and transporter geometry |
| 5–6 | Six static snapshots and embedded HTML animation |
| 7 | Total ON sites, per-rail ON fractions, bound transporter counts |
| 8 | Rail-state trajectories, histograms, occupancy coupling, bimodality coefficient, switching counts |
| 9 | Optional 4 × 4 transporter-count/erasure-rate sweep; disabled in the saved notebook |
| 10 | Author's interpretation, historical sweep table, and suggested follow-up settings |

Core simulation outputs are `rails`, `snaps`, the rounded footprint size, and seeded rail IDs. `snaps` contains times, site states, transporter rail/position arrays, completed-run distances, and the permanent-site mask. The notebook has no persistent simulation cache or explicit plot-file export; its existing outputs are embedded in the notebook.

Visual encodings: gray rails; orange permanent seed sites; red ON sites (red opacity is binned ON fraction in density mode); blue bound transporters. The blue bars are shifted perpendicular to rails by 0.7 µm for display only. The time-evolution heatmap uses ON fraction from 0 to 1, with rails sorted by their final ON fraction.

## Saved results and their status

These values are transcribed from existing text outputs, not recomputed:

- 49,333 total sites; 81 snapshots; 29-site transporter footprint.
- 1,030 completed runs, mean distance 5.81 µm and median 5.19 µm.
- Final rail classes: 18 low (`ON fraction < 0.05`), 9 intermediate, and 23 high (`ON fraction > 0.40`).
- 31 low-to-high transitions and zero high-to-low transitions, after ignoring intermediate-state samples in each rail's sampled trajectory.
- Final bimodality coefficient 0.62 and correlation between bound transporter count and ON fraction 0.72.
- Approximate full-rail maintenance occupancy `B* = 1.1`; transporter supply averages 0.8 per rail.

The last narrative cell also describes previous sweeps and a longer run. Those claims are not backed by corresponding executed sweep outputs in this file: cell 9 records that `RUN_SWEEP` is disabled. All code-cell execution counts are null despite saved outputs, so execution provenance and agreement with current source are not independently established.

## Points to resolve before using this as an analysis baseline

1. **Coexistence does not establish bistability.** The saved output describes one seed and one finite run. No replicate uncertainty, formal hypothesis test, or stability analysis is provided. The author's longer-run narrative explicitly describes metastable coexistence and slow ignition. The bimodality coefficient's `5/9` reference is used as a heuristic, not a significance threshold or proof of two stable attractors.
2. **The seed-only label uses a length-dependent proxy.** Cell 8 counts rails with total ON fraction below 2%, rather than directly counting nonpermanent ON sites. The saved per-rail list has 18 rails with exactly 15 ON sites, but only 15 fall below 2%; shorter rails have higher seed fractions. True seed-only classification should use the permanent mask if adopted later.
3. **The `ON_FLOOR` parameter comment reverses the run-length interpretation.** The code caps per-step detachment probability at `p_leave / ON_FLOOR`. At fixed density, away from boundaries, the nominal distance scale is `RUN_LENGTH * max(f, ON_FLOOR)`, giving a minimum of 0.4 µm at defaults, not `RUN_LENGTH / ON_FLOOR`.
4. **Detachment depends on movement.** A blocked transporter does not undergo the post-step detachment trial. There is no separate time-dependent unbinding while stalled. The completed-run summary also excludes transporters still bound at simulation end, and rail ends truncate completed runs.
5. **The maintenance estimate is approximate.** `B* = K_OFF * mean(site count) / ((SPEED / SITE_SPACING) * P_WRITE)` balances nominal writing and erasure. It does not account for permanent seeds, protection, rewriting already-ON sites, exclusion, or spatially variable ON density; it is not a demonstrated stability boundary.
6. **Sweep categories are not exhaustive.** The sweep calls a rail dark only when ON fraction is below 5% AND occupancy is zero. Low-ON rails with a bound transporter are neither dark, intermediate, nor lit, so the three counts need not sum to 50.
7. **Parameter validation is limited.** The simulation asserts only that walking probability is at most 0.6; arbitrary edited rates and geometry can produce invalid probabilities or footprints. Scattered seeds are sampled with replacement and can yield fewer unique permanent sites than requested.
8. **The dynamics use fixed sequential updates.** Transporters are processed in index order, with writing and detachment before enzymatic erasure. Time-step sensitivity and update-order effects have not been assessed here. The 200-second sampling interval also limits observable switching.

The original notebook remains unchanged. Any adopted corrections, scientific comparisons, or reproducible reruns should live in a new compact unit with its own parameters, cache, outputs, and documentation.
