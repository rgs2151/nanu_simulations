"""Notebook-style baseline rendering; no dynamics or RNG calls."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection


def draw_frame(ax, result, frame, variables, settings, title='Translated baseline'):
    ax.clear()
    start, direction = result.starts, result.directions
    ns, offsets, spacing = result.site_counts, result.offsets, result.spacing
    ax.set_xlim(-2, settings.chamber_size_um + 2)
    ax.set_ylim(-2, settings.chamber_size_um + 2)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    c = settings.chamber_size_um
    ax.add_collection(LineCollection([[[0, 0], [c, 0]], [[c, 0], [c, c]],
                                      [[c, c], [0, c]], [[0, c], [0, 0]]], colors='k', linewidths=0.8))
    segments = np.stack([start, start + direction * ((ns - 1) * spacing)[:, None]], axis=1)
    # Relative brightness has fixed exposure; values above 1 saturate, not auto-normalize.
    track_color = 1 - 0.28 * min(variables.track_brightness, 1.0)
    ax.add_collection(LineCollection(segments, colors=str(track_color), linewidths=1.2))
    bins, bin_starts, bin_sizes, seeds = [], [], [], []
    for j in range(len(ns)):
        edges = np.linspace(0, ns[j], max(4, ns[j] // 40) + 1).astype(int)
        for a, b in zip(edges[:-1], edges[1:]):
            if b > a:
                bins.append([start[j] + direction[j] * a * spacing[j],
                             start[j] + direction[j] * (b - 1) * spacing[j]])
                bin_starts.append(offsets[j] + a)
                bin_sizes.append(b - a)
        permanent_indices = np.flatnonzero(result.permanent[offsets[j]:offsets[j] + ns[j]])
        if permanent_indices.size:
            seeds.append([start[j] + direction[j] * permanent_indices[0] * spacing[j],
                          start[j] + direction[j] * permanent_indices[-1] * spacing[j]])
    density = np.add.reduceat(result.on[frame].astype(np.int32), bin_starts) / bin_sizes
    colors = np.zeros((len(bins), 4))
    colors[:, 0] = 1
    colors[:, 3] = np.clip(density, 0, 1)
    ax.add_collection(LineCollection(bins, colors=colors, linewidths=3))
    if seeds:
        ax.add_collection(LineCollection(seeds, colors='#ffb300', linewidths=4.2, zorder=3))
    bound = result.motor_track[frame] >= 0
    j, p = result.motor_track[frame][bound], result.motor_position[frame][bound]
    if j.size:
        u = direction[j]
        offset = np.stack([-u[:, 1], u[:, 0]], axis=1) * 0.7
        a = start[j] + u * (p * spacing[j])[:, None] + offset
        b = start[j] + u * ((p + result.body_sites[j]) * spacing[j])[:, None] + offset
        ax.add_collection(LineCollection(np.stack([a, b], axis=1), colors='#1155ee',
                                         alpha=min(variables.motor_brightness, 1.0), linewidths=3.4, zorder=4))
    ax.set_title(f'{title}\nt = {result.times[frame]:.0f} s | ON = {result.on[frame].sum()} | bound = {bound.sum()}', fontsize=10)


def save_animation(path, result, variables, settings, reference=None):
    panels = 1 if reference is None else 2
    fig, axes = plt.subplots(1, panels, figsize=(6.4 * panels, 6.8), squeeze=False)
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.065, top=0.90, wspace=0.07)
    fig.text(0.5, 0.025, 'Gray: tracks   Orange: permanent sites   Red: ON-site density   Blue: motors', ha='center', fontsize=9)

    def update(k):
        if reference is not None:
            draw_frame(axes[0, 0], reference, k, variables, settings, 'Professor’s engine (rerun)')
        draw_frame(axes[0, -1], result, k, variables, settings)
        return []

    animation = FuncAnimation(fig, update, frames=len(result.times), interval=120, blit=False)
    path.unlink(missing_ok=True)
    # GIF timing uses 10-ms increments: an 8-fps writer encodes 120 ms/frame.
    animation.save(path, writer=PillowWriter(fps=8), dpi=100)
    plt.close(fig)


def save_snapshot(path, result, variables, settings):
    fig, ax = plt.subplots(figsize=(6.4, 6.8))
    draw_frame(ax, result, -1, variables, settings)
    fig.tight_layout()
    path.unlink(missing_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
