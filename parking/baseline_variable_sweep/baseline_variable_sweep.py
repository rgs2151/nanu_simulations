"""Run two baseline sweeps; render-only reuses all saved trajectories."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
import hashlib
import json
import multiprocessing
import os
from pathlib import Path

import numpy as np
from protein_simulation.engine import simulate
from protein_simulation.parameters import Variables, RunSettings, ModelRules, per_track
from observations import Recorder

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[1]
CONFIG = None
CACHE = None


def run_one(job):
    key, motors, cutter = job
    v = replace(Variables(**CONFIG['variables']), number_motors=motors,
                cutter_concentration=cutter)
    settings = RunSettings(**CONFIG['run'])
    counts = (per_track(v.number_temporary_sites, v.number_tracks, 'temporary', True)
              + per_track(v.number_permanent_sites, v.number_tracks, 'permanent', True))
    recorder = Recorder(counts, settings)
    result = simulate(v, settings, CONFIG['layout'], ModelRules(**CONFIG['rules']),
                      event_callback=recorder.event, state_callback=recorder.state)
    np.savez_compressed(CACHE / f'{key}.npz', **asdict(result), **recorder.finish())
    return key


def main():
    global CONFIG, CACHE
    parser = argparse.ArgumentParser()
    parser.add_argument('--render-only', action='store_true')
    parser.add_argument('--workers', type=int, default=max(1, min(60, len(os.sched_getaffinity(0))-4)))
    args = parser.parse_args()
    CONFIG = json.loads((UNIT / 'config.json').read_text())
    jobs = {}
    sweeps = {}
    for name, values in CONFIG['sweeps'].items():
        sweeps[name] = []
        for value in values:
            motors = int(value) if name == 'motor' else CONFIG['variables']['number_motors']
            cutter = float(value) if name == 'cutter' else CONFIG['variables']['cutter_concentration']
            key = f'm{motors:03d}_c{cutter:.12g}'
            jobs[key] = (key, motors, cutter)
            sweeps[name].append(key)
    provenance_file = UNIT / 'cache' / 'manifest.json'
    if provenance_file.exists():
        provenance = json.loads(provenance_file.read_text())
        if provenance['configuration'] != CONFIG:
            raise ValueError('Configuration differs from cache; use a separate unit/cache for a new experiment.')
    else:
        sources = {str(p.relative_to(ROOT)): p.read_text() for p in
                   [ROOT/'protein_simulation/engine.py', ROOT/'protein_simulation/parameters.py',
                    UNIT/'observations.py', Path(__file__)]}
        provenance = {'configuration': CONFIG, 'source_sha256':
                      {p: hashlib.sha256(s.encode()).hexdigest() for p, s in sources.items()},
                      'source_text': sources, 'sweeps': sweeps}
        provenance_file.parent.mkdir(exist_ok=True)
        provenance_file.write_text(json.dumps(provenance, indent=2)+'\n')
    CACHE = UNIT / 'cache'
    missing = [job for key, job in jobs.items() if not (CACHE/f'{key}.npz').exists()]
    if missing and args.render_only:
        raise ValueError(f'{len(missing)} simulation caches are missing.')
    if missing:
        # Fork inherits one loaded engine in every worker, even during parallel repository work.
        print(f'Running {len(missing)} simulations with {args.workers} workers.', flush=True)
        with ProcessPoolExecutor(max_workers=args.workers,
                                 mp_context=multiprocessing.get_context('fork')) as pool:
            futures = [pool.submit(run_one, job) for job in missing]
            for i, future in enumerate(as_completed(futures), 1):
                key = future.result()
                print(f'{i}/{len(missing)} cached: {key}', flush=True)
    from plot import render
    render(UNIT, CONFIG, sweeps)
    print('Both sweep figures saved.', flush=True)


if __name__ == '__main__':
    main()
