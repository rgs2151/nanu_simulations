# Follow-up questions

This is the running record of the user's scientific questions about the conditions analysis. The original answers used the code and cached single realizations available at that time, with no new simulations or tests. That original follow-up removed the path panel and used a 2×3 layout. The correction below supersedes the original motor-condition interpretation and records the subsequent simulation refresh and 2×4 layout.


## Correction: the requested motor condition is an upper cap, not a guaranteed run

The user clarified that early release must remain exactly as in baseline. My previous implementation removed baseline stochastic release and therefore implemented the wrong scientific condition. The earlier explanation checked the internal consistency of that wrong condition; it did not establish fidelity to the user's intended model. The historical answers and numbers below describe that superseded implementation (tracked outputs at commit `107e96f`) and must not be treated as current corrected results.

The corrected rule performs baseline's ON-density-dependent release trial after every successful step, and additionally forces release on reaching 357 steps (4.998 µm). Track-end release, motor protection, upstream permanent sites, and every shared scientific variable remain unchanged. The RNG release draw is retained even on a capped step. The fixed-distance field is now a maximum only.

Only the motor condition was resimulated; its fine-step events were recorded in the same pass. The other three conditions were reused unchanged. Corrected cached results: 1,634 completed visits, 787 shorter than 4.998 µm, maximum 4.998 µm, completed mean dwell 369.72 s, final ON fraction 37.84%, and final track counts 26 lit / 16 intermediate / 8 dark. The first plotted dwell value is now 73.5 s at 200 s, identical to baseline's first completed-visit value. The initially high green dwell onset in the old figure is no longer present.

The capped condition still has a higher global ON fraction in this single realization. That does not restore the old guarantee-based explanation: it is now a different, corrected result under baseline stochastic release plus a cap. Earlier mechanisms invoking removal of low-density stochastic release are inapplicable. Redistribution after capped release and differences in net productive writing remain possible explanations, not established causes; no new mechanistic sweep was run.

The new figure order is A motors/track, B dwell time, C ON fraction, D dark-to-lit time; E lit count, F intermediate count, G dark count. The old question numbers and plot letters below refer to the earlier figure. The old path panel is not restored.

## 1. Why does fixed motor run produce more ON sites than baseline? Was scattered permanent-site placement accidentally included?

**Question.** Baseline motors remain bound longer, so why is their ON fraction lower than fixed-run motors? Is the fixed-run condition contaminated by another condition, an implementation error, or a counterintuitive scientific effect?

**Checked facts.** Comparing the actual source cache manifests and arrays, not only the intended configuration:

- `motor.json` and `baseline.json` have identical `shared_inputs`, including all scientific variables, geometry, numerical settings, and initial RNG state.
- The only differing model-rule field is `run_length_mode`: `on_dependent` versus `fixed_steps`.
- The permanent-site masks are exactly identical across all tracks. The fixed-run condition uses the same 15 upstream permanent sites per track; it does not use scattered sites. Its motor-protection rule remains enabled.
- Only the `permanent` condition changes `permanent_site_placement` to `random_normal`.

| Cached measurement | Baseline | Fixed run | Scattered permanent sites |
| --- | ---: | ---: | ---: |
| Final fraction of all sites ON | 32.00% | 36.22% | 37.60% |
| Mean completed motor dwell | 583.03 s | 418.67 s | 482.49 s |
| Completed motor visits | 1,030 | 1,455 | 1,273 |
| Mean completed run distance | 5.810 µm | 4.183 µm | 4.809 µm |
| Time-averaged bound motors over 0–16,000 s | 38.67 | 38.59 | 39.40 |
| Mean number of tracks carrying motors at sampled times 8,000–16,000 s | 22.17 | 24.80 | 27.15 |

The time-averaged bound-motor count comes from the sum of all observed residence durations, including ongoing visits truncated at the observation horizon, divided by 16,000 s. This is different from the completed-visit mean in F. The late track count is a descriptive mean over the 41 stored snapshots in that stated interval, not a confidence estimate.

**Why longer individual visits do not guarantee a higher global ON fraction.**

