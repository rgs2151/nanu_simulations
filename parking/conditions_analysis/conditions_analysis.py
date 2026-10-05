"""Analyze existing condition trajectories and exact-step event caches; never simulate."""
import argparse
import csv
from dataclasses import fields
import json
from pathlib import Path

import numpy as np

from protein_simulation import Result
from protein_simulation.style import CONDITION_COLORS
from metrics import summarize
from plot import render
from record_events import identity, sha

UNIT = Path(__file__).resolve().parent
SOURCE = UNIT.parent / 'conditions/cache'
NAMES = tuple(CONDITION_COLORS)
LOW, HIGH = 0.05, 0.40


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recompute', action='store_true', help='Recalculate metrics only; never rerun dynamics')
    args = parser.parse_args()
    cache, plots = UNIT / 'cache', UNIT / 'plots'
    cache.mkdir(exist_ok=True)
    plots.mkdir(exist_ok=True)
    event_identities = {}
    for name in NAMES:
        expected = identity(name)
        event_meta = cache / f'{name}_events.json'
        if not event_meta.exists():
            raise ValueError(f'{name}: missing events; run record_events.py explicitly before analysis')
        recorded = json.loads(event_meta.read_text())
        # Analysis consumes recorded observations of the source cache, not new dynamics.
        keys = ('source_cache_sha256', 'source_manifest_sha256', 'recorder_sha256', 'numpy_version')
        if any(recorded[key] != expected[key] for key in keys):
            raise ValueError(f'{name}: stale events; run record_events.py explicitly before analysis')
        event_identities[name] = recorded | {'events_sha256': sha(cache / f'{name}_events.npz')}
    signature = {'event_sources': event_identities, 'metrics_sha256': sha(UNIT / 'metrics.py'),
                 'low_threshold': LOW, 'high_threshold': HIGH}
    metrics_path, metrics_meta = cache / 'summary.npz', cache / 'summary.json'
    summaries, passages = {}, {}
    if metrics_path.exists() and not args.recompute:
        if not metrics_meta.exists() or json.loads(metrics_meta.read_text()) != signature:
            raise ValueError('Summary cache is stale; use --recompute to recalculate metrics')
        with np.load(metrics_path, allow_pickle=False) as archive:
            times = archive['times']
            number_tracks = int(archive['number_tracks'])
            for name in NAMES:
                summaries[name] = {key.split('__', 1)[1]: archive[key] for key in archive.files if key.startswith(f'{name}__')}
                passages[name] = archive[f'passages_{name}']
        print('Reusing summary cache; no simulation or metric recomputation.', flush=True)
    else:
        packed = {}
        times = None
        for name in NAMES:
            with np.load(SOURCE / f'{name}.npz', allow_pickle=False) as archive:
                result = Result(**{f.name: archive[f.name] for f in fields(Result)})
            if times is not None:
                np.testing.assert_array_equal(times, result.times)
            times, number_tracks = result.times, len(result.site_counts)
            with np.load(cache / f'{name}_events.npz', allow_pickle=False) as archive:
                observations = {key: archive[key] for key in archive.files}
            summary, dark_passages = summarize(result, observations, LOW, HIGH)
            summaries[name], passages[name] = summary, dark_passages
            packed.update({f'{name}__{key}': value for key, value in summary.items()})
            packed[f'passages_{name}'] = dark_passages
        np.savez_compressed(metrics_path, times=times, number_tracks=number_tracks, **packed)
        metrics_meta.write_text(json.dumps(signature, indent=2) + '\n')
        print('Calculated seven metrics from cached trajectories and exact-step records.', flush=True)
    for path in plots.iterdir():
        if path.is_file():
            path.unlink()
    keys = list(summaries[NAMES[0]])
    with (plots / 'conditions_analysis.csv').open('w', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['condition', 'time_s', *keys])
        for name in NAMES:
            for i, time_s in enumerate(times):
                writer.writerow([name, time_s, *[summaries[name][key][i] if np.isfinite(summaries[name][key][i]) else '' for key in keys]])
    censoring = {}
    with (plots / 'duration_episodes.csv').open('w', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['condition', 'episode_type', 'motor_id', 'track_id', 'start_s', 'end_s', 'duration_s', 'completed'])
        for name in NAMES:
            with np.load(cache / f'{name}_events.npz', allow_pickle=False) as archive:
                dwell = archive['motor_episodes']
            for motor, track, start, end, completed in dwell:
                writer.writerow([name, 'motor_dwell', int(motor), int(track), start, end, end-start, int(completed)])
            for track, start, end, completed in passages[name]:
                writer.writerow([name, 'dark_to_lit', '', int(track), start, end, end-start, int(completed)])
            censoring[name] = {'completed_dwell': int(dwell[:, 4].sum()), 'ongoing_dwell': int((dwell[:, 4] == 0).sum()),
                               'completed_dark_to_lit': int(passages[name][:, 3].sum()),
                               'ongoing_dark_to_lit': int((passages[name][:, 3] == 0).sum())}
    render(plots, times, summaries, number_tracks)
    manifest = signature | {'colors': CONDITION_COLORS, 'censoring': censoring,
                            'plot_sha256': sha(UNIT / 'plot.py'), 'confidence_intervals': False,
                            'realizations_per_condition': 1, 'time_unit': 's', 'length_unit': 'um',
                            'event_replay_validation': json.loads((cache / 'replay_validation.json').read_text())}
    (plots / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Saved conditions_analysis.png, .pdf, and source tables.', flush=True)


if __name__ == '__main__':
    main()
