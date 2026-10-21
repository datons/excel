"""HTTP API for the settlement process: the form and any other client call it, and validation lives only in the Pydantic models below.

Run with `uv run api` (http://127.0.0.1:8000, docs at /docs). The workbook comes from SETTLEMENT_WORKBOOK or defaults to the example one.
"""

import os
from datetime import date
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from settlement_demo.settlement import Inputs, read_inputs, settle

WORKBOOK = Path(os.environ.get("SETTLEMENT_WORKBOOK", Path(__file__).parents[3] / "settlement.xlsx"))

app = FastAPI(title="Liquidación de una instalación")


class SettleRequest(BaseModel):
    losses: float = Field(0.045, ge=0, le=0.2, title="Pérdidas", description="Coeficiente que se suma a la energía medida (0,045 = 4,5 %).")
    toll: float = Field(12.35, ge=0, le=100, title="Peaje (€/MWh)", description="Se suma al precio de cada hora.")


class DayOut(BaseModel):
    day: date
    hours: int
    estimated_hours: int
    energy_mwh: float
    amount_eur: float
    without_measures: bool
    missing_prices: list[int]


class SettleResponse(BaseModel):
    days: list[DayOut]
    total_eur: float


@app.post("/settle", response_model=SettleResponse)
def settle_endpoint(request: SettleRequest) -> SettleResponse:
    base = read_inputs(WORKBOOK)
    results = settle(Inputs(request.losses, request.toll, base.measures, base.prices))
    return SettleResponse(days=[DayOut(**vars(r)) for r in results], total_eur=round(sum(r.amount_eur for r in results), 2))


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "8000")))
