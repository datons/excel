# Casos de referencia desde Excel

Un caso es una ejecución real de la macro: entradas fijadas y salidas leídas del libro. Los tests de caracterización comparan Python con estos casos, así que su calidad decide lo que los tests garantizan.

## Con Excel instalado (macOS o Windows)

```bash
uv run scripts/run_macro.py workbooks/<libro>.xlsm <Macro> \
  --set "Parametros!B2=0.05" --set "Medidas!C10=" \
  --read "Liquidacion!A1:F20" \
  --name perdidas-5-hora-vacia --out tests/cases
```

- Trabaja sobre una copia: el libro original no cambia.
- `--set` fija una celda de entrada; vacío (`Hoja!C10=`) la borra. Los números y fechas ISO se convierten solos.
- `--read` puede repetirse para leer varias salidas.
- El caso guarda `inputs`, `outputs` y `macro_seconds`, el tiempo de la macro para la comparación del paso 5.
- La primera ejecución abre Excel por debajo y tarda (un minuto es normal). Si Excel pide habilitar macros, el usuario lo acepta una vez.

Elige los casos desde la auditoría: el caso normal del libro tal como viene, un cambio en cada parámetro y un caso por cada rareza (vacíos, ceros, límites, fechas especiales). Pon a cada uno un nombre que diga qué prueba.

## Sin Excel o en CI

- **Libro solo con fórmulas, sin macro**: la librería `formulas` calcula el libro en Python (`uv run --with formulas python`: `formulas.ExcelModel().loads(libro).finish()`, cambiar entradas y `calculate()`). Contrasta un caso con Excel antes de fiarte del resto.
- **Libro con macro y sin Excel**: usa las salidas que ya trae el libro (la última ejecución guardada) como un único caso, y pide al usuario que genere el resto en un equipo con Excel.
- **CI**: los tests nunca ejecutan Excel; leen los JSON de `tests/cases/`, que se generan una vez y se versionan.

## Cuándo regenerar

Solo cuando cambie la macro o se añada un caso. Si un caso regenerado cambia, no actualices el JSON sin más: entiende primero por qué cambió.

## Medir el tiempo con volumen

Con los pocos días de un caso de prueba, macro y Python tardan lo mismo. Para comparar de verdad, genera o pide un libro con un volumen realista (un mes, un año) y ejecuta la macro una vez con `run_macro.py`: el tiempo queda en `macro_seconds`. Muchas macros buscan fila a fila dentro de un bucle y su tiempo crece con el cuadrado de las filas: mide con un mes antes de lanzar un año.
