"""Shared transport engine with explicit, independently selectable model rules."""
from dataclasses import dataclass

import numpy as np

from .parameters import ModelRules, RunSettings, Variables, per_track


@dataclass
class Result:
    starts: np.ndarray
    directions: np.ndarray
    lengths: np.ndarray
    site_counts: np.ndarray
    offsets: np.ndarray
    spacing: np.ndarray
    body_sites: np.ndarray
    permanent: np.ndarray
    times: np.ndarray
    on: np.ndarray
    motor_track: np.ndarray
    motor_position: np.ndarray
    run_lengths: np.ndarray


def binding_probability(n_temporary, n_permanent, p_temporary, p_permanent):
    """Independent opportunities at ON sites within an encountered footprint."""
    return 1.0 - (1.0 - p_temporary) ** n_temporary * (1.0 - p_permanent) ** n_permanent


def simulate(v: Variables, settings: RunSettings = RunSettings(), layout=None,
             rules: ModelRules = ModelRules(), event_callback=None, state_callback=None) -> Result:
    """Simulate using a supplied layout/RNG continuation, or generate a new layout.

    Track length is the distance between the first and last binding sites.
    A supplied layout contains starts, directions, and the RNG state immediately
    after track generation. It is used for exact notebook-baseline reproduction.
    Optional observers record events and completed-step site states without RNG draws.
    event_callback(kind, time_s, motor_id, track_id) receives bind/release events.
    state_callback(time_s, on) receives a read-only view of the current site state.
    """
    if not isinstance(rules.protect_occupied_sites, bool):
        raise ValueError("protect_occupied_sites must be a boolean")
    if rules.run_length_mode not in ("on_dependent", "capped_steps"):
        raise ValueError("Unknown run-length mode")
    if rules.permanent_site_placement not in ("upstream", "random_normal"):
        raise ValueError("Unknown permanent-site placement")
    if not isinstance(rules.fixed_run_steps, int) or rules.fixed_run_steps < 1:
        raise ValueError("fixed_run_steps must be a positive integer")
    if not np.isfinite(rules.permanent_position_sd_fraction) or rules.permanent_position_sd_fraction <= 0:
        raise ValueError("Permanent-position SD must be positive and finite")
    if not isinstance(v.number_tracks, int) or v.number_tracks < 1:
        raise ValueError("number_tracks must be a positive integer")
    if not isinstance(v.number_motors, int) or v.number_motors < 0:
        raise ValueError("number_motors must be a nonnegative integer")
    lengths = per_track(v.track_length_um, v.number_tracks, "track_length_um")
    temporary = per_track(v.number_temporary_sites, v.number_tracks, "number_temporary_sites", True)
    permanent_counts = per_track(v.number_permanent_sites, v.number_tracks, "number_permanent_sites", True)
    ns = temporary + permanent_counts
    if (temporary < 0).any() or (permanent_counts < 0).any() or (ns < 2).any() or (lengths <= 0).any():
        raise ValueError("Each track needs positive length, >=2 sites, and nonnegative site counts")
    # Twelve decimal places in micrometers remove inversion roundoff in L/(N-1).
    spacing = np.round(lengths / (ns - 1), 12)
    positive = (v.motor_run_length_um, v.motor_size_um, settings.chamber_size_um,
                settings.time_step_s, settings.sample_interval_s)
    nonnegative = (v.cutter_concentration, v.motor_brightness, v.track_brightness,
                   v.motor_speed_um_s, settings.duration_s, settings.encounter_rate_s,
                   settings.erasure_rate_per_concentration_s)
    if not all(np.isfinite(x) and x > 0 for x in positive):
        raise ValueError("Sizes, run length, chamber size, and time intervals must be positive and finite")
    if not all(np.isfinite(x) and x >= 0 for x in nonnegative):
        raise ValueError("Concentration, brightness, speed, duration, and rates must be nonnegative and finite")
    for p in (v.binding_probability_temporary, v.binding_probability_permanent, v.writing_probability):
        if not np.isfinite(p) or not 0 <= p <= 1:
            raise ValueError("Binding and writing probabilities must lie in [0, 1]")
    if not 0 < settings.minimum_on_fraction <= 1 or (spacing <= 0).any():
        raise ValueError("ON-density floor must lie in (0, 1]; site spacing must be positive")
    body = np.rint(v.motor_size_um / spacing).astype(int)
    if (body < 1).any() or (body >= ns).any():
        raise ValueError("Motor footprint must cover >=1 site and be shorter than each track")
    p_step = v.motor_speed_um_s * settings.time_step_s / spacing
    p_search = settings.encounter_rate_s * settings.time_step_s
    p_leave = spacing / v.motor_run_length_um
    p_cut = v.cutter_concentration * settings.erasure_rate_per_concentration_s * settings.time_step_s
    if (p_step > 0.6).any() or p_search > 1 or p_cut > 1:
        raise ValueError("Reduce time_step_s: walking probability must be <=0.6; other event probabilities <=1")
    if (p_leave / settings.minimum_on_fraction > 1).any():
        raise ValueError("Run length is too short for this site spacing and ON-density floor")
    for value, name in ((settings.duration_s, "duration_s"), (settings.sample_interval_s, "sample_interval_s")):
        ratio = value / settings.time_step_s
        if not np.isclose(ratio, round(ratio), rtol=0, atol=1e-9):
            raise ValueError(f"{name} must be an integer multiple of time_step_s")
    if settings.sample_interval_s < settings.time_step_s:
        raise ValueError("sample_interval_s must be at least time_step_s")
    rng = np.random.default_rng(settings.random_seed)
    if layout is None:
        starts, directions = [], []
        for length in lengths:
            for _ in range(20000):
                theta = rng.uniform(0, 2 * np.pi)
                direction = np.array([np.cos(theta), np.sin(theta)])
                center = rng.uniform(0, settings.chamber_size_um, 2)
                start, end = center - length * direction / 2, center + length * direction / 2
                if (start >= 0).all() and (end >= 0).all() and (start <= settings.chamber_size_um).all() and (end <= settings.chamber_size_um).all():
                    starts.append(start)
                    directions.append(direction)
                    break
            else:
                raise ValueError("Could not fit track into chamber")
        starts, directions = np.array(starts), np.array(directions)
    else:
        if layout["random_seed"] != settings.random_seed:
            raise ValueError("Saved layout has a different random seed; set layout to null to draw a new realization")
        starts = np.array(layout["starts"], dtype=float)
        directions = np.array(layout["directions"], dtype=float)
        if starts.shape != (v.number_tracks, 2) or directions.shape != starts.shape:
            raise ValueError("Saved layout has a different track count; set layout to null to generate a new layout")
        if not np.isfinite(starts).all() or not np.isfinite(directions).all() or not np.allclose(np.linalg.norm(directions, axis=1), 1):
            raise ValueError("Layout must contain finite coordinates and unit directions")
        ends = starts + directions * lengths[:, None]
        if (starts < 0).any() or (ends < 0).any() or (starts > settings.chamber_size_um).any() or (ends > settings.chamber_size_um).any():
            raise ValueError("Saved layout does not fit the requested tracks/chamber; set layout to null")
        rng.bit_generator.state = layout["rng_state"]
    offsets = np.concatenate([[0], np.cumsum(ns)])[:-1]
    total = int(ns.sum())
    on = np.zeros(total, dtype=bool)
    occupied = np.zeros(total, dtype=np.int32)
    permanent = np.zeros(total, dtype=bool)
    # Site placement never advances the dynamics RNG beyond the original seeding draw.
    placement_rng = np.random.default_rng([settings.random_seed, 173])
    # Preserve the professor's seeding draw, even though every track is seeded.
    for j in rng.permutation(v.number_tracks):
        if rules.permanent_site_placement == "upstream":
            indices = np.arange(permanent_counts[j])
        else:
            x = np.arange(ns[j]) / (ns[j] - 1)
            weights = np.exp(-0.5 * ((x - 0.5) / rules.permanent_position_sd_fraction) ** 2)
            weights /= weights.sum()
            indices = placement_rng.choice(ns[j], size=permanent_counts[j], replace=False, p=weights)
        on[offsets[j] + indices] = True
        permanent[offsets[j] + indices] = True
    track = np.full(v.number_motors, -1, dtype=np.int32)
    position = np.zeros(v.number_motors, dtype=np.int32)
    binding_position = np.zeros(v.number_motors, dtype=np.int32)
    runs = []
    cdf = np.cumsum(ns / ns.sum())
    steps = int(round(settings.duration_s / settings.time_step_s))
    every = max(1, int(round(settings.sample_interval_s / settings.time_step_s)))
    times, on_history, track_history, position_history = [], [], [], []

    def detach(i):
        j = track[i]
        g = offsets[j] + position[i]
        occupied[g:g + body[j]] -= 1
        runs.append((position[i] - binding_position[i]) * spacing[j])
        if event_callback is not None:
            event_callback("release", (step + 1) * settings.time_step_s, int(i), int(j))
        track[i] = -1

    def report_state(time_s):
        if state_callback is not None:
            state = on.view()
            state.flags.writeable = False
            state_callback(time_s, state)

    report_state(0.0)
    for step in range(steps + 1):
        if step % every == 0:
            times.append(step * settings.time_step_s)
            on_history.append(on.copy())
            track_history.append(track.copy())
            position_history.append(position.copy())
        if step == steps:
            break
        random_events = rng.random(v.number_motors)
        for i in range(v.number_motors):
            j = track[i]
            if j < 0:
                if random_events[i] < p_search:
                    j = int(np.searchsorted(cdf, rng.random()))
                    pos = int(rng.integers(0, ns[j] - body[j] + 1))
                    g = offsets[j] + pos
                    footprint = slice(g, g + body[j])
                    if occupied[footprint].any() or not on[footprint].any():
                        continue
                    # Baseline p=1 consumes no extra random number, matching the notebook.
                    if v.binding_probability_temporary != 1 or v.binding_probability_permanent != 1:
                        n_perm = int(permanent[footprint].sum())
                        n_temp = int(on[footprint].sum()) - n_perm
                        probability = binding_probability(n_temp, n_perm, v.binding_probability_temporary, v.binding_probability_permanent)
                        if probability <= 0 or (probability < 1 and rng.random() >= probability):
                            continue
                    track[i] = j
                    position[i] = pos
                    binding_position[i] = pos
                    occupied[footprint] += 1
                    if event_callback is not None:
                        event_callback("bind", (step + 1) * settings.time_step_s, int(i), int(j))
            elif random_events[i] < p_step[j]:
                pos = position[i]
                lead = pos + body[j]
                if lead >= ns[j]:
                    detach(i)
                    continue
                gl = offsets[j] + lead
                if occupied[gl] != 0:
                    continue
                occupied[offsets[j] + pos] -= 1
                occupied[gl] += 1
                position[i] = pos + 1
                if rng.random() < v.writing_probability:
                    on[gl] = True
                # Every mode retains baseline's density-dependent release trial.
                f = on[gl - body[j] + 1:gl + 1].sum() / body[j]
                stochastic_release = rng.random() < p_leave[j] / max(f, settings.minimum_on_fraction)
                reached_cap = (rules.run_length_mode == "capped_steps"
                               and position[i] - binding_position[i] >= rules.fixed_run_steps)
                if stochastic_release or reached_cap:
                    detach(i)
        eligible = np.flatnonzero(on & ~permanent)
        if eligible.size:
            if rules.protect_occupied_sites:
                eligible = eligible[occupied[eligible] == 0]
            if eligible.size:
                on[eligible[rng.random(eligible.size) < p_cut]] = False
        report_state((step + 1) * settings.time_step_s)
    return Result(starts, directions, lengths, ns, offsets, spacing, body, permanent,
                  np.array(times), np.array(on_history), np.array(track_history),
                  np.array(position_history), np.array(runs, dtype=float))
