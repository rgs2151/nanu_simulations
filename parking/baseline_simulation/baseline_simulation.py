"""Run/cache the baseline, render GIFs, and optionally compare the original engine."""
import argparse
from copy import deepcopy
from dataclasses import asdict, fields
import hashlib
import json
from pathlib import Path
import platform

import numpy as np

from protein_simulation.engine import Result, simulate
from protein_simulation.parameters import RunSettings, Variables
from reference import NOTEBOOK, reference_namespace
from render import save_animation, save_snapshot

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_result(path, result):
    np.savez_compressed(path, **asdict(result))


def load_result(path):
    with np.load(path, allow_pickle=False) as archive:
        return Result(**{field.name: archive[field.name] for field in fields(Result)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=UNIT / 'baseline.json')
    parser.add_argument('--recompute', action='store_true')
    parser.add_argument('--verify-reference', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    variables, settings = Variables(**config['variables']), RunSettings(**config['run'])
    dynamics_config = deepcopy(config)
    for name in ('motor_brightness', 'track_brightness'):
        dynamics_config['variables'].pop(name)
    identity = {
        'config': dynamics_config,
        'engine_sha256': digest(ROOT / 'protein_simulation/engine.py'),
        'parameters_sha256': digest(ROOT / 'protein_simulation/parameters.py'),
        'numpy_version': np.__version__,
        'python_version': platform.python_version(),
    }
    cache, plots = UNIT / 'cache', UNIT / 'plots'
    cache.mkdir(exist_ok=True)
    plots.mkdir(exist_ok=True)
    manifest_path, cache_path = cache / 'manifest.json', cache / 'baseline.npz'
    if cache_path.exists() and not args.recompute:
        if not manifest_path.exists() or json.loads(manifest_path.read_text()) != identity:
            raise ValueError('Inputs/engine/environment changed. Use --recompute explicitly to refresh this unit.')
        result = load_result(cache_path)
        print('Reused baseline cache.', flush=True)
    else:
        print('Running translated baseline...', flush=True)
        result = simulate(variables, settings, config.get('layout'))
        save_result(cache_path, result)
        manifest_path.write_text(json.dumps(identity, indent=2) + '\n')
    reference = None
    report = {'reference_checked': False}
    if args.verify_reference:
        from reference import create_baseline_config
        if config != create_baseline_config():
            raise ValueError('Exact reference verification requires the unchanged baseline preset')
        ref_path, ref_meta = cache / 'reference.npz', cache / 'reference_manifest.json'
        ref_identity = {'notebook_sha256': digest(NOTEBOOK), 'numpy_version': np.__version__,
                        'python_version': platform.python_version(), 'adapter_sha256': digest(Path(__file__).with_name('reference.py'))}
        if ref_path.exists() and ref_meta.exists() and json.loads(ref_meta.read_text()) == ref_identity and not args.recompute:
            reference = load_result(ref_path)
        else:
            print('Running original notebook engine for exact comparison...', flush=True)
            ns = reference_namespace()
            rails, snaps, body, _ = ns['simulate'](verbose=False)
            reference = Result(rails['start'], rails['dir'], (rails['nsites'] - 1) * ns['SITE_SPACING'],
                               rails['nsites'], rails['offset'], np.full(ns['N_RAILS'], ns['SITE_SPACING']),
                               np.full(ns['N_RAILS'], body), snaps['perm'], snaps['t'], snaps['on'],
                               snaps['rail'], snaps['pos'], snaps['runs'])
            save_result(ref_path, reference)
            ref_meta.write_text(json.dumps(ref_identity, indent=2) + '\n')
        checks = {f.name: np.array_equal(getattr(result, f.name), getattr(reference, f.name)) for f in fields(Result)}
        report = {'reference_checked': True, 'exact_match': all(checks.values()), 'array_checks': checks,
                  'notebook_sha256': digest(NOTEBOOK)}
        if not report['exact_match']:
            raise AssertionError(f'Reference mismatch: {checks}')
        print('Exact match: every saved state, track layout, and completed run distance.', flush=True)
    # All files in plots/ are owned by this unit. Remove the previous iteration.
    for path in plots.iterdir():
        if path.is_file() and path.name != '.gitkeep':
            path.unlink()
    on_per_track = np.add.reduceat(result.on[-1].astype(int), result.offsets)
    fraction = on_per_track / result.site_counts
    report.update({
        'snapshot_count': len(result.times), 'site_count': int(result.site_counts.sum()),
        'completed_runs': len(result.run_lengths),
        'mean_completed_run_um': float(result.run_lengths.mean()) if result.run_lengths.size else None,
        'median_completed_run_um': float(np.median(result.run_lengths)) if result.run_lengths.size else None,
        'final_low_tracks': int((fraction < 0.05).sum()),
        'final_high_tracks': int((fraction > 0.40).sum()),
        'final_intermediate_tracks': int(((fraction >= 0.05) & (fraction <= 0.40)).sum()),
    })
    (plots / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    (plots / 'run_manifest.json').write_text(json.dumps({**identity, 'config': config}, indent=2) + '\n')
    print('Rendering baseline GIF...', flush=True)
    save_animation(plots / 'baseline.gif', result, variables, settings)
    save_snapshot(plots / 'baseline_final.png', result, variables, settings)
    if reference is not None:
        print('Rendering side-by-side comparison GIF...', flush=True)
        save_animation(plots / 'comparison.gif', result, variables, settings, reference)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
