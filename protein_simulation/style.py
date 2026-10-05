"""Stable condition colors for comparative analysis figures."""
CONDITION_COLORS = {
    "baseline": "#000000",
    "cutter": "#2674D9",
    "motor": "#219447",
    "permanent": "#8B3FC7",
}
CONDITION_LABELS = {
    "baseline": "Baseline",
    "cutter": "Cutter ignores protection",
    "motor": "Capped motor run",
    "permanent": "Scattered permanent sites",
}


def apply_plot_style():
    """Arial and ordinary Matplotlib axes, following the reference notebook."""
    import matplotlib.pyplot as plt
    plt.style.use("default")
    plt.rcParams.update({
        "font.family": "Arial", "font.sans-serif": ["Arial"],
        "mathtext.fontset": "custom", "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold",
        "axes.labelsize": 12, "axes.titlesize": 13,
        "xtick.labelsize": 11, "ytick.labelsize": 11,
        "lines.linestyle": "-", "lines.linewidth": 1.8,
        "legend.frameon": False, "figure.facecolor": "white",
        "savefig.facecolor": "white", "pdf.fonttype": 42,
    })
