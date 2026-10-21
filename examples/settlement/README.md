# Example: settlement of one installation

A synthetic workbook with a VBA macro, and its migration to Python. Nothing here comes from a real client.

| File | What it is |
|---|---|
| `macro/Settlement.bas` | The macro source (ASCII, see below) |
| `vbaProject.bin` | The macro compiled by Excel, embedded by `build.py` |
| `build.py` | Builds `settlement.xlsx` (no macro) and `settlement.xlsm` (with the macro and a Liquidar button); `--year 2026 [--months N]` builds every hour from 1 January, with the real 23- and 25-hour days, to compare run times |
| `settlement-1m.xlsm` | January 2026 (744 hours), to measure the macro against Python |
| `expected/settlement.csv` | The macro's own output, run in Excel |
| `reference/` | The migration: Python port, characterization tests, FastAPI and a SvelteKit form |

The data includes what a migration must keep: a 25-hour day (end of summer time), hours without a measure, a day with no measures at all, and an hour without a price that the macro silently settles at 0.

## Changing the macro

`vbaProject.bin` can only be produced by Excel. After editing `macro/Settlement.bas`:

1. `uv run build.py` and open `settlement.xlsx` in Excel.
2. Tools → Macro → Visual Basic Editor → File → Import File… → `macro/Settlement.bas`.
3. Save As → Excel Macro-Enabled Workbook (`.xlsm`) in `macro/`.
4. `unzip -p macro/<saved>.xlsm xl/vbaProject.bin > vbaProject.bin && uv run build.py`.
5. Regenerate `expected/settlement.csv` by running the macro (`../../skills/migrate/scripts/run_macro.py`) and check the reference tests still pass.

Keep `Settlement.bas` ASCII: the VBA editor reads it in the local code page (MacRoman on Mac, cp1252 on Windows) and garbles any accent.
