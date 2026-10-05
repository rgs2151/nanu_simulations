# Plot style

Use this style for all new and revised plots. It supersedes the earlier serif, endpoint-only, trimmed-spine style. Existing figures are not regenerated unless requested.

- Use **Arial** for all text, including titles, labels, ticks, legends, and math labels.
- Start from ordinary Matplotlib defaults, following the professor’s notebook: standard attached axes/spines, white background, and several readable tick values on each axis.
- Use solid lines. Do not introduce different dash patterns to distinguish conditions.
- Use the fixed saturated condition colors from `protein_simulation/style.py`, also documented in `DECISIONS.md`.
- Keep axis labels short and include physical units where applicable.
- Use a proper shared legend. Keep subplot titles when useful; do not add an overall figure title unless requested.
- Do not put methodological commentary, threshold explanations, caveats, or footnotes inside the figure. Put them in the owning unit README.
- Do not smooth or change data merely to make curves look cleaner.
- Save PNG previews and vector PDFs where appropriate.

Initialize new plotting code with:

```python
from protein_simulation.style import apply_plot_style
apply_plot_style()
```

Routine visualization edits use existing caches. Do not rerun simulations or run/add tests for cosmetic plotting changes. Reserve tests for explicitly requested or substantively important engine/scientific changes.
