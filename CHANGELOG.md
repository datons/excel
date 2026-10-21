# Changelog

## 0.2.0

- `references/port.md`: fixing a behaviour test first (the characterization test changes in the same commit, with the decision written down), and a new data source with the same calculation (granularity, units, gaps; `/fabric:lakehouse` for Fabric lakehouses).
- `references/cases.md`: measuring run time with a realistic volume, a month before a year, because row-by-row lookups grow with the square of the rows.
- Example: `build.py --year --months` builds whole months or a year with the real summer-time days; `settlement-1m.xlsm` (January) for timing.

## 0.1.0

- Skill `migrate`: audit, reference cases from Excel, port, characterization tests, comparison, and an optional API and form.
- `scripts/describe.py` (sheets, formulas, VBA) and `scripts/run_macro.py` (runs a macro on a copy through xlwings and saves a reference case).
- Form templates: SvelteKit with shadcn-svelte, validated by Superforms with the API's JSON Schema.
- Worked example `examples/settlement/`: synthetic workbook and macro, reference port with characterization tests, FastAPI and form.
