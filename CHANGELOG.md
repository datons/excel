# Changelog

## 0.4.0

- Once the user confirms the proposal and asks to implement it, `migrate` runs steps 2 to 5 in one go (and 6 when asked or proposed), stopping only for a reference case that does not match or a rule it cannot understand, and ends with one summary: tests, Python total against the macro, deliberate quirks and how to start the API and the form.

## 0.3.0

- Step 1 of `migrate` ends in `docs/<process>-proposal.html`: a self-contained page (inline CSS and SVG, no external libraries) with the project tree, the data model, the process diagram, the reference cases with their expected results and, if the web step is requested, the form mockup. The user confirms the migration on that page before any code is written.

## 0.2.0

- `references/port.md`: fixing a behaviour test first (the characterization test changes in the same commit, with the decision written down), and a new data source with the same calculation (granularity, units, gaps; `/fabric:lakehouse` for Fabric lakehouses).
- `references/cases.md`: measuring run time with a realistic volume, a month before a year, because row-by-row lookups grow with the square of the rows.
- Example: `build.py --year --months` builds whole months or a year with the real summer-time days; `settlement-1m.xlsm` (January) for timing.

## 0.1.0

- Skill `migrate`: audit, reference cases from Excel, port, characterization tests, comparison, and an optional API and form.
- `scripts/describe.py` (sheets, formulas, VBA) and `scripts/run_macro.py` (runs a macro on a copy through xlwings and saves a reference case).
- Form templates: SvelteKit with shadcn-svelte, validated by Superforms with the API's JSON Schema.
- Worked example `examples/settlement/`: synthetic workbook and macro, reference port with characterization tests, FastAPI and form.
