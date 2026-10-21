# excel

Plugin for Claude Code and Codex that interprets Excel workbooks and their VBA macros and migrates them to verified Python. The macro stays the reference: the Python version must reproduce what it does today, proven by characterization tests built from real Excel runs, before anything is improved.

The skill `/excel:migrate` walks through:

1. **Audit**: `scripts/describe.py` dumps sheets, formulas and the full VBA code; the agent writes what the process does (inputs, outputs, rules, edge cases, quirks) and a plan the user confirms.
2. **Reference cases**: `scripts/run_macro.py` runs the macro on a copy of the workbook through Excel (xlwings, macOS or Windows) with the inputs you choose, and saves the outputs as JSON.
3. **Port** to a uv package, keeping every quirk documented.
4. **Characterization tests** with pytest against the reference cases, with explicit tolerances, and a rule in the project's `AGENTS.md` to run them after every change.
5. **Comparison** of run time, maintainability and the risks the macro hid.
6. **API and form** (optional): FastAPI with a Pydantic model as the single definition of the inputs, and a SvelteKit form with shadcn-svelte that validates with that same schema through Superforms.

## Install

Claude Code:

```
/plugin marketplace add datons/excel
/plugin install excel@datons-excel
```

Codex:

```bash
codex plugin marketplace add datons/excel
codex plugin add excel@datons-excel
```

## Requirements

- `uv` for Python; Bun for the web form.
- Excel (macOS or Windows) to extract reference cases from a macro. Tests never need Excel: they read the saved cases. Formula-only workbooks can be computed without Excel (see `skills/migrate/references/cases.md`).

## Worked example

[`examples/settlement/`](examples/settlement) is a synthetic settlement workbook for one energy installation, with a VBA macro and the full migration: reference port, characterization tests, API and form. It is what the skill should lead you to build, and CI checks it on every change.

## Development

```bash
cd examples/settlement/reference && uv run --python 3.12 pytest -q
cd app && bun install && bun run check
uvx ruff check skills examples
claude plugin validate .
```

No client workbooks, macros or data belong in this repository: examples are synthetic.
