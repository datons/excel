"""Characterization tests: the Python port must reproduce what the macro produced in Excel (expected/settlement.csv)."""

import csv
from datetime import date
from pathlib import Path

import pytest
from settlement_demo.settlement import read_inputs, settle

EXAMPLE = Path(__file__).parents[2]
WORKBOOK = EXAMPLE / "settlement.xlsx"
EXPECTED = EXAMPLE / "expected" / "settlement.csv"


def expected_days() -> list[dict]:
    with EXPECTED.open() as f:
        return [row for row in csv.DictReader(f) if row["Fecha"] != "Total"]


@pytest.fixture(scope="module")
def results():
    return {r.day: r for r in settle(read_inputs(WORKBOOK))}


@pytest.mark.parametrize("row", expected_days(), ids=lambda r: r["Fecha"])
def test_matches_macro(results, row):
    got = results[date.fromisoformat(row["Fecha"])]
    assert got.hours == int(row["Horas"])
    assert got.estimated_hours == int(row["Horas_estimadas"])
    assert got.energy_mwh == pytest.approx(float(row["Energia_MWh"]), abs=1e-9)
    assert got.amount_eur == pytest.approx(float(row["Importe_EUR"]), abs=0.005)
    assert got.without_measures == (row["Aviso"] == "sin medidas")


def test_total_matches_macro(results):
    with EXPECTED.open() as f:
        total = next(float(r["Importe_EUR"]) for r in csv.DictReader(f) if r["Fecha"] == "Total")
    assert sum(r.amount_eur for r in results.values()) == pytest.approx(total, abs=0.005)


def test_end_of_summer_time_has_25_hours(results):
    assert results[date(2026, 10, 25)].hours == 25


def test_missing_price_is_settled_at_zero_and_reported(results):
    # The macro settles it at 0 without a word. The port keeps the number (so it still matches) and exposes the hour; deciding to fail instead is a change to agree with the owner of the process.
    assert results[date(2026, 10, 26)].missing_prices == [13]
