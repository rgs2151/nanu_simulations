"""Seven descriptive time-series panels with one shared sweep color scale."""
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from protein_simulation.style import apply_plot_style
from observations import COLUMNS

PANELS = ('Bound motors / track', 'Motor dwell time (s)', 'Fraction of sites ON',
          'Dark-to-lit time (s)', 'Lit track count', 'Intermediate track count',
          'Dark track count')


def render(unit, config, sweeps):
    apply_plot_style()
    folder = unit / 'plots'
    folder.mkdir(exist_ok=True)
    for path in folder.iterdir():
        if path.suffix in ('.png', '.pdf', '.csv', '.json'):
            path.unlink()
    cmap = LinearSegmentedColormap.from_list('sweep_plasma', plt.get_cmap('plasma')(np.linspace(0, .80, 256)))
    for name, keys in sweeps.items():
        values = np.asarray(config['sweeps'][name])
        norm = Normalize(values.min(), values.max())
        baseline = config['variables']['number_motors' if name == 'motor' else 'cutter_concentration']
        rows = []
        for key in keys:
            with np.load(unit / 'cache' / f'{key}.npz') as data:
                rows.append(data['summary'])
        series = np.asarray(rows)
        fig, axes = plt.subplots(2, 4, figsize=(16, 7))
        fig.subplots_adjust(left=.065, right=.985, bottom=.23, top=.95, wspace=.32, hspace=.32)
        for idx, ylabel in enumerate(PANELS):
            ax = axes.flat[idx]
            for value, data in zip(values, series):
                ax.plot(data[:, 0], data[:, idx+1], color=cmap(norm(value)), lw=.65, alpha=.9)
            data = series[np.flatnonzero(values == baseline)[0]]
            ax.plot(data[:, 0], data[:, idx+1], color='black', lw=1.6, zorder=5)
            ax.set(xlabel='Time (s)', ylabel=ylabel, xlim=(0, config['run']['duration_s']))
            ax.set_xticks(np.linspace(0, config['run']['duration_s'], 5))
            ax.tick_params(labelsize=10)
            finite = series[:, :, idx+1][np.isfinite(series[:, :, idx+1])]
            lo, hi = (float(finite.min()), float(finite.max())) if finite.size else (0., 1.)
            pad = .06*(hi-lo) if hi > lo else max(.1, .05*abs(hi))
            ax.set_ylim(max(0,lo-pad), hi+pad)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=idx>=4))
            ax.text(0, 1.035, chr(65+idx), transform=ax.transAxes, fontsize=13, weight='bold', va='bottom')
        axes.flat[7].set_visible(False)
        cax = fig.add_axes([.28, .085, .46, .025])
        bar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation='horizontal')
        bar.set_label('Number of motors' if name == 'motor' else 'Cutter concentration (relative units)')
        bar.set_ticks([1,20,40,60,80,100] if name == 'motor' else [.01,.5,1,1.5,2,2.5,3])
        fig.legend(handles=[Line2D([], [], color='black', lw=1.6,
                   label=f'Baseline: {baseline:g}' + (' motors' if name=='motor' else ' relative unit'))],
                   loc='lower left', bbox_to_anchor=(.77, .052), fontsize=10)
        fig.savefig(folder/f'{name}_sweep.png', dpi=180, bbox_inches='tight')
        fig.savefig(folder/f'{name}_sweep.pdf', bbox_inches='tight')
        plt.close(fig)
        with (folder/f'{name}_sweep.csv').open('w') as handle:
            writer = csv.writer(handle)
            writer.writerow(['number_motors' if name=='motor' else 'cutter_concentration', *COLUMNS])
            for value, data in zip(values, series):
                writer.writerows([[value, *row] for row in data])
    provenance = json.loads((unit/'cache/manifest.json').read_text())
    provenance.pop('source_text')
    provenance.update(unique_simulations=len(set(sum(list(sweeps.values()), []))),
                      color_map='plasma truncated to [0, 0.80]', baseline_color='#000000',
                      panels=dict(zip('ABCDEFG', PANELS)), thresholds={'dark_below':.05,'lit_above':.40})
    (folder/'manifest.json').write_text(json.dumps(provenance, indent=2)+'\n')