1. Baseline is not guaranteed to travel farther on every visit. Its per-successful-step release probability is `site_spacing / (20 µm * max(f, 0.02))`, where `f` is current total footprint ON density. It can release early, especially at low ON density. At constant `f=0.1`, the nominal distance scale would be about 2 µm, not 20 µm; actual `f` changes during motion. The fixed rule instead prevents this stochastic early release and permits 357 steps (4.998 µm), unless the track ends first. It therefore changes the whole distribution, not just truncates the baseline's longest runs. In the recorded baseline, 501 of 1,030 completed visits traveled less than 4.998 µm, including any track-end-truncated visits.
2. There are still only 40 motors in both conditions. A longer visit is not extra motors or automatically extra aggregate motor-time. Both populations spend almost all the experiment bound: their average bound counts are 38.67 and 38.59. Shorter fixed-run visits are followed by more new visits: 1,455 versus 1,030 completed visits.
3. Switching an already-ON leading site ON again does not increase the number of ON sites. Global activation is governed by new OFF-to-ON writing minus ON-to-OFF erasure, not by residence duration alone. Stalls also contribute dwell time without advancing or writing.
4. Releasing and rebinding can redistribute motors. These caches do show broader simultaneous track coverage in the fixed-run condition: about 24.80 motor-carrying tracks versus 22.17 over the late sampled interval. Baseline's ON-dependent retention can favor already-active tracks; removing that dependence can reduce this concentration of motors. Broader coverage and protection are consistent with more global ON sites despite shorter individual visits.

**Conclusion and remaining uncertainty.** There is no evidence of the proposed condition mix-up. The observed ordering is compatible with the implemented model and is not logically contradicted by F. Redistribution, removal of low-density early release, and differences in productive versus redundant writing are plausible mechanisms. The caches establish the occupancy/turnover differences above, but do not separately tally every OFF-to-ON write, rewrite, cleavage, or stall. Their relative contributions are therefore not proven by these plots. Do not call this an established scientific finding from one seed.

A further design limitation is explicit: the fixed condition uses a ~5 µm deterministic cutoff, while the baseline uses a 20 µm full-ON stochastic scale. This comparison does not isolate release-distribution shape independently of the selected numerical distance scale. A future requested investigation could tally productive writes, erasures, and per-track visits, or compare matched distance scales; none was run here.

## 2. Why are lit-track and dark-track counts not reciprocal? What are the missing tracks?

**Question.** Why do C and D not sum to all tracks? What does lit/dark mean?

**Definition currently used.** The user selected the professor's low/high thresholds. For each track, fraction ON includes permanent and temporary sites:

- Dark: fraction ON <5%.
- Intermediate: 5% ≤ fraction ON ≤40%.
- Lit: fraction ON >40%.

Thus “lit” currently means highly activated and “dark” means weakly activated, not literally any light versus none. Every track has permanently ON sites even at the initial time; “dark” is not zero ON sites. These are biochemical ON-state categories, not thresholds of the sampled object fluorescence.

| Final category at 16,000 s | Baseline | Cutter | Fixed run | Scattered permanent |
| --- | ---: | ---: | ---: | ---: |
| Lit | 23 | 20 | 23 | 18 |
| Intermediate | 9 | 15 | 20 | 31 |
| Dark | 18 | 15 | 7 | 1 |
| Total | 50 | 50 | 50 | 50 |

C + D = 50 − intermediate, not 50. For example, baseline is 23 lit + 18 dark + 9 intermediate. The intermediate counts are already exported in `plots/conditions_analysis.csv`, but the plot does not display that third category. That omission and the shorthand labels made the figure harder to interpret; no tracks are missing from the simulation.

C and D would be reciprocal only under one binary threshold, with dark defined as the complement of lit. Changing to that definition would also change E; no such metric change has been made here.

The scattered case also illustrates why C need not rank conditions like B: many moderately ON tracks can yield a high pooled ON fraction while relatively few exceed 40%. Track lengths vary, so B additionally weights longer tracks more than C's one-track-one-count rule.

## 3. What does E measure?

**Question.** What is “time for a dark track to light up” under these definitions?

