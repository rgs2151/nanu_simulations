# conditions_analysis

## Method

- Read the four single-realization caches owned by `../conditions/`; keep this analysis, its derived caches, and its outputs in this separate unit. No condition simulation cache or existing GIF is overwritten.
- Use the same 81 snapshot times, 0–16,000 s at 200 s intervals, for all seven displayed metrics. Permanent sites count as ON in the fractions and connectivity calculations.
- The original animation caches do not identify binding/release events between snapshots. `record_events.py` replays each original seed/initialization once through the shared engine with observation callbacks. It records track ON counts and individual binding/release events at the 0.5 s integration resolution, then requires exact equality of every original result array before accepting the new event cache. This is instrumentation of the existing realization, not an independent replicate.
- Define dark as total ON fraction strictly below 0.05 and lit as total ON fraction strictly above 0.40, following the user-selected professor thresholds. A track exactly at either threshold, or between them, is intermediate and counted as neither lit nor dark.
- Compute the panels as follows:

| Panel | Measurement | Calculation |
| --- | --- | --- |
| A | Motors bound per track | Bound motor count divided by all 50 tracks, including empty tracks. |
| B | Motor dwell time | Cumulative mean completed binding-to-release duration, including stalls. |
| C | Fraction of sites ON | Total ON sites divided by all sites; includes permanent sites. |
| D | Dark-to-lit time | Cumulative mean completed passage from <5% to >40% ON, including intermediate time. |
| E | Lit track count | Tracks with ON fraction >40%. |
| F | Intermediate track count | Tracks with 5% ≤ ON fraction ≤40%. |
| G | Dark track count | Tracks with ON fraction <5%. |

The historical path metric is no longer plotted. The bottom-right cell is empty.

- For the duration panels B and D, ongoing episodes at the end of observation are retained with `completed=0` in the episode table, but excluded from the completed-episode means. Before any episode completes, its mean is undefined (`NaN`), so the curve starts only when data exist. Do not replace these missing values with zero. These conditional descriptive means are not censoring-adjusted estimates of all eventual waiting/residence times.
- The historical, now unplotted within-track segment metric is computed as `(number_of_sites_in_segment - 1) * site_spacing`, consistent with the engine's first-to-last-site track-length definition. An isolated ON site has zero span; an all-OFF track has no positive span. No connection graph or cross-track transport is inferred.
- Render a compact 2×4 grid with A–D on top and E–G below. The last cell is empty. Use descriptive Y-axis labels without redundant subplot titles, aligned panel letters above each axis, a bottom legend, and per-panel data-range limits with 6% padding. Each occupied panel contains one line per condition and no confidence interval. Export the plotted data and underlying duration episodes alongside PNG and vector PDF versions.

## Variables

Inputs (read-only):

- `../conditions/cache/{baseline,cutter,motor,permanent}.npz`: original trajectories, track geometry, site masks, and completed run distances.
- `../conditions/cache/{baseline,cutter,motor,permanent}.json`: exact resolved scientific inputs and condition rules used to produce each trajectory.
- Shared conditions are the original baseline, unprotected cutter, baseline-like motor run capped at 357 steps, and normal-weighted scattered permanent sites. All other source input values and shared object fluorescence are retained; this unit does not define a new parameter set.
- Track IDs index the matching count/offset arrays; motor IDs index snapshot columns and event records. Arrays are aligned by the original IDs and simulation times, not by sorting tracks by their outcome.
- Source durations: 16,000 s, integration step 0.5 s, plot sampling 200 s. Four conditions, one original seed-0 realization per condition, no additional seeds or Monte Carlo replicates.
- Dark threshold: `<0.05`; lit threshold: `>0.40`; both threshold boundaries belong to the intermediate category.
- X axis: elapsed simulation time in seconds. It is not a step index, episode number, or parameter sweep value.
- Motor/track counts are counts; the site fraction is dimensionless; waiting/dwell durations are seconds; contiguous path length is µm.

Additional caches owned by this unit:

- `cache/{name}_events.npz`: `times` (32,001 integration boundaries), `track_on` (time × 50 integer counts), and `motor_episodes` (motor ID, track ID, binding time, release/end time, completion flag).
- `cache/{name}_events.json`: source-cache/manifest hashes, observation/engine source hashes, and NumPy version.
- `cache/replay_validation.json`: exact-trajectory checks and completed/ongoing residence counts.
- `cache/summary.npz` and `cache/summary.json`: all plot-ready metrics, dark-to-lit episodes, and derivation identity. Changing thresholds or metric code requires an explicit metric refresh, not a dynamics rerun.

Tracked outputs:

- `plots/conditions_analysis.png`: high-resolution 2×4 figure.
- `plots/conditions_analysis.pdf`: vector version of the same figure.
- `plots/conditions_analysis.csv`: 324 rows, one per condition and snapshot. Retains the seven plotted metrics, the historical unplotted within-track path metric, and intermediate-track and completed-episode counts for auditing denominators. Missing duration means are empty fields.
- `plots/duration_episodes.csv`: condition, episode type, motor ID when applicable, track ID, start/end times, observed duration, and completion flag. For unfinished episodes, the end is the observation horizon and the duration is only time observed so far.
- `plots/manifest.json`: color mapping, metric/source identities, end-of-run episode counts, and exact-replay validation results.

## Statistics

