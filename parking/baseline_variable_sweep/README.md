# motor_sweep

## Method

Run the shared baseline transport engine once for each number of motors value, keeping every other scientific control, track geometry, initial state, and random seed fixed. All runs retain clustered upstream permanent sites, motor protection against cutting, and baseline ON-dependent stochastic release without a run cap. Summarize the same seven time-dependent measurements as conditions analysis, ordered A–G in a two-row, four-column figure; the last panel is empty. Write a PNG preview, vector PDF, and CSV of the plotted values.

Motor visits are measured from binding to release. Dark-to-lit passages begin when a track first becomes dark and finish at its first subsequent lit state, including time spent intermediate. Returning to dark before reaching lit does not restart the timer. Initial dark tracks begin at time zero. Duration curves show the cumulative mean of completed episodes at each displayed time, with no value before the first completion. Unfinished episodes are retained as censored records but excluded from those means.

## Variables

- Resolved inputs: `config.json`, copied from `../baseline_simulation/baseline.json` with the shared motor/track brightness overrides from `../conditions/config.json`. The sweep does not read a changing sibling configuration during execution.
- Swept variable: number of motors. Every integer from 1 through 100; baseline = 40 motors. Cutter concentration stays at 1 relative unit.
- Shared settings: 50 tracks, seed 0, duration 16,000 s, integration step 0.5 s, plotted snapshots every 200 s. The full 14-variable configuration, layout and model rules are in `config.json` and `plots/manifest.json`.
- Cutter units are relative concentration, not volume fraction or an experimentally calibrated concentration. One relative unit maps to an erasure rate of 0.0008 per second; at the 0.5 s step, per-site erasure probability is 0.0004 times concentration before protection/permanence rules.
- Track ON fraction includes permanent and temporary sites. Dark: fraction strictly below 0.05; lit: strictly above 0.40; intermediate: 0.05 through 0.40 inclusive. State crossings are measured every integration step, not only at plotted snapshots.
- Outputs: `plots/motor_sweep.png`, `plots/motor_sweep.pdf`, `plots/motor_sweep.csv`. CSV rows identify sweep value and time; completed-episode counts accompany duration means. `plots/manifest.json` records configuration, sweep-to-cache mapping, source hashes and panel/color definitions.
- Caches: `cache/mNNN_cVALUE.npz` contains full sampled engine states, seven summaries, completed-episode counts, motor visit records and dark-to-lit records. Motor episode columns: motor ID, track ID, binding time, release/end time, completed flag. Passage columns: track ID, dark-entry time, lit-entry/end time, completed flag. `cache/manifest.json` includes the exact source text used for computation.

## Statistics

No inferential tests or fitted statistical models; this output is descriptive. Null and alternative hypotheses and significance thresholds are not applicable. There is one realization per parameter value, no confidence interval, smoothing or averaging across seeds.

Bound motors per track is total currently bound motors divided by all 50 tracks. Overall ON fraction is total ON sites divided by total sites, weighting tracks by site count. Lit, intermediate and dark counts partition all tracks using the stated thresholds. Dwell and dark-to-lit curves are arithmetic means over episodes completed by the plotted time; their sample sizes appear in the CSV. These summaries match the condition comparison and expose time evolution rather than replacing it with a single average over time. Completed-only duration means exclude censored episodes and can favor shorter episodes early in a run; they are not survival estimates or mean ages of currently bound motors.

## Legends

- X axis: time in seconds on every panel.
- A: bound motors per track. B: completed motor dwell time in seconds. C: fraction of all sites ON (unitless). D: completed dark-to-lit passage time in seconds. E: lit track count. F: intermediate track count. G: dark track count.
- One shared horizontal colorbar encodes number of motors across all seven panels. The scale runs from dark purple at the low end through magenta to orange at the high end, using `plasma` truncated to its first 80% to avoid pale yellow against white.
- All curves are solid; each sweep contains exactly 100 parameter values. The baseline value is highlighted by a thicker black line, overlaid on its colored trace. Curves are drawn in ascending parameter order; black is drawn last. No model-condition colors are reassigned: every curve uses baseline dynamics.

## Interpretation

Compare time evolution across the color scale to see how changing only number of motors influences recruitment, site activation, track classifications, and completed durations. A trend is exploratory behavior of this model and realization, not evidence of statistical significance. The same-seed design holds the starting random state fixed, but changing motor count or event rates changes subsequent random-number consumption; trajectories are not matched event by event.

## Notes

- Run both sweeps with `conda run -n protein-simulation python parking/baseline_variable_sweep/baseline_variable_sweep.py`. Default parallelism uses up to 60 workers, leaving four of this machine's 64 cores available. All workers inherit one loaded core engine through fork.
- For plotting changes, add `--render-only`; it reads caches and does not simulate. Existing caches are reused. Change no result files outside this unit.
- Two 100-value sweeps share one identical baseline simulation, giving 199 distinct cached runs. Brightness is unchanged within each sweep and does not enter these state-based metrics; no optical readout is used here.
- Routine summaries/plotting edits do not add or run tests. No confidence intervals were requested.

## References

- `../conditions_analysis/`: corresponding seven-panel definitions, thresholds and completed-episode interpretation.
- `../baseline_simulation/baseline.json`: baseline inputs and professor-derived track layout/RNG continuation.
- `../../protein_simulation/engine.py` and `../../protein_simulation/parameters.py`: single shared engine and scientific controls.
- `../../STYLE.md` and `../../DECISIONS.md`: Arial, solid lines, baseline identity and relative cutter calibration.

# cutter_sweep

