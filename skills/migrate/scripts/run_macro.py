# /// script
# requires-python = ">=3.12"
# dependencies = ["xlwings>=0.33"]
# ///
"""Runs a workbook's macro on a copy, with the inputs you set, and prints the output ranges as JSON: one reference case for the characterization tests.

Needs Excel installed (macOS or Windows); xlwings drives it. The original workbook is never modified.

Usage:
  uv run run_macro.py <workbook> <macro> --read "Sheet!A1:F10" [--read ...] [--set "Sheet!B2=0.05" ...] [--name case] [--out tests/cases]
Values in --set are parsed as numbers when they look like numbers, as ISO dates when they look like dates, and as text otherwise; an empty value clears the cell.
"""

import argparse
import json
import shutil
import sys
import tempfile
import time
from datetime import date, datetime
from pathlib import Path


def parse_value(text: str):
    if text == "":
        return None
    for cast in (int, float):
        try:
            return cast(text)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return text


def to_json(value):
    if isinstance(value, (datetime, date)):
        return value.date().isoformat() if isinstance(value, datetime) and value.time() == datetime.min.time() else value.isoformat()
    if isinstance(value, list):
        return [to_json(v) for v in value]
    return value


def split_address(address: str) -> tuple[str, str]:
    sheet, _, cells = address.rpartition("!")
    if not sheet:
        sys.exit(f"Address without sheet: {address} (use Sheet!A1)")
    return sheet.strip("'"), cells


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("workbook", type=Path)
    p.add_argument("macro")
    p.add_argument("--read", action="append", required=True, help="Output range, Sheet!A1:F10")
    p.add_argument("--set", action="append", default=[], help="Input cell, Sheet!B2=value")
    p.add_argument("--name", help="Case name; with --out, the file is <out>/<name>.json")
    p.add_argument("--out", type=Path, help="Folder for the case file; without it the case is printed")
    a = p.parse_args()

    import xlwings as xw

    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / a.workbook.name
        shutil.copy2(a.workbook, copy)
        app = xw.App(visible=False, add_book=False)
        try:
            wb = app.books.open(str(copy))
            inputs = {}
            for item in a.set:
                address, _, raw = item.partition("=")
                sheet, cells = split_address(address)
                wb.sheets[sheet].range(cells).value = parse_value(raw)
                inputs[address] = raw
            started = time.perf_counter()
            wb.macro(a.macro)()
            seconds = time.perf_counter() - started
            outputs = {}
            for address in a.read:
                sheet, cells = split_address(address)
                outputs[address] = to_json(wb.sheets[sheet].range(cells).options(ndim=2).value)
            wb.close()
        finally:
            app.quit()

    case = {"workbook": a.workbook.name, "macro": a.macro, "inputs": inputs, "outputs": outputs, "macro_seconds": round(seconds, 3)}
    text = json.dumps(case, ensure_ascii=False, indent=2)
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        target = a.out / f"{a.name or 'case'}.json"
        target.write_text(text + "\n")
        print(target)
    else:
        print(text)


if __name__ == "__main__":
    main()
