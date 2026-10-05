"""Read only the professor's parameter assignments and simulation definitions."""
import ast
import json
from pathlib import Path

import numpy as np

NOTEBOOK = Path(__file__).resolve().parents[2] / 'ref/dna_rail_transport_sim_en__1_.ipynb'


def reference_namespace():
    notebook = json.loads(NOTEBOOK.read_text())
    parameters = ast.parse(''.join(notebook['cells'][1]['source']))
    core = ast.parse(''.join(notebook['cells'][2]['source']))
    nodes = [n for n in parameters.body if isinstance(n, ast.Assign)]
    nodes += [n for n in core.body if isinstance(n, ast.FunctionDef)]
    namespace = {'np': np}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(NOTEBOOK), 'exec'), namespace)
    return namespace


def create_baseline_config():
    """Translate one original realization to explicit scientific input values."""
    ref = reference_namespace()
    rng = np.random.default_rng(ref['SEED'])
    rails = ref['build_rails'](rng)
    return {
        'variables': {
            'number_motors': ref['N_TRANSPORTER'],
            'number_tracks': ref['N_RAILS'],
            'cutter_concentration': 1.0,
            'motor_brightness': 1.0,
            'track_brightness': 1.0,
            'track_length_um': ((rails['nsites'] - 1) * ref['SITE_SPACING']).tolist(),
            'number_temporary_sites': (rails['nsites'] - ref['SEEDS_PER_RAIL']).tolist(),
            'number_permanent_sites': ref['SEEDS_PER_RAIL'],
            'motor_speed_um_s': ref['SPEED'],
            'motor_run_length_um': ref['RUN_LENGTH'],
            'motor_size_um': ref['BODY_LEN'],
            'binding_probability_temporary': 1.0,
            'binding_probability_permanent': 1.0,
            'writing_probability': ref['P_WRITE'],
        },
        'run': {
            'chamber_size_um': ref['CHAMBER'],
            'duration_s': ref['T_TOTAL'],
            'time_step_s': ref['DT'],
            'sample_interval_s': ref['SAMPLE_EVERY'],
            'random_seed': ref['SEED'],
            'encounter_rate_s': ref['K_SEARCH'],
            'erasure_rate_per_concentration_s': ref['K_OFF'],
            'minimum_on_fraction': ref['ON_FLOOR'],
        },
        'layout': {
            'starts': rails['start'].tolist(),
            'directions': rails['dir'].tolist(),
            'rng_state': rng.bit_generator.state,
            'random_seed': ref['SEED'],
        },
    }


if __name__ == '__main__':
    path = Path(__file__).with_name('baseline.json')
    if path.exists():
        raise FileExistsError('The baseline preset already exists; do not silently replace scientific inputs')
    path.write_text(json.dumps(create_baseline_config(), indent=2) + '\n')