## Method

Run the shared baseline transport engine once for each cutter concentration value, keeping every other scientific control, track geometry, initial state, and random seed fixed. All runs retain clustered upstream permanent sites, motor protection against cutting, and baseline ON-dependent stochastic release without a run cap. Summarize the same seven time-dependent measurements as conditions analysis, ordered A–G in a two-row, four-column figure; the last panel is empty. Write a PNG preview, vector PDF, and CSV of the plotted values.

Motor visits are measured from binding to release. Dark-to-lit passages begin when a track first becomes dark and finish at its first subsequent lit state, including time spent intermediate. Returning to dark before reaching lit does not restart the timer. Initial dark tracks begin at time zero. Duration curves show the cumulative mean of completed episodes at each displayed time, with no value before the first completion. Unfinished episodes are retained as censored records but excluded from those means.

## Variables

- Resolved inputs: `config.json`, copied from `../baseline_simulation/baseline.json` with the shared motor/track brightness overrides from `../conditions/config.json`. The sweep does not read a changing sibling configuration during execution.
- Swept variable: cutter concentration. 100 values spanning 0.01–3 relative units, initially evenly spaced; the nearest value to 1 is replaced by exactly 1 to include the baseline. Motor count stays at 40.
- Shared settings: 50 tracks, seed 0, duration 16,000 s, integration step 0.5 s, plotted snapshots every 200 s. The full 14-variable configuration, layout and model rules are in `config.json` and `plots/manifest.json`.
- Cutter units are relative concentration, not volume fraction or an experimentally calibrated concentration. One relative unit maps to an erasure rate of 0.0008 per second; at the 0.5 s step, per-site erasure probability is 0.0004 times concentration before protection/permanence rules.
- Track ON fraction includes permanent and temporary sites. Dark: fraction strictly below 0.05; lit: strictly above 0.40; intermediate: 0.05 through 0.40 inclusive. State crossings are measured every integration step, not only at plotted snapshots.
- Outputs: `plots/cutter_sweep.png`, `plots/cutter_sweep.pdf`, `plots/cutter_sweep.csv`. CSV rows identify sweep value and time; completed-episode counts accompany duration means. `plots/manifest.json` records configuration, sweep-to-cache mapping, source hashes and panel/color definitions.
- Caches: `cache/mNNN_cVALUE.npz` contains full sampled engine states, seven summaries, completed-episode counts, motor visit records and dark-to-lit records. Motor episode columns: motor ID, track ID, binding time, release/end time, completed flag. Passage columns: track ID, dark-entry time, lit-entry/end time, completed flag. `cache/manifest.json` includes the exact source text used for computation.

## Statistics

No inferential tests or fitted statistical models; this output is descriptive. Null and alternative hypotheses and significance thresholds are not applicable. There is one realization per parameter value, no confidence interval, smoothing or averaging across seeds.

Bound motors per track is total currently bound motors divided by all 50 tracks. Overall ON fraction is total ON sites divided by total sites, weighting tracks by site count. Lit, intermediate and dark counts partition all tracks using the stated thresholds. Dwell and dark-to-lit curves are arithmetic means over episodes completed by the plotted time; their sample sizes appear in the CSV. These summaries match the condition comparison and expose time evolution rather than replacing it with a single average over time. Completed-only duration means exclude censored episodes and can favor shorter episodes early in a run; they are not survival estimates or mean ages of currently bound motors.

## Legends

- X axis: time in seconds on every panel.
- A: bound motors per track. B: completed motor dwell time in seconds. C: fraction of all sites ON (unitless). D: completed dark-to-lit passage time in seconds. E: lit track count. F: intermediate track count. G: dark track count.
- One shared horizontal colorbar encodes cutter concentration across all seven panels. The scale runs from dark purple at the low end through magenta to orange at the high end, using `plasma` truncated to its first 80% to avoid pale yellow against white.
- All curves are solid; each sweep contains exactly 100 parameter values. The baseline value is highlighted by a thicker black line, overlaid on its colored trace. Curves are drawn in ascending parameter order; black is drawn last. No model-condition colors are reassigned: every curve uses baseline dynamics.

## Interpretation

Compare time evolution across the color scale to see how changing only cutter concentration influences recruitment, site activation, track classifications, and completed durations. A trend is exploratory behavior of this model and realization, not evidence of statistical significance. The same-seed design holds the starting random state fixed, but changing motor count or event rates changes subsequent random-number consumption; trajectories are not matched event by event.

## Notes

- Run both sweeps with `conda run -n protein-simulation python parking/baseline_variable_sweep/baseline_variable_sweep.py`. Default parallelism uses up to 60 workers, leaving four of this machine's 64 cores available. All workers inherit one loaded core engine through fork.
- For plotting changes, add `--render-only`; it reads caches and does not simulate. Existing caches are reused. Change no result files outside this unit.
- Two 100-value sweeps share one identical baseline simulation, giving 199 distinct cached runs. Brightness is unchanged within each sweep and does not enter these state-based metrics; no optical readout is used here.
- Routine summaries/plotting edits do not add or run tests. No confidence intervals were requested.

## References

- `../conditions_analysis/`: corresponding seven-panel definitions, thresholds and completed-episode interpretation.
- `../baseline_simulation/baseline.json`: baseline inputs and professor-derived track layout/RNG continuation.
- `../../protein_simulation/engine.py` and `../../protein_simulation/parameters.py`: single shared engine and scientific controls.
- `../../STYLE.md` and `../../DECISIONS.md`: Arial, solid lines, baseline identity and relative cutter calibration.
