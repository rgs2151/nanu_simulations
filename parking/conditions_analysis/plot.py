"""Six descriptive panels with fixed project-wide condition colors."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from protein_simulation.style import CONDITION_COLORS, CONDITION_LABELS, apply_plot_style

PANELS = (
    ('motors_per_track', 'Motors bound per track', 'Motors / track'),
    ('fraction_on', 'Fraction of sites ON', 'Fraction ON'),
    ('lit_tracks', 'Lit tracks', 'Tracks (count)'),
    ('dark_tracks', 'Dark tracks', 'Tracks (count)'),
    ('dark_to_lit_s', 'Time for a dark track to light up', 'Dark-to-lit time (s)'),
    ('motor_dwell_s', 'Motor dwell time on a track', 'Dwell time (s)'),
)
LINESTYLES = {name: '-' for name in CONDITION_COLORS}


def render(folder, times, summaries, number_tracks):
    apply_plot_style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.subplots_adjust(left=.085, right=.975, bottom=.07, top=.91, wspace=.46, hspace=.55)
    handles = [Line2D([], [], color=CONDITION_COLORS[name], lw=2, linestyle=LINESTYLES[name],
                      label=CONDITION_LABELS[name]) for name in CONDITION_COLORS]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .99), ncol=4, fontsize=11)
    for idx, (key, title, ylabel) in enumerate(PANELS):
        ax = axes.flat[idx]
        for name, values in summaries.items():
            ax.plot(times, values[key], color=CONDITION_COLORS[name], lw=1.8,
                    linestyle=LINESTYLES[name], label=CONDITION_LABELS[name])
        ax.set_title(title, pad=12)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel(ylabel)
        ax.set_xlim(0, times[-1])
        ax.set_xticks(np.linspace(0, times[-1], 5))
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
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=key in ('lit_tracks', 'dark_tracks')))
        ax.set_box_aspect(0.78)
        ax.text(-.20, 1.12, chr(ord('A') + idx), transform=ax.transAxes, fontsize=13, weight='bold')
    fig.savefig(folder / 'conditions_analysis.pdf', bbox_inches='tight')
    fig.savefig(folder / 'conditions_analysis.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
