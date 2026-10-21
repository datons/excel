"""The API returns the same settlement as the function, and rejects out-of-range inputs before computing anything."""

from fastapi.testclient import TestClient

from settlement_demo.api import app

client = TestClient(app)


def test_default_parameters_reproduce_the_macro_total():
    body = client.post("/settle", json={}).json()
    assert len(body["days"]) == 4
    assert abs(body["total_eur"] - 1734.12) < 0.005


def test_out_of_range_losses_are_rejected_with_the_field_name():
    response = client.post("/settle", json={"losses": 0.5})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "losses"]


def test_schema_carries_the_validation_the_form_uses():
    schema = client.get("/openapi.json").json()["components"]["schemas"]["SettleRequest"]["properties"]["losses"]
    assert (schema["minimum"], schema["maximum"], schema["title"]) == (0, 0.2, "Pérdidas")
