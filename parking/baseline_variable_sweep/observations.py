"""Unit-owned online summaries; observers never draw random numbers."""
import numpy as np


class Recorder:
    def __init__(self, counts, settings):
        self.counts = counts
        self.offsets = np.r_[0, np.cumsum(counts)[:-1]]
        self.settings = settings
        self.open_motor = {}
        self.motor_episodes = []
        self.passages = []
        self.dark_start = np.full(len(counts), np.nan)
        self.dwell_total = self.passage_total = 0.
        self.dwell_count = self.passage_count = 0
        self.rows = []

    def event(self, kind, time, motor, track):
        if kind == 'bind':
            self.open_motor[motor] = (track, time)
        else:
            original, start = self.open_motor.pop(motor)
            self.motor_episodes.append((motor, original, start, time, 1))
            self.dwell_total += time - start
            self.dwell_count += 1

    def state(self, time, on):
        counts = np.add.reduceat(on, self.offsets, dtype=np.int32)
        fraction = counts / self.counts
        dark, lit = fraction < .05, fraction > .40
        self.dark_start[dark & np.isnan(self.dark_start)] = time
        complete = np.flatnonzero(lit & np.isfinite(self.dark_start))
        for track in complete:
            start = self.dark_start[track]
            self.passages.append((track, start, time, 1))
            self.passage_total += time - start
            self.passage_count += 1
        self.dark_start[complete] = np.nan
        step = round(time / self.settings.time_step_s)
        interval = round(self.settings.sample_interval_s / self.settings.time_step_s)
        if step % interval == 0:
            self.rows.append((time, len(self.open_motor) / len(counts),
                self.dwell_total / self.dwell_count if self.dwell_count else np.nan,
                counts.sum() / self.counts.sum(),
                self.passage_total / self.passage_count if self.passage_count else np.nan,
                lit.sum(), (~(dark | lit)).sum(), dark.sum(),
                self.dwell_count, self.passage_count))

    def finish(self):
        end = self.settings.duration_s
        for motor, (track, start) in self.open_motor.items():
            self.motor_episodes.append((motor, track, start, end, 0))
        for track in np.flatnonzero(np.isfinite(self.dark_start)):
            self.passages.append((track, self.dark_start[track], end, 0))
        return dict(summary=np.asarray(self.rows),
                    motor_episodes=np.asarray(self.motor_episodes).reshape(-1, 5),
                    dark_to_lit_episodes=np.asarray(self.passages).reshape(-1, 4))


COLUMNS = ('time_s', 'motors_per_track', 'motor_dwell_s', 'fraction_on',
           'dark_to_lit_s', 'lit_tracks', 'intermediate_tracks', 'dark_tracks',
           'completed_dwell_episodes', 'completed_dark_to_lit_episodes')