- None; this output is descriptive. Summary operations are means, pooled site fractions, counts, cumulative means of completed durations, and a maximum contiguous segment length. There are no statistical tests, fitted models, smoothing, confidence intervals, or significance claims.
- Null hypothesis and alternative hypothesis: not applicable. The requested plot compares one existing realization per condition rather than performing an inferential experiment.
- Decision rules: strict 5%/40% thresholds classify individual track states; they are mechanistic/descriptive categories, not significance thresholds. Lit + dark can be less than 50 because intermediate tracks are omitted from both counts; lit + dark + intermediate must equal 50.
- Acceptance checks require exact equality of every replayed result array against the original condition cache; all four passed. Fine-step ON counts must reproduce every original snapshot count. Completed residence-episode counts must equal the original completed-run counts.
- Completed-episode denominators vary by condition and time. Long/unfinished dark passages or motor dwell episodes are excluded until completion, so B/D are conditional means with completion-selection effects. They must not be interpreted as unbiased population mean waiting times or used to claim a significant condition difference.
- Final event inventory for this realization:

| Condition | Completed motor dwell | Ongoing motor dwell | Completed dark-to-lit | Ongoing dark-to-lit |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 1,030 | 40 | 31 | 19 |
| Cutter ignores protection | 1,146 | 39 | 35 | 16 |
| Capped motor run | 1,634 | 39 | 41 | 9 |
| Scattered permanent sites | 1,273 | 40 | 51 | 3 |

A track can contribute more than one completed dark-to-lit passage. An ongoing passage can currently be intermediate rather than dark, so its count need not equal panel G (dark tracks).

## Legends

Condition identity is fixed project-wide in `../../DECISIONS.md` and `../../protein_simulation/style.py`:

| Condition | Color | Hex | Line style in this figure |
| --- | --- | --- | --- |
| Baseline | Black | `#000000` | Solid |
| Cutter ignores protection | Blue | `#2674D9` | Solid |
| Capped motor run | Green | `#219447` | Solid |
| Scattered permanent sites | Purple | `#8B3FC7` | Solid |

- All four lines are solid and use fixed saturated condition colors; coincident values may overlap. Do not shift or smooth data to separate lines.
- Every panel uses `Time (s)` on X. A shows mean motors/track; B dwell duration in seconds; C total-site ON fraction; D activation-passage duration in seconds; E/F/G lit, intermediate, and dark track counts. The historical path metric is no longer displayed.
- Legend is shared below the figure. No overall title or footer commentary is included. Thresholds, averaging, and path definitions are documented here.
- Lines join sampled values without smoothing or uncertainty bands. NaN sections are not drawn.
- All text uses Arial. Standard attached axes show several tick values; Y limits follow the finite data range with modest padding and a nonnegative lower bound. No initial samples are discarded to zoom the curves.
- The colors used here encode conditions. They do not replace the object/site colors in existing simulation GIFs.

## Interpretation

See [follow_up_questions.md](follow_up_questions.md) for the user’s scientific questions, cached-data checks, and interpretation of the metrics (with historical panel labels explicitly identified).

- A/C/E/F/G describe contemporaneous binding and activation. B/D summarize durations completed up to the plotted time. The historical path metric is no longer plotted.
- The figure supports qualitative comparison of these specific simulated trajectories. It does not establish statistical significance, stable bistability, or experimentally validated performance.
- The corrected capped-run condition retains baseline stochastic detachment (including the 20 µm full-ON scale) and adds only a 357-step maximum. The previous guaranteed-distance implementation was incorrect and its numerical results are superseded.
- Track connectivity is still absent from the model. The historical G metric was a within-track substitute, not a connected multi-track route; the user has now removed it from the figure.

## Notes

From the repository root:

```bash
conda activate protein-simulation
# First use only: record missing exact-step events from the original realizations.
python parking/conditions_analysis/record_events.py --workers 64
# Derive metrics and draw; this command never simulates.
python parking/conditions_analysis/conditions_analysis.py
# After a plotting-only edit: reuse metrics and redraw.
python parking/conditions_analysis/conditions_analysis.py
# After changing metric definitions: refresh derived metrics only.
python parking/conditions_analysis/conditions_analysis.py --recompute
```

The event recorder skips valid caches. It requires `--recompute` for an explicitly requested event-cache refresh after source changes, and checks the replay against the original trajectory before accepting it. Analysis itself never automatically launches simulations. Re-rendering replaces only this unit's plot/table iteration.

CPU handling: the machine exposes 64 available CPUs. The event recorder accepts a 64-worker limit and starts one worker per independent missing condition (four for this task). It does not spawn 60 idle workers or create extra replicates to fill the machine. The within-run transporter update order remains sequential to preserve the model. BLAS threads were capped at one per worker during the original four-process recording run.

No manuscript caption is drafted yet; future caption text belongs in this unit's `caption.md`. Unit documentation follows the repo's `rudra-iterate-unit-readme` standard.

## References

- `../conditions/README.md`: shared scientific controls, condition rules, caches, and known comparison limits.
- `../../ref/dna_rail_transport_sim_en__1_.ipynb`, analysis cell 8: professor's strict low/high thresholds.
- `../../protein_simulation/engine.py`: shared simulation with optional event/state observation hooks.
- `../../protein_simulation/style.py` and `../../DECISIONS.md`: stable condition colors.
