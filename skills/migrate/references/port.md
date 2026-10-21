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

## Corregir un comportamiento, con el test primero

Cuando el responsable del proceso decide corregir una rareza (por ejemplo, que una hora sin precio deje de valer 0 en silencio):

1. Escribe el test del comportamiento nuevo y comprueba que **falla**.
2. Cambia el código lo mínimo para que pase.
3. Ejecuta todos los tests: los demás casos deben seguir en verde. El test de caracterización de esa rareza cambia a la vez y en el mismo commit, con una línea que diga quién lo decidió.
4. Anota en `docs/<process>.md` la diferencia con la macro y la fecha de la decisión.

Desde ese momento Python y la macro ya no dan lo mismo en ese caso, a propósito y por escrito.

## Otra fuente de datos, el mismo cálculo

La separación entre `read_inputs` y la función pura permite cambiar de dónde salen los datos (otro libro, un CSV, una base de datos) sin tocar el cálculo ni sus tests: se escribe otra función de lectura que devuelve el mismo `Inputs`.

- Comprueba la **granularidad** de la nueva fuente: si la macro trabaja por horas y la fuente da cuartos de hora, decide con el usuario si se agrega a horas o se calcula por periodo. Si el cálculo trata el periodo como una clave (hora 1–24, cuarto 1–96), suele servir tal cual con periodos más finos; dilo y compruébalo.
- Comprueba **unidades** (kWh frente a MWh) y **huecos** (filas que faltan frente a valores nulos) antes de comparar resultados.
- Si la fuente es un lakehouse de Fabric y está instalado el plugin `fabric`, usa `/fabric:lakehouse` para la consulta y su conexión.
