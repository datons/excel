# Portar y fijar con tests de caracterización

## El módulo

```python
# src/<project>/<process>.py
@dataclass(frozen=True)
class Inputs: ...          # lo que la macro lee, ya tipado

def read_inputs(path: Path) -> Inputs: ...   # openpyxl, load_workbook(path, data_only=True)
def run(inputs: Inputs) -> Result: ...        # puro: sin Excel, sin ficheros
```

- Lee el dato original, nunca una columna calculada (ver «Celdas vacías» en `references/audit.md`).
- Separa la lectura del cálculo: los tests y la API llaman a la función pura.
- Funciones pequeñas con el nombre de la regla de negocio que implementan.
- Cada rareza reproducida lleva un comentario que la explica y su entrada en `docs/<process>.md`.
- Lo que la macro hacía en silencio (valores que faltan, búsquedas fallidas) se mantiene en el número y se expone en el resultado como aviso.
- Dependencias con `uv add`: `openpyxl` siempre; `pytest` como dependencia de desarrollo (`uv add --dev pytest`).

## Los tests

```python
# tests/test_<process>.py
CASES = sorted(Path(__file__).parent.joinpath("cases").glob("*.json"))

@pytest.mark.parametrize("case", CASES, ids=lambda p: p.stem)
def test_matches_excel(case): ...   # aplica case["inputs"] al libro, ejecuta run(), compara con case["outputs"]
```

- **Tolerancias explícitas y justificadas**: importes a medio céntimo (`abs=0.005`), energías y ratios a `1e-9`. Nunca `approx` sin tolerancia indicada.
- **Un test por rareza** con un nombre que la describa (`test_missing_price_is_settled_at_zero_and_reported`).
- **Ningún test ejecuta Excel**: leen los casos versionados.
- Si un caso no cuadra, el fallo es del port hasta que se demuestre lo contrario. Si resulta ser un error de la macro, se documenta y se decide con el usuario; el test cambia solo con esa decisión.

## La regla en AGENTS.md

Añade al `AGENTS.md` del proyecto (créalo si no existe):

> Tras cada cambio en `src/<project>/<process>.py`, ejecuta `uv run pytest`. Un cambio de comportamiento acordado con el responsable del proceso lleva su test nuevo y su nota en `docs/<process>.md`.
