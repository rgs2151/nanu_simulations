"""Record fine-grained observations without modifying transport dynamics."""
import numpy as np


class EventRecorder:
    def __init__(self, offsets, number_motors):
        self.offsets = offsets
        self.open_motor = {}
        self.motor_episodes = []
        self.times = []
        self.track_on = []
        self.number_motors = number_motors

    def event(self, kind, time_s, motor_id, track_id):
        if kind == 'bind':
            if motor_id in self.open_motor:
                raise AssertionError('A bound motor cannot bind again before release')
            self.open_motor[motor_id] = (track_id, time_s)
        elif kind == 'release':
            original_track, start = self.open_motor.pop(motor_id)
            if original_track != track_id or time_s < start:
                raise AssertionError('Invalid motor residence interval')
            self.motor_episodes.append((motor_id, track_id, start, time_s, 1))
        else:
            raise ValueError(f'Unknown event: {kind}')

    def state(self, time_s, on):
        self.times.append(time_s)
        self.track_on.append(np.add.reduceat(on.astype(np.int32), self.offsets))

    def finish(self, end_s):
        for motor_id, (track_id, start) in self.open_motor.items():
            self.motor_episodes.append((motor_id, track_id, start, end_s, 0))
        return {
            'times': np.asarray(self.times),
            'track_on': np.asarray(self.track_on, dtype=np.int32),
            # Columns: motor ID, track ID, binding time, release/end time, completed.
            'motor_episodes': np.asarray(self.motor_episodes, dtype=float).reshape(-1, 5),
        }
