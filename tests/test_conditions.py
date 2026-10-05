"""Mechanistic checks for isolated condition switches and stable object fluorescence."""
from dataclasses import replace
import unittest

import numpy as np

from protein_simulation import ModelRules, RunSettings, Variables, simulate, sample_population_fluorescence


class Conditions(unittest.TestCase):
    def setUp(self):
        self.v = Variables(1, 1, 1, 1, 0.12, 2.0, 130, 15, 0.01, 20, 0.4, 1, 1, 1)
        self.s = RunSettings(duration_s=500, sample_interval_s=0.5, encounter_rate_s=2)

    def test_cutting_under_motor(self):
        settings = replace(self.s, erasure_rate_per_concentration_s=2)
        protected = simulate(self.v, settings)
        unprotected = simulate(self.v, settings, rules=ModelRules(protect_occupied_sites=False))
        # With p_cut=1 every temporary ON site is erased at each step if protection is off.
        self.assertTrue((unprotected.on == unprotected.permanent).all())
        self.assertTrue(protected.on[:, ~protected.permanent].any())
        self.assertTrue(unprotected.on[:, unprotected.permanent].all())
        self.assertTrue((unprotected.motor_track >= 0).any())

    def test_fixed_steps_release_exactly_and_ignore_density_rule(self):
        rules = ModelRules(run_length_mode='fixed_steps', fixed_run_steps=5)
        variables = replace(self.v, writing_probability=0)
        result = simulate(variables, self.s, rules=rules)
        self.assertGreater(len(result.run_lengths), 0)
        np.testing.assert_array_equal(result.run_lengths, np.full(len(result.run_lengths), 5 * result.spacing[0]))
        other = simulate(replace(variables, motor_run_length_um=100), self.s, rules=rules)
        np.testing.assert_array_equal(result.on, other.on)
        np.testing.assert_array_equal(result.motor_position, other.motor_position)

    def test_fixed_run_can_end_at_track_boundary(self):
        result = simulate(self.v, replace(self.s, duration_s=1000), rules=ModelRules(run_length_mode='fixed_steps', fixed_run_steps=1000))
        self.assertGreater(len(result.run_lengths), 0)
        self.assertTrue((result.run_lengths < 1000 * result.spacing[0]).all())

    def test_random_permanent_sites_preserve_unique_counts(self):
        variables = replace(self.v, number_tracks=4)
        initial = replace(self.s, duration_s=0)
        result = simulate(variables, initial, rules=ModelRules(permanent_site_placement='random_normal'))
        np.testing.assert_array_equal(np.add.reduceat(result.permanent.astype(int), result.offsets), [15]*4)
        self.assertTrue((result.on[0] == result.permanent).all())
        baseline = simulate(variables, initial)
        np.testing.assert_array_equal(result.starts, baseline.starts)
        np.testing.assert_array_equal(result.directions, baseline.directions)
        self.assertFalse(np.array_equal(result.permanent, baseline.permanent))
        for j in range(4):
            positions = np.flatnonzero(result.permanent[result.offsets[j]:result.offsets[j]+result.site_counts[j]])
            self.assertGreater(np.ptp(positions), 15)

    def test_fluorescence_is_stable_per_id_and_separate_from_dynamics(self):
        variables = replace(self.v, number_motors=40, number_tracks=50)
        a = sample_population_fluorescence(variables, self.s)
        b = sample_population_fluorescence(variables, self.s)
        np.testing.assert_array_equal(a.motor_brightness, b.motor_brightness)
        np.testing.assert_array_equal(a.track_brightness, b.track_brightness)
        self.assertTrue(((a.motor_brightness >= .9) & (a.motor_brightness <= 1.1)).all())
        self.assertTrue(((a.track_brightness >= .108) & (a.track_brightness <= .132)).all())
        self.assertGreater(np.ptp(a.motor_brightness), 0)
        self.assertGreater(a.motor_brightness.min(), a.track_brightness.max())


if __name__ == '__main__':
    unittest.main()
