# Data

`data/` is the canonical location for organized analysis-ready research inputs. No research data has been supplied or generated.

## Structure

- Keep each future dataset in a descriptively named subfolder under `data/`.
- Before analysis, document actual filenames, table/array layout, record hierarchy, variable definitions, physical units, and provenance here.
- Specify identifiers and exact alignment rules between trajectories, time samples, conditions, and metadata when those inputs exist; no alignment contract has been chosen yet.
- Specify missing-data and exclusion rules for each dataset before use; none are currently defined.
- Unit-generated intermediate simulation outputs belong in the owning unit's `cache/`; derived tables and figures belong in its `plots/`.
- Data files are ignored by Git. Do not commit research data without explicit authorization.

## Inventory

| Name | Records | Notes |
| --- | ---: | --- |
| Research inputs | 0 | No datasets supplied; only this documentation is present. |

The environment-inventory diagnostic reads installed software metadata, not research inputs.
