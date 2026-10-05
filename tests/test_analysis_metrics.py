"""Hand-calculated checks for threshold passages, censoring, and segment lengths."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np

UNIT = Path(__file__).resolve().parents[1] / 'parking/conditions_analysis'
spec = importlib.util.spec_from_file_location('analysis_metrics', UNIT / 'metrics.py')
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
spec = importlib.util.spec_from_file_location('analysis_events', UNIT / 'events.py')
events = importlib.util.module_from_spec(spec)
spec.loader.exec_module(events)


class AnalysisMetrics(unittest.TestCase):
    def test_strict_professor_thresholds(self):
        np.testing.assert_array_equal(metrics.classify_tracks(np.array([.049, .05, .4, .401])), [-1, 0, 0, 1])

    def test_dark_passage_includes_intermediate_without_restarting(self):
        times = np.arange(9, dtype=float)
        frac = np.array([.01, .2, .02, .41, .3, .01, .2, .45, .01])[:, None]
        episodes = metrics.dark_to_lit_episodes(times, frac)
        np.testing.assert_array_equal(episodes, [[0, 0, 3, 1], [0, 5, 7, 1], [0, 8, 8, 0]])
        mean, count = metrics.cumulative_completed_mean(episodes[:, 1], episodes[:, 2], episodes[:, 3], np.array([0, 3, 6, 7, 8]))
        np.testing.assert_allclose(mean, [np.nan, 3, 3, 2.5, 2.5], equal_nan=True)
        np.testing.assert_array_equal(count, [0, 1, 1, 2, 2])

    def test_no_completed_episodes_is_undefined(self):
        mean, count = metrics.cumulative_completed_mean(np.array([0]), np.array([10]), np.array([0]), np.array([0, 10]))
        self.assertTrue(np.isnan(mean).all())
        np.testing.assert_array_equal(count, [0, 0])

    def test_longest_path_never_connects_two_tracks(self):
        on = np.array([[0, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0]], dtype=bool)
        result = metrics.longest_within_track(on, np.array([0, 3]), np.array([3, 3]), np.array([.1, .2]))
        np.testing.assert_allclose(result, [.2, .4, 0])

    def test_rebinding_to_same_track_is_a_new_dwell(self):
        recorder = events.EventRecorder(np.array([0]), 1)
        recorder.event('bind', .5, 0, 0)
        recorder.event('release', 1., 0, 0)
        recorder.event('bind', 1.5, 0, 0)
        result = recorder.finish(2.)
        np.testing.assert_array_equal(result['motor_episodes'], [[0, 0, .5, 1., 1], [0, 0, 1.5, 2., 0]])


if __name__ == '__main__':
    unittest.main()
