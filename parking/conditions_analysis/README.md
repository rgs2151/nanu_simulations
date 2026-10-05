# conditions_analysis

## Method

- Read the four single-realization caches owned by `../conditions/`; keep this analysis, its derived caches, and its outputs in this separate unit. No condition simulation cache or existing GIF is overwritten.
- Use the same 81 snapshot times, 0–16,000 s at 200 s intervals, for all six displayed metrics. Permanent sites count as ON in the fractions and connectivity calculations.
- The original animation caches do not identify binding/release events between snapshots. `record_events.py` replays each original seed/initialization once through the shared engine with observation callbacks. It records track ON counts and individual binding/release events at the 0.5 s integration resolution, then requires exact equality of every original result array before accepting the new event cache. This is instrumentation of the existing realization, not an independent replicate.
- Define dark as total ON fraction strictly below 0.05 and lit as total ON fraction strictly above 0.40, following the user-selected professor thresholds. A track exactly at either threshold, or between them, is intermediate and counted as neither lit nor dark.
- Compute the panels as follows:

| Panel | Measurement | Calculation |
| --- | --- | --- |
| A | Motors bound per track | Number of bound motors at the snapshot divided by all 50 tracks, including tracks with no motors. This is the population mean, not 50 separate track curves. |
| B | Fraction of sites ON | Total ON sites divided by total sites across all tracks; permanent and temporary sites are included. This is site-weighted, not the unweighted mean of per-track fractions. |
| C | Lit tracks | Count of tracks with total ON fraction >0.40. |
| D | Dark tracks | Count of tracks with total ON fraction <0.05. Intermediate tracks are neither C nor D. |
| E | Time for a dark track to light up | Cumulative mean duration of completed dark-to-lit passages by each plotted time. A passage starts on entry below 0.05 and ends on first entry above 0.40. Time spent intermediate counts toward the passage; intermediate-to-dark returns do not restart it. A new passage can start after the track has become lit and later becomes dark again. |
| F | Motor dwell time on a track | Cumulative mean binding-to-release duration among motor residence episodes completed by each plotted time, including time stalled by exclusion. Release at a track end also completes an episode. Rebinding, including to the same track, starts a new episode. |
| Historical G (not plotted) | Longest lit path | Maximum physical first-to-last-site span of any contiguous ON-site run within one track at the snapshot. Inspect tracks separately; crossing tracks and neighboring flattened array blocks are not connected. |

- For E and F, ongoing episodes at the end of observation are retained with `completed=0` in the episode table, but excluded from the completed-episode means. Before any episode completes, its mean is undefined (`NaN`), so the curve starts only when data exist. Do not replace these missing values with zero. These conditional descriptive means are not censoring-adjusted estimates of all eventual waiting/residence times.
- Compute G as `(number_of_sites_in_segment - 1) * site_spacing`, consistent with the engine's first-to-last-site track-length definition. An isolated ON site has zero span; an all-OFF track has no positive span. No connection graph or cross-track transport is inferred.
- Render one 2×3 grid containing A–F. G was removed at the user’s request; its historical cached values remain available but are not plotted. Each occupied panel contains one line per condition and no confidence interval. Export the plotted data and underlying duration episodes alongside PNG and vector PDF versions.

## Variables

Inputs (read-only):

- `../conditions/cache/{baseline,cutter,motor,permanent}.npz`: original trajectories, track geometry, site masks, and completed run distances.
- `../conditions/cache/{baseline,cutter,motor,permanent}.json`: exact resolved scientific inputs and condition rules used to produce each trajectory.
- Shared conditions are the original baseline, unprotected cutter, 357-step fixed motor run, and normal-weighted scattered permanent sites. All other source input values and shared object fluorescence are retained; this unit does not define a new parameter set.
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

