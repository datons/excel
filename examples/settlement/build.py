# /// script
# requires-python = ">=3.12"
# dependencies = ["xlsxwriter==3.2.5"]
# ///
"""Builds the example settlement workbook: synthetic hourly measures, prices and parameters, with formulas and, when vbaProject.bin is present, the Settle macro and its button.

Usage: uv run build.py [--year 2026 [--months N]]  →  settlement.xlsx (no macro) or settlement.xlsm (with vbaProject.bin); with --year, every hour from 1 January (settlement-year or settlement-<N>m), to compare run times.
The data is synthetic and deterministic. It deliberately includes the cases a migration must keep: a 25-hour day (end of summer time), hours without a measure, a day with no measures at all and an hour without a price.
"""

import argparse
import math
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import xlsxwriter

HERE = Path(__file__).parent
VBA_BIN = HERE / "vbaProject.bin"

LOSSES = 0.045  # loss coefficient applied to measured energy
TOLL = 12.35  # access toll, €/MWh
MADRID = ZoneInfo("Europe/Madrid")

# Day → number of hours (25 on the last Sunday of October, when summer time ends).
EXAMPLE_DAYS = {date(2026, 10, 24): 24, date(2026, 10, 25): 25, date(2026, 10, 26): 24, date(2026, 10, 27): 24}
MISSING_MEASURES = {(date(2026, 10, 26), 9), (date(2026, 10, 26), 10)}
DAY_WITHOUT_MEASURES = date(2026, 10, 27)
MISSING_PRICE = (date(2026, 10, 26), 13)


def measure_kwh(day: date, hour: int) -> float:
    """A solar-shaped profile with a small daily variation, in kWh."""
    sun = max(0.0, math.sin(math.pi * (hour - 7) / 12))
    return round(850 * sun * (1 + 0.03 * (day.day % 5)) + 4.2, 3)


def price(day: date, hour: int) -> float:
    """Day-ahead style price, €/MWh: cheap at noon, expensive in the evening."""
    return round(78 + 22 * math.cos(math.pi * (hour - 20) / 12) - 0.7 * (day.day % 3), 2)


def hours_in(day: date, tz: ZoneInfo = MADRID) -> int:
    """23, 24 or 25: the length of the local day, which changes when summer time starts or ends."""
    start = datetime(day.year, day.month, day.day, tzinfo=tz)
    end = datetime.combine(day + timedelta(days=1), datetime.min.time(), tzinfo=tz)
    # Subtracting two times of the same zone gives wall-clock time (always 24 h); in UTC it gives the real length.
    return round((end.astimezone(UTC) - start.astimezone(UTC)).total_seconds() / 3600)


def year_days(year: int, months: int = 12) -> dict[date, int]:
    """Every day from 1 January for `months` months, with its real number of hours."""
    first = date(year, 1, 1)
    end = date(year + 1, 1, 1) if months >= 12 else date(year, months + 1, 1)
    return {first + timedelta(days=i): hours_in(first + timedelta(days=i)) for i in range((end - first).days)}


def build(days: dict[date, int] = EXAMPLE_DAYS, name: str = "settlement") -> Path:
    with_macro = VBA_BIN.exists()
    out = HERE / (f"{name}.xlsm" if with_macro else f"{name}.xlsx")
    wb = xlsxwriter.Workbook(out)
    bold = wb.add_format({"bold": True})
    date_fmt = wb.add_format({"num_format": "yyyy-mm-dd"})
    pct = wb.add_format({"num_format": "0.0%"})

    params = wb.add_worksheet("Parametros")
    params.write_row(0, 0, ["Parámetro", "Valor", "Nota"], bold)
    params.write_row(1, 0, ["Pérdidas"])
    params.write_number(1, 1, LOSSES, pct)
    params.write(1, 2, "Coeficiente que se suma a la energía medida")
    params.write_row(2, 0, ["Peaje (€/MWh)", TOLL, "Se suma al precio de cada hora"])
    params.write(3, 0, "Pérdidas en %")
    params.write_formula(3, 1, "=B2*100", None, LOSSES * 100)
    params.set_column(0, 0, 18)
    params.set_column(2, 2, 44)

    measures = wb.add_worksheet("Medidas")
    measures.write_row(0, 0, ["Fecha", "Hora", "Energia_kWh", "Energia_MWh"], bold)
    prices = wb.add_worksheet("Precios")
    prices.write_row(0, 0, ["Fecha", "Hora", "Precio_EUR_MWh"], bold)
    row = prow = 1
    for day, hours in days.items():
        for hour in range(1, hours + 1):
            measures.write_datetime(row, 0, day, date_fmt)
            measures.write_number(row, 1, hour)
            if day != DAY_WITHOUT_MEASURES and (day, hour) not in MISSING_MEASURES:
                kwh = measure_kwh(day, hour)
                measures.write_number(row, 2, kwh)
                measures.write_formula(row, 3, f"=C{row + 1}/1000", None, kwh / 1000)
            else:
                # An empty measure: the MWh formula still shows 0, a trap for anyone who reads column D instead of C.
                measures.write_formula(row, 3, f"=C{row + 1}/1000", None, 0)
            row += 1
            if (day, hour) != MISSING_PRICE:
                prices.write_datetime(prow, 0, day, date_fmt)
                prices.write_number(prow, 1, hour)
                prices.write_number(prow, 2, price(day, hour))
                prow += 1
    for ws in (measures, prices):
        ws.set_column(0, 0, 12)
        ws.set_column(1, 3, 14)

    result = wb.add_worksheet("Liquidacion")
    result.write_row(0, 0, ["Fecha", "Horas", "Horas_estimadas", "Energia_MWh", "Aviso", "Importe_EUR"], bold)
    result.set_column(0, 5, 16)
    if with_macro:
        wb.add_vba_project(str(VBA_BIN))
        result.insert_button("H2", {"macro": "Settle", "caption": "Liquidar", "width": 120, "height": 30})
    result.activate()

    wb.close()
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, help="Build hours from 1 January of this year instead of the four example days")
    parser.add_argument("--months", type=int, default=12, help="With --year, how many months (default 12); the file is settlement-<months>m")
    args = parser.parse_args()
    print(build(year_days(args.year, args.months), "settlement-year" if args.months >= 12 else f"settlement-{args.months}m") if args.year else build())
