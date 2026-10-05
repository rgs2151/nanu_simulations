"""Compact seven-panel comparison in a two-by-four layout."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from protein_simulation.style import CONDITION_COLORS, CONDITION_LABELS, apply_plot_style

PANELS = (
    ('motors_per_track', 'Bound motors / track'),
    ('motor_dwell_s', 'Motor dwell time (s)'),
    ('fraction_on', 'Fraction of sites ON'),
    ('dark_to_lit_s', 'Dark-to-lit time (s)'),
    ('lit_tracks', 'Lit track count'),
    ('intermediate_tracks', 'Intermediate track count'),
    ('dark_tracks', 'Dark track count'),
)


def render(folder, times, summaries, number_tracks):
    apply_plot_style()
    fig, axes = plt.subplots(2, 4, figsize=(16, 7))
    fig.subplots_adjust(left=.065, right=.985, bottom=.16, top=.95, wspace=.32, hspace=.30)
    handles = [Line2D([], [], color=CONDITION_COLORS[name], lw=1.8,
                      label=CONDITION_LABELS[name]) for name in CONDITION_COLORS]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .015), ncol=4, fontsize=11)
    for idx, (key, ylabel) in enumerate(PANELS):
        ax = axes.flat[idx]
        for name, values in summaries.items():
            ax.plot(times, values[key], color=CONDITION_COLORS[name], lw=1.8, linestyle='-')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel(ylabel)
        ax.set_xlim(0, times[-1])
        ax.set_xticks(np.linspace(0, times[-1], 5))
        ax.tick_params(labelsize=10)
        values = np.concatenate([v[key] for v in summaries.values()])
        finite = values[np.isfinite(values)]
        lo, hi = (float(finite.min()), float(finite.max())) if finite.size else (0., 1.)
        margin = .06 * (hi - lo) if hi > lo else max(.05 * abs(hi), .1)
        ax.set_ylim(max(0., lo-margin), hi+margin)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=key.endswith('_tracks')))
        ax.text(0, 1.035, chr(ord('A') + idx), transform=ax.transAxes, fontsize=13, weight='bold', va='bottom')
    axes.flat[7].set_visible(False)
    fig.savefig(folder / 'conditions_analysis.pdf', bbox_inches='tight')
    fig.savefig(folder / 'conditions_analysis.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
