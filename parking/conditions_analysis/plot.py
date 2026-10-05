"""Seven descriptive panels with fixed project-wide condition colors."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

from protein_simulation.style import CONDITION_COLORS, CONDITION_LABELS

PANELS = (
    ('motors_per_track', 'Motors bound per track', 'Motors / track'),
    ('fraction_on', 'Fraction of sites ON', 'Fraction ON'),
    ('lit_tracks', 'Lit tracks', 'Tracks (count)'),
    ('dark_tracks', 'Dark tracks', 'Tracks (count)'),
    ('dark_to_lit_s', 'Time for a dark track to light up', 'Dark-to-lit time (s)'),
    ('motor_dwell_s', 'Motor dwell time on a track', 'Dwell time (s)'),
    ('longest_lit_segment_um', 'Longest lit path', 'Within-track length (µm)'),
)
LINESTYLES = {'baseline': '-', 'cutter': (0, (4, 2)), 'motor': (0, (7, 2)), 'permanent': (0, (2, 1.5))}


def render(folder, times, summaries, number_tracks):
    sns.set_theme(context='paper', style='ticks')
    plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'cm',
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.labelsize': 12, 'axes.titlesize': 13, 'xtick.labelsize': 11,
                         'ytick.labelsize': 11, 'legend.frameon': False, 'savefig.facecolor': 'white'})
    fig, axes = plt.subplots(3, 3, figsize=(14, 12))
    fig.subplots_adjust(left=.085, right=.975, bottom=.105, top=.86, wspace=.46, hspace=.55)
    handles = [Line2D([], [], color=CONDITION_COLORS[name], lw=2, linestyle=LINESTYLES[name],
                      label=CONDITION_LABELS[name]) for name in CONDITION_COLORS]
    fig.suptitle('Conditions analysis', fontsize=21, y=.975)
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .94), ncol=4, fontsize=11)
    for idx, (key, title, ylabel) in enumerate(PANELS):
        ax = axes.flat[idx]
        for name, values in summaries.items():
            ax.plot(times, values[key], color=CONDITION_COLORS[name], lw=1.8,
                    linestyle=LINESTYLES[name], label=CONDITION_LABELS[name])
        ax.set_title(title, pad=12)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel(ylabel)
        ax.set_xlim(0, times[-1])
        ax.set_xticks([0, times[-1]])
        if key in ('lit_tracks', 'dark_tracks'):
            upper = number_tracks
        elif key == 'fraction_on':
            upper = 1.0
        elif key == 'motors_per_track':
            upper = max(1.0, max(float(np.nanmax(v[key])) for v in summaries.values()))
        else:
            values = np.concatenate([v[key] for v in summaries.values()])
            finite = values[np.isfinite(values)]
            max_value = float(finite.max()) if finite.size else 1.0
            magnitude = 10 ** np.floor(np.log10(max_value)) if max_value > 0 else 1
            upper = max(magnitude, np.ceil(max_value / magnitude * 2) / 2 * magnitude)
        ax.set_ylim(-.025 * upper, 1.05 * upper)
        ax.set_yticks([0, upper])
        ax.set_box_aspect(0.78)
        sns.despine(ax=ax, trim=True, offset=6)
        ax.text(-.20, 1.12, chr(ord('A') + idx), transform=ax.transAxes, fontsize=13, weight='bold')
    for ax in axes.flat[7:]:
        ax.set_visible(False)
    fig.text(.085, .050, 'Lit >40% ON; dark <5% ON. Durations: cumulative means of completed episodes only.', fontsize=10, color='#444444')
    fig.text(.085, .028, 'One realization per condition; no confidence intervals. Path = longest contiguous ON segment within one track.', fontsize=10, color='#444444')
    fig.savefig(folder / 'conditions_analysis.pdf', bbox_inches='tight')
    fig.savefig(folder / 'conditions_analysis.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
