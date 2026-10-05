"""Replay each existing realization once for event logs, verifying exact cache parity."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import fields
import hashlib
import json
import multiprocessing
import os
from pathlib import Path

import numpy as np

from protein_simulation import ModelRules, Result, RunSettings, Variables, simulate
from events import EventRecorder

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[1]
SOURCE = UNIT.parent / 'conditions/cache'
NAMES = ('baseline', 'cutter', 'motor', 'permanent')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(name):
    return {'source_cache_sha256': sha(SOURCE / f'{name}.npz'),
            'source_manifest_sha256': sha(SOURCE / f'{name}.json'),
            'engine_sha256': sha(ROOT / 'protein_simulation/engine.py'),
            'parameters_sha256': sha(ROOT / 'protein_simulation/parameters.py'),
            'recorder_sha256': sha(UNIT / 'events.py'), 'numpy_version': np.__version__}


def record_one(name):
    source_meta = json.loads((SOURCE / f'{name}.json').read_text())
    shared = source_meta['shared_inputs']
    with np.load(SOURCE / f'{name}.npz', allow_pickle=False) as data:
        original = Result(**{f.name: data[f.name] for f in fields(Result)})
    v, settings = Variables(**shared['variables']), RunSettings(**shared['run'])
    observer = EventRecorder(original.offsets, v.number_motors)
    result = simulate(v, settings, shared.get('layout'), ModelRules(**source_meta['rules']),
                      event_callback=observer.event, state_callback=observer.state)
    checks = {f.name: np.array_equal(getattr(result, f.name), getattr(original, f.name)) for f in fields(Result)}
    if not all(checks.values()):
        raise AssertionError(f'{name}: event replay changed the cached trajectory: {checks}')
    observations = observer.finish(round(settings.duration_s / settings.time_step_s) * settings.time_step_s)
    snapshot_indices = np.searchsorted(observations['times'], original.times)
    np.testing.assert_array_equal(observations['track_on'][snapshot_indices],
                                  np.add.reduceat(original.on.astype(np.int32), original.offsets, axis=1))
    completed = observations['motor_episodes'][:, 4] == 1
    if int(completed.sum()) != len(original.run_lengths):
        raise AssertionError('Completed dwell episodes do not match completed runs')
    dest = UNIT / 'cache'
    np.savez_compressed(dest / f'{name}_events.npz', **observations)
    (dest / f'{name}_events.json').write_text(json.dumps(identity(name), indent=2) + '\n')
    return name, {'exact_trajectory_match': checks, 'completed_dwell_episodes': int(completed.sum()),
                  'ongoing_dwell_episodes': int((~completed).sum()), 'integration_states': len(observations['times'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=64)
    parser.add_argument('--recompute', action='store_true')
    parser.add_argument('--condition', choices=NAMES, action='append', help='Refresh only selected conditions')
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    (UNIT / 'cache').mkdir(exist_ok=True)
    needed = []
    for name in (args.condition or NAMES):
        cache, meta = UNIT / 'cache' / f'{name}_events.npz', UNIT / 'cache' / f'{name}_events.json'
        if cache.exists() and not args.recompute:
            recorded = json.loads(meta.read_text()) if meta.exists() else {}
            expected = identity(name)
            keys = ('source_cache_sha256', 'source_manifest_sha256', 'recorder_sha256', 'numpy_version')
            if any(recorded.get(key) != expected[key] for key in keys):
                raise ValueError(f'{name}: event cache is stale; explicitly use --recompute')
        else:
            needed.append(name)
    if not needed:
        print('All event caches are current; no simulation reruns.', flush=True)
        return
    available = len(os.sched_getaffinity(0))
    workers = min(args.workers, available, len(needed))
    print(f'{available} CPUs available; {workers} independent condition workers (requested limit {args.workers}).', flush=True)
    # One process per independent realization; preserve within-run sequential updates.
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        report = dict(pool.map(record_one, needed))
    report_path = UNIT / 'cache/replay_validation.json'
    previous = json.loads(report_path.read_text()) if report_path.exists() else {}
    previous.update(report)
    report_path.write_text(json.dumps(previous, indent=2) + '\n')
    print('Recorded exact-step observations; all four saved trajectories match.', flush=True)


if __name__ == '__main__':
    main()