- `plots/conditions_analysis.png`: high-resolution 2×3 figure.
- `plots/conditions_analysis.pdf`: vector version of the same figure.
- `plots/conditions_analysis.csv`: 324 rows, one per condition and snapshot. Retains the six plotted metrics, the historical unplotted within-track path metric, and intermediate-track and completed-episode counts for auditing denominators. Missing duration means are empty fields.
- `plots/duration_episodes.csv`: condition, episode type, motor ID when applicable, track ID, start/end times, observed duration, and completion flag. For unfinished episodes, the end is the observation horizon and the duration is only time observed so far.
- `plots/manifest.json`: color mapping, metric/source identities, end-of-run episode counts, and exact-replay validation results.

## Statistics

- None; this output is descriptive. Summary operations are means, pooled site fractions, counts, cumulative means of completed durations, and a maximum contiguous segment length. There are no statistical tests, fitted models, smoothing, confidence intervals, or significance claims.
- Null hypothesis and alternative hypothesis: not applicable. The requested plot compares one existing realization per condition rather than performing an inferential experiment.
- Decision rules: strict 5%/40% thresholds classify individual track states; they are mechanistic/descriptive categories, not significance thresholds. Lit + dark can be less than 50 because intermediate tracks are omitted from both counts; lit + dark + intermediate must equal 50.
- Acceptance checks require exact equality of every replayed result array against the original condition cache; all four passed. Fine-step ON counts must reproduce every original snapshot count. Completed residence-episode counts must equal the original completed-run counts.
- Completed-episode denominators vary by condition and time. Long/unfinished dark passages or motor dwell episodes are excluded until completion, so E/F are conditional means with completion-selection effects. They must not be interpreted as unbiased population mean waiting times or used to claim a significant condition difference.
- Final event inventory for this realization:

| Condition | Completed motor dwell | Ongoing motor dwell | Completed dark-to-lit | Ongoing dark-to-lit |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 1,030 | 40 | 31 | 19 |
| Cutter ignores protection | 1,146 | 39 | 35 | 16 |
| Fixed motor run | 1,455 | 38 | 42 | 9 |
| Scattered permanent sites | 1,273 | 40 | 51 | 3 |

A track can contribute more than one completed dark-to-lit passage. An ongoing passage can currently be intermediate rather than dark, so its count need not equal panel D.

## Legends

Condition identity is fixed project-wide in `../../DECISIONS.md` and `../../protein_simulation/style.py`:

| Condition | Color | Hex | Line style in this figure |
| --- | --- | --- | --- |
| Baseline | Black | `#000000` | Solid |
| Cutter ignores protection | Blue | `#2674D9` | Solid |
| Fixed motor run | Green | `#219447` | Solid |
| Scattered permanent sites | Purple | `#8B3FC7` | Solid |

- All four lines are solid and use fixed saturated condition colors; coincident values may overlap. Do not shift or smooth data to separate lines.
- Every panel uses `Time (s)` on X. A shows mean motors/track; B dimensionless total-site ON fraction; C/D track counts; E/F seconds. The historical path metric is no longer displayed.
- Legend is shared above the figure. No overall title or footer commentary is included. Thresholds, averaging, and path definitions are documented here.
- Lines join sampled values without smoothing or uncertainty bands. NaN sections are not drawn.
- All text uses Arial. Standard attached axes show several tick values; bounded fractions/counts retain their natural full range, following the revised `STYLE.md`.
- The colors used here encode conditions. They do not replace the object/site colors in existing simulation GIFs.

## Interpretation

See [follow_up_questions.md](follow_up_questions.md) for the user’s scientific questions, cached-data checks, and interpretation of panels B–F.

- A–D describe contemporaneous binding and activation. E–F summarize durations completed up to the plotted time. The historical G metric is no longer plotted.
- The figure supports qualitative comparison of these specific simulated trajectories. It does not establish statistical significance, stable bistability, or experimentally validated performance.
- The fixed-run condition uses the requested ~5 µm deterministic cutoff while the baseline retains a 20 µm nominal full-ON stochastic run scale. The earlier design limitation remains: this plot does not separate release-rule effects from cutoff-magnitude effects.
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
