"""Scientific controls, numerical settings, and a frozen starting layout."""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Variables:
    number_motors: int
    number_tracks: int
    cutter_concentration: float
    motor_brightness: float
    track_brightness: float
    track_length_um: float | tuple[float, ...]
    number_temporary_sites: int | tuple[int, ...]
    number_permanent_sites: int | tuple[int, ...]
    motor_speed_um_s: float
    motor_run_length_um: float
    motor_size_um: float
    binding_probability_temporary: float
    binding_probability_permanent: float
    writing_probability: float


@dataclass(frozen=True)
class RunSettings:
    chamber_size_um: float = 100.0
    duration_s: float = 16000.0
    time_step_s: float = 0.5
    sample_interval_s: float = 200.0
    random_seed: int = 0
    encounter_rate_s: float = 0.2
    erasure_rate_per_concentration_s: float = 0.0008
    minimum_on_fraction: float = 0.02


def per_track(value, count, name, integer=False):
    raw = np.asarray(value, dtype=float)
    if raw.ndim == 0:
        raw = np.full(count, raw.item())
    if raw.shape != (count,) or not np.isfinite(raw).all():
        raise ValueError(f"{name} must be a finite scalar or one value per track")
    if integer and not np.equal(raw, np.floor(raw)).all():
        raise ValueError(f"{name} must contain integer counts")
    return raw.astype(int) if integer else raw


@dataclass(frozen=True)
class ModelRules:
    protect_occupied_sites: bool = True
    run_length_mode: str = "on_dependent"
    fixed_run_steps: int = 357
    permanent_site_placement: str = "upstream"
    permanent_position_sd_fraction: float = 0.3


@dataclass(frozen=True)
class FluorescenceSettings:
    fractional_half_range: float = 0.1


@dataclass
class PopulationFluorescence:
    motor_brightness: np.ndarray
    track_brightness: np.ndarray


def sample_population_fluorescence(v: Variables, settings: RunSettings,
                                   fluorescence: FluorescenceSettings = FluorescenceSettings()):
    """Intrinsic relative fluorescence, sampled once per ID on a separate RNG stream."""
    width = fluorescence.fractional_half_range
    if not np.isfinite(width) or not 0 <= width <= 1:
        raise ValueError("Fluorescence fractional_half_range must lie in [0, 1]")
    if not all(np.isfinite(x) and x >= 0 for x in (v.motor_brightness, v.track_brightness)):
        raise ValueError("Population mean brightness must be finite and nonnegative")
    rng = np.random.default_rng([settings.random_seed, 947])
    return PopulationFluorescence(
        v.motor_brightness * rng.uniform(1 - width, 1 + width, v.number_motors),
        v.track_brightness * rng.uniform(1 - width, 1 + width, v.number_tracks),
    )
