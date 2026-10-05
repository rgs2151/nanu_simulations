"""Readable condition GIFs from cached states and persistent object fluorescence."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

TITLES = {
    'baseline': ('Baseline', 'Occupied temporary sites are protected.\nRun length depends on footprint ON density.\nPermanent sites form upstream clusters.'),
    'cutter': ('Cutter ignores motors', 'Temporary ON sites can be cut\neven underneath a motor.\nAll other baseline rules are retained.'),
    'motor': ('Capped motor run', 'Baseline stochastic release is retained.\nAt most {steps} forward steps ({distance:.3f} µm).\nTrack-end release is retained.'),
    'permanent': ('Scattered permanent sites', 'Same permanent-site count per track.\nDistinct positions sampled from a normal\ndistribution centered along each track.'),
}
MOTOR_COLOR = '#145bd7'
PERMANENT_COLOR = '#f4a51c'
TEMP_COLOR = '#cf2448'
EXPOSURE_MAX = 1.1


def make_figure(name, result, population, settings, rules):
    title, description = TITLES[name]
    description = description.format(steps=rules.fixed_run_steps, distance=rules.fixed_run_steps * result.spacing[0])
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    fig = plt.figure(figsize=(11.6, 8), facecolor='white')
    ax = fig.add_axes([0.045, 0.10, 0.62, 0.79])
    side = fig.add_axes([0.71, 0.10, 0.275, 0.77])
    side.set_axis_off()
    fig.text(0.045, 0.956, title, fontsize=21, weight='bold', color='#14213d')
    fig.text(0.045, 0.921, 'DNA track transport · same shared inputs across four conditions', fontsize=11, color='#596579')
    chamber = settings.chamber_size_um
    ax.set_xlim(-3, chamber + 3)
    ax.set_ylim(-3, chamber + 3)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.add_patch(plt.Rectangle((0, 0), chamber, chamber, fill=False, edgecolor='#cbd2dc', linewidth=0.9))
    start, direction, spacing = result.starts, result.directions, result.spacing
    normal = np.stack([-direction[:, 1], direction[:, 0]], axis=1)
    ends = start + direction * ((result.site_counts - 1) * spacing)[:, None]
    # One fixed sqrt display transfer for both populations; never rescale by condition/frame.
    track_alpha = np.sqrt(np.clip(population.track_brightness / EXPOSURE_MAX, 0, 1))
    rail_colors = np.zeros((len(start), 4))
    rail_colors[:, :3] = [0.16, 0.20, 0.27]
    rail_colors[:, 3] = track_alpha
    ax.add_collection(LineCollection(np.stack([start, ends], axis=1), colors=rail_colors, linewidths=1.45, zorder=1))
    segments, bin_start, bin_size = [], [], []
    permanent_xy, permanent_origins = [], []
    for j, (ns, off) in enumerate(zip(result.site_counts, result.offsets)):
        edges = np.linspace(0, ns, max(4, ns // 40) + 1).astype(int)
        for a, b in zip(edges[:-1], edges[1:]):
            if b > a:
                segments.append([start[j] + direction[j] * a * spacing[j],
                                 start[j] + direction[j] * (b-1) * spacing[j]])
                bin_start.append(off+a)
                bin_size.append(b-a)
        sites = np.flatnonzero(result.permanent[off:off+ns])
        xy = start[j] + direction[j] * (sites * spacing[j])[:, None]
        permanent_origins.extend(xy)
        permanent_xy.extend(xy - normal[j] * 1.1)
    temporary_artist = LineCollection(segments, linewidths=3.0, zorder=2)
    ax.add_collection(temporary_artist)
    if permanent_xy:
        xy = np.asarray(permanent_xy)
        connectors = np.stack([np.asarray(permanent_origins), xy], axis=1)
        ax.add_collection(LineCollection(connectors, colors='#bd8625', linewidths=0.3, alpha=0.25, zorder=2))
        ax.scatter(xy[:, 0], xy[:, 1], marker='D', s=15, facecolor=PERMANENT_COLOR,
                   edgecolor='#704709', linewidth=0.35, zorder=4)
    motors = LineCollection([], linewidths=4.3, zorder=5)
    ax.add_collection(motors)
    # Shared physical scale; glyph widths and perpendicular offsets are display-only.
    ax.plot([2, 12], [-2, -2], color='#344054', lw=2, clip_on=False)
    ax.text(7, -4.2, '10 µm', ha='center', va='top', fontsize=9, color='#344054', clip_on=False)
    side.text(0, 1, 'MODEL RULE', weight='bold', fontsize=10, color='#617085', va='top')
    side.text(0, .94, description, fontsize=10, linespacing=1.6, color='#243248', va='top')
    handles = [
        Line2D([], [], color='#a8adb6', lw=1.8, label='Track background\n(per-track fluorescence)'),
        Line2D([], [], color=TEMP_COLOR, lw=3.2, label='Temporary sites ON\n(opacity = local ON fraction)'),
        Line2D([], [], linestyle='None', marker='D', markersize=6, markerfacecolor=PERMANENT_COLOR,
               markeredgecolor='#704709', label='Permanent sites ON\n(offset to the opposite side)'),
        Line2D([], [], color=MOTOR_COLOR, lw=4.3, label='Bound motor\n(per-motor fluorescence)'),
    ]
    side.legend(handles=handles, loc='upper left', bbox_to_anchor=(-.025, .72), frameon=False,
                fontsize=10, labelspacing=1.5, handlelength=2.4, borderaxespad=0)
    time_text = side.text(0, .25, '', va='top', fontsize=16, weight='bold', color='#14213d')
    count_text = side.text(0, .19, '', va='top', fontsize=11, linespacing=1.6, color='#344054')
    side.text(0, .045, 'Fluorescence sampled once per object.\nSame population and exposure in every GIF.\nFree motors are not drawn.', fontsize=8.5,
              color='#617085', linespacing=1.5, va='top')
    bin_start, bin_size = np.asarray(bin_start), np.asarray(bin_size)
    temporary_mask = ~result.permanent
    motor_alpha = np.sqrt(np.clip(population.motor_brightness / EXPOSURE_MAX, 0, 1))
    base_motor_rgb = matplotlib.colors.to_rgb(MOTOR_COLOR)
    base_temp_rgb = matplotlib.colors.to_rgb(TEMP_COLOR)

    def update(k):
        temp_on = result.on[k] & temporary_mask
        density = np.add.reduceat(temp_on.astype(np.int32), bin_start) / bin_size
        colors = np.empty((len(density), 4))
        colors[:, :3] = base_temp_rgb
        colors[:, 3] = density
        temporary_artist.set_color(colors)
        bound = result.motor_track[k] >= 0
        ids = np.flatnonzero(bound)
        j, p = result.motor_track[k, bound], result.motor_position[k, bound]
        a = start[j] + direction[j] * (p * spacing[j])[:, None] + normal[j] * .9
        b = start[j] + direction[j] * ((p + result.body_sites[j]) * spacing[j])[:, None] + normal[j] * .9
        motors.set_segments(np.stack([a, b], axis=1))
        colors = np.empty((len(ids), 4))
        colors[:, :3] = base_motor_rgb
        colors[:, 3] = motor_alpha[ids]
        motors.set_color(colors)
        time_text.set_text(f't = {result.times[k]:,.0f} s')
        count_text.set_text(f'Bound motors  {len(ids)} / {len(population.motor_brightness)}\nTemporary ON  {temp_on.sum():,}\nPermanent ON  {result.permanent.sum():,}')
        return temporary_artist, motors, time_text, count_text

    update(0)
    return fig, update


def render_condition(folder, name, result, population, settings, rules):
    fig, update = make_figure(name, result, population, settings, rules)
    update(len(result.times)-1)
    fig.savefig(folder / f'{name}_final.png', dpi=100, facecolor='white')
    animation = FuncAnimation(fig, update, frames=len(result.times), interval=120, blit=False)
    # GIF stores 10-ms time units: this encodes 120 ms/frame.
    animation.save(folder / f'{name}.gif', writer=PillowWriter(fps=8), dpi=100)
    plt.close(fig)
