"""Four isolated model conditions; simulation and rendering have separate cache paths."""
import argparse
from dataclasses import asdict, fields
import hashlib
import json
from pathlib import Path
import platform

import numpy as np

from protein_simulation import (
    FluorescenceSettings, ModelRules, PopulationFluorescence, Result, RunSettings,
    Variables, sample_population_fluorescence, simulate,
)

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_result(path):
    with np.load(path, allow_pickle=False) as archive:
        return Result(**{f.name: archive[f.name] for f in fields(Result)})


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recompute', action='store_true', help='Explicitly refresh simulation/population caches')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--simulate-only', action='store_true')
    mode.add_argument('--render-only', action='store_true', help='Require valid caches; never simulate')
    args = parser.parse_args()
    if args.recompute and args.render_only:
        parser.error('--recompute and --render-only cannot be combined')
    config = json.loads((UNIT / 'config.json').read_text())
    baseline_path = (UNIT / config['shared_baseline']).resolve()
    shared = json.loads(baseline_path.read_text())
    shared['variables'].update(config['shared_variable_overrides'])
    variables, settings = Variables(**shared['variables']), RunSettings(**shared['run'])
    rules = {name: ModelRules(**(config['model_defaults'] | overrides)) for name, overrides in config['conditions'].items()}
    if set(rules) != {'baseline', 'cutter', 'motor', 'permanent'}:
        raise ValueError('This unit requires baseline, cutter, motor, and permanent conditions')
    expected = {'baseline': set(), 'cutter': {'protect_occupied_sites'},
                'motor': {'run_length_mode'}, 'permanent': {'permanent_site_placement'}}
    changed = {name: [key for key, value in asdict(rule).items() if value != asdict(rules['baseline'])[key]]
               for name, rule in rules.items()}
    if any(set(changed[name]) != expected[name] for name in rules):
        raise ValueError('Conditions must differ from the baseline in exactly their intended rule')
    cache, plots = UNIT / 'cache', UNIT / 'plots'
    cache.mkdir(exist_ok=True)
    plots.mkdir(exist_ok=True)
    population_identity = {'number_motors': variables.number_motors, 'number_tracks': variables.number_tracks,
                           'motor_mean': variables.motor_brightness, 'track_mean': variables.track_brightness,
                           'random_seed': settings.random_seed, 'fluorescence': config['fluorescence'],
                           'parameters_sha256': sha(ROOT / 'protein_simulation/parameters.py'), 'numpy': np.__version__}
    population_path, population_meta = cache / 'population.npz', cache / 'population.json'
    if population_path.exists() and not args.recompute:
        if not population_meta.exists() or json.loads(population_meta.read_text()) != population_identity:
            raise ValueError('Population inputs changed. Use --recompute.')
        with np.load(population_path, allow_pickle=False) as archive:
            population = PopulationFluorescence(archive['motor_brightness'], archive['track_brightness'])
    else:
        if args.render_only:
            raise FileNotFoundError('Missing population cache; run simulation first')
        population = sample_population_fluorescence(variables, settings, FluorescenceSettings(**config['fluorescence']))
        np.savez_compressed(population_path, **asdict(population))
        write_json(population_meta, population_identity)
    results, identities = {}, {}
    for name, rule in rules.items():
        identity = {'shared_inputs': shared, 'rules': asdict(rule),
                    'engine_sha256': sha(ROOT / 'protein_simulation/engine.py'),
                    'parameters_sha256': sha(ROOT / 'protein_simulation/parameters.py'),
                    'python': platform.python_version(), 'numpy': np.__version__}
        identities[name] = identity
        path, meta = cache / f'{name}.npz', cache / f'{name}.json'
        if path.exists() and not args.recompute:
            if not meta.exists() or json.loads(meta.read_text()) != identity:
                raise ValueError(f'{name}: stale cache. Use --recompute explicitly.')
            print(f'{name}: using cached simulation', flush=True)
            results[name] = read_result(path)
        else:
            if args.render_only:
                raise FileNotFoundError(f'{name}: missing cache; run simulation first')
            print(f'{name}: simulating...', flush=True)
            results[name] = simulate(variables, settings, shared.get('layout'), rule)
            np.savez_compressed(path, **asdict(results[name]))
            write_json(meta, identity)
    base = results['baseline']
    checks = {'only_intended_rule_differs': changed, 'shared_geometry': {}, 'shared_site_counts': {},
              'permanent_counts_correct': {}, 'permanent_sites_stay_on': {}, 'fixed_run_limit_respected': None}
    for name, result in results.items():
        checks['shared_geometry'][name] = all(np.array_equal(getattr(base, field), getattr(result, field))
                                               for field in ('starts', 'directions', 'lengths', 'spacing', 'times'))
        checks['shared_site_counts'][name] = np.array_equal(base.site_counts, result.site_counts)
        counts = np.add.reduceat(result.permanent.astype(int), result.offsets)
        base_counts = np.add.reduceat(base.permanent.astype(int), base.offsets)
        checks['permanent_counts_correct'][name] = np.array_equal(counts, base_counts)
        checks['permanent_sites_stay_on'][name] = bool(result.on[:, result.permanent].all())
    fixed = results['motor']
    checks['fixed_run_limit_respected'] = bool((fixed.run_lengths <= rules['motor'].fixed_run_steps * fixed.spacing.max()).all())
    checks['nonplacement_conditions_share_permanent_mask'] = all(np.array_equal(base.permanent, results[name].permanent) for name in ('cutter', 'motor'))
    # Compare with previously verified baseline arrays without touching its artifacts.
    original_cache = baseline_path.parent / 'cache/reference.npz'
    checks['baseline_reference_cache_available'] = original_cache.exists()
    if original_cache.exists():
        original = read_result(original_cache)
        checks['baseline_exact_reference_match'] = all(np.array_equal(getattr(base, f.name), getattr(original, f.name)) for f in fields(Result))
        if not checks['baseline_exact_reference_match']:
            raise AssertionError('Shared-engine baseline differs from the preserved reference result')
    for name in ('shared_geometry', 'shared_site_counts', 'permanent_counts_correct', 'permanent_sites_stay_on'):
        if not all(checks[name].values()):
            raise AssertionError(f'Condition invariant failed: {name}')
    if not checks['fixed_run_limit_respected'] or not checks['nonplacement_conditions_share_permanent_mask']:
        raise AssertionError('Condition rule invariant failed')
    write_json(cache / 'validation.json', checks)
    if args.simulate_only:
        print('All four simulations cached and validated.', flush=True)
        return
    from render import render_condition
    for path in plots.iterdir():
        if path.is_file():
            path.unlink()
    for name, result in results.items():
        print(f'{name}: rendering from cached states', flush=True)
        render_condition(plots, name, result, population, settings, rules[name])
    write_json(plots / 'validation.json', checks)
    write_json(plots / 'manifest.json', {'conditions': identities, 'population': population_identity,
                                      'object_brightness': {k: v.tolist() for k, v in asdict(population).items()},
                                      'render_sha256': sha(UNIT / 'render.py')})
    print('Four condition GIFs complete.', flush=True)


if __name__ == '__main__':
    main()
