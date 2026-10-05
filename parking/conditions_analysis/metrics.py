"""Descriptive metrics for one cached realization per condition."""
import numpy as np


def classify_tracks(fraction, low=0.05, high=0.40):
    """Strict professor thresholds: low, intermediate, high -> -1, 0, 1."""
    return np.where(fraction > high, 1, np.where(fraction < low, -1, 0))


def dark_to_lit_episodes(times, fraction, low=0.05, high=0.40):
    """Track ID, dark-entry time, high-entry/end time, completed flag.

    Passage time includes intermediate states. Returning from intermediate to dark
    does not restart the clock; a new episode begins only after a completed passage.
    """
    states = classify_tracks(fraction, low, high)
    episodes = []
    for j in range(states.shape[1]):
        relevant = np.flatnonzero(states[:, j])
        if relevant.size == 0:
            continue
        changes = relevant[np.r_[True, np.diff(states[relevant, j]) != 0]]
        start = None
        for idx in changes:
            if states[idx, j] == -1:
                start = times[idx]
            elif start is not None:
                episodes.append((j, start, times[idx], 1))
                start = None
        if start is not None:
            episodes.append((j, start, times[-1], 0))
    return np.asarray(episodes, dtype=float).reshape(-1, 4)


def cumulative_completed_mean(start, end, completed, query_times):
    """Mean duration among episodes completed by each query time; undefined before any."""
    keep = np.asarray(completed, dtype=bool)
    order = np.argsort(end[keep])
    finish = end[keep][order]
    durations = (end[keep] - start[keep])[order]
    counts = np.searchsorted(finish, query_times, side='right')
    totals = np.r_[0.0, np.cumsum(durations)]
    mean = np.full(len(query_times), np.nan)
    np.divide(totals[counts], counts, out=mean, where=counts > 0)
    return mean, counts


def longest_within_track(on, offsets, site_counts, spacing):
    """Longest first-to-last-site span; never connect adjoining array blocks/tracks."""
    longest = np.zeros(len(on))
    for k, state in enumerate(on):
        for offset, count, dx in zip(offsets, site_counts, spacing):
            site_on = state[offset:offset+count]
            transitions = np.diff(np.r_[False, site_on, False].astype(np.int8))
            lengths = np.flatnonzero(transitions == -1) - np.flatnonzero(transitions == 1)
            if lengths.size:
                longest[k] = max(longest[k], (lengths.max() - 1) * dx)
    return longest


def summarize(result, observations, low=0.05, high=0.40):
    times = result.times
    counts = np.add.reduceat(result.on.astype(np.int32), result.offsets, axis=1)
    fraction = counts / result.site_counts[None, :]
    states = classify_tracks(fraction, low, high)
    fine_fraction = observations['track_on'] / result.site_counts[None, :]
    passages = dark_to_lit_episodes(observations['times'], fine_fraction, low, high)
    passage_mean, passage_count = cumulative_completed_mean(passages[:, 1], passages[:, 2], passages[:, 3], times)
    dwell = observations['motor_episodes']
    dwell_mean, dwell_count = cumulative_completed_mean(dwell[:, 2], dwell[:, 3], dwell[:, 4], times)
    summary = {
        'motors_per_track': (result.motor_track >= 0).sum(axis=1) / len(result.site_counts),
        'fraction_on': counts.sum(axis=1) / result.site_counts.sum(),
        'lit_tracks': (states == 1).sum(axis=1),
        'dark_tracks': (states == -1).sum(axis=1),
        'intermediate_tracks': (states == 0).sum(axis=1),
        'dark_to_lit_s': passage_mean,
        'motor_dwell_s': dwell_mean,
        'longest_lit_segment_um': longest_within_track(result.on, result.offsets, result.site_counts, result.spacing),
        'completed_dark_to_lit_episodes': passage_count,
        'completed_dwell_episodes': dwell_count,
    }
    if not np.all(summary['lit_tracks'] + summary['dark_tracks'] + summary['intermediate_tracks'] == len(result.site_counts)):
        raise AssertionError('Track classifications do not partition tracks')
    return summary, passages