For each track, start a passage when it enters the <5% state. End that passage the first time it subsequently enters the >40% state. Include time in intermediate states; returning from intermediate to dark before reaching >40% does not restart the clock. A later completed lit-to-dark transition can start a new passage.

At horizontal-axis time `t`, E is the average duration of only the passages that have finished by `t`. It is not the fraction recruited, not a prediction of the remaining wait, and not the current age of every dark track.

Example: if one initially dark track crosses 40% at 1,000 s, E is 1,000 s after that event. If another crosses at 5,000 s, E becomes `(1,000 + 5,000) / 2 = 3,000 s`. E can rise while the number of dark tracks falls, because later completions add longer waits to the average.

At 16,000 s the baseline mean is 4,032.42 s over 31 completed passages. Nineteen passages are unfinished and excluded from that mean. An unfinished passage can currently be intermediate, so nineteen unfinished passages does not imply nineteen currently dark tracks. Completed-only averaging favors earlier/shorter completions; E is a conditional descriptive summary, not an unbiased mean eventual activation time for all tracks.

**Status.** Calculation is consistent with its documented definition, but the short axis label alone does not communicate that definition well. A different definition can be chosen later; it has not been silently changed in this follow-up.

## 4. Why is baseline highest in F but lower in B? Why does the green curve appear to start near 500 s?

**Question.** Does longer motor dwell imply more writing, and why does fixed-run dwell seem nonzero at the beginning?

F averages **completed binding-to-release visit durations** up to each plotted time. It does not show how long a newly recruited motor has been bound so far. Initial visits are not assigned zero duration while still ongoing.

The fixed-run cache contains:

| Plot time | Fixed-run completed-dwell mean |
| --- | --- |
| 0 s | Undefined; no completed visits |
| 200 s | Undefined; no completed visits |
| 400 s | Undefined; no completed visits |
| 600 s | 505.958 s |
| 800 s | 500.953 s |

The first fixed-run release occurred at simulation time 511.5 s: that motor bound at 28.5 s and remained for 483 s. The figure is sampled every 200 s, so the first plotted green point is at 600 s. On a 0–16,000 s axis that point is close to the left edge, but it is not at time zero.

A nominal unblocked travel time of `4.998 µm / 0.010 µm/s = 499.8 s` explains the scale of those first completed visits. Stepping is stochastic and exclusion can stall motors, so this is not a deterministic time limit. Later, motors can bind nearer a track end and release before completing 357 steps; this contributes to the final completed-dwell mean of 418.67 s. Track-end-truncated fixed runs are present: 481 of 1,455 completed fixed-run visits are shorter than 4.998 µm.

Baseline permits stochastic early release, so its first completed visit is much shorter: binding at 123.5 s, release at 197 s, duration 73.5 s. F first displays that value at 200 s, then incorporates longer completed visits as time passes. Different early shapes are expected from these different release rules plus completed-episode selection. Recruitment time is present in both simulations; F simply is not a recruitment plot.

The B/F contrast is addressed in question 1: longer average visits are not more total population-bound time, and elapsed bound time is not a count of newly activated sites. The existing evidence does not indicate that the fixed-run simulation is starting motors with pre-existing dwell time.

## 5. Remove G

**Request.** Drop the longest-path panel and use two rows by three columns.

**Action.** Removed G from the renderer and redrew A–F from the existing summary cache. The old within-track segment values are retained as historical cached/table data but are no longer shown. Other metric definitions and all simulation outputs remain unchanged.

## Sources and scope

- `../conditions/config.json` and `../conditions/cache/{name}.json`: requested and realized condition settings.
- `../conditions/cache/{name}.npz`: actual permanent-site masks, motor positions, and run distances.
- `cache/{name}_events.npz`: fine-step ON counts and complete/unfinished residence episodes.
- `cache/summary.npz` and `plots/conditions_analysis.csv`: plotted values, including intermediate-track and completed-episode counts.
- `../../protein_simulation/engine.py`: stepping, writing, protection, and release rules.
- `metrics.py`: thresholds and completed-episode aggregation.

Verified comparisons are distinguished above from proposed mechanisms. No confidence intervals, inferential tests, new seeds, or new simulations were introduced.
