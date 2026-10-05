"""Scientific-control contracts; full baseline parity is checked by the unit runner."""
from dataclasses import replace
import unittest

import numpy as np

from protein_simulation import RunSettings, Variables, simulate
from protein_simulation.engine import binding_probability


class EngineControls(unittest.TestCase):
    def setUp(self):
        self.v = Variables(4, 3, 1.0, 1.0, 1.0, 2.0, 130, 15, 0.01, 20.0, 0.4, 1.0, 1.0, 1.0)
        self.s = RunSettings(duration_s=200, sample_interval_s=10)

    def test_brightness_does_not_change_dynamics(self):
        a = simulate(self.v, self.s)
        b = simulate(replace(self.v, motor_brightness=0.2, track_brightness=0.4), self.s)
        for field in ('on', 'motor_track', 'motor_position', 'run_lengths'):
            np.testing.assert_array_equal(getattr(a, field), getattr(b, field))

    def test_zero_binding_prevents_capture(self):
        r = simulate(replace(self.v, binding_probability_temporary=0, binding_probability_permanent=0), self.s)
        self.assertTrue((r.motor_track == -1).all())
        self.assertTrue((r.on == r.permanent).all())

    def test_zero_writing_preserves_seed_only_state(self):
        r = simulate(replace(self.v, writing_probability=0), self.s)
        self.assertTrue((r.on == r.permanent).all())

    def test_zero_cutter_cannot_erase(self):
        r = simulate(replace(self.v, cutter_concentration=0), self.s)
        self.assertTrue((np.diff(r.on.astype(int), axis=0) >= 0).all())
        self.assertTrue(r.on[:, r.permanent].all())

    def test_concentration_calibration_equivalence(self):
        a = simulate(self.v, self.s)
        b = simulate(replace(self.v, cutter_concentration=2), replace(self.s, erasure_rate_per_concentration_s=0.0004))
        np.testing.assert_array_equal(a.on, b.on)
        np.testing.assert_array_equal(a.motor_position, b.motor_position)

    def test_site_counts_and_exclusion(self):
        r = simulate(self.v, self.s)
        np.testing.assert_array_equal(r.site_counts, [145, 145, 145])
        self.assertEqual(r.permanent.sum(), 45)
        for track, pos in zip(r.motor_track, r.motor_position):
            for j in range(self.v.number_tracks):
                locations = np.sort(pos[track == j])
                self.assertTrue((np.diff(locations) >= r.body_sites[j]).all())
        self.assertTrue(r.on[:, r.permanent].all())

    def test_probability_is_combined_per_site(self):
        self.assertAlmostEqual(binding_probability(2, 1, 0.5, 0.25), 0.8125)
        self.assertEqual(binding_probability(0, 0, 1, 1), 0)
        self.assertEqual(binding_probability(0, 1, 0, 1), 1)

    def test_reject_invalid_counts_and_time_step(self):
        with self.assertRaises(ValueError):
            simulate(replace(self.v, number_temporary_sites=1.5), self.s)
        with self.assertRaises(ValueError):
            simulate(self.v, replace(self.s, time_step_s=100))
        with self.assertRaises(ValueError):
            simulate(self.v, replace(self.s, sample_interval_s=0.1))


if __name__ == '__main__':
    unittest.main()
