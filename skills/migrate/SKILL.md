---
name: migrate
description: "Interpreta macros VBA y libros de Excel y los migra a Python verificado: documenta qué hace el proceso, saca casos de referencia ejecutando la macro en Excel, porta la lógica a un paquete uv, fija su comportamiento con tests de caracterización pytest, compara las dos versiones y, si se pide, la expone con una API FastAPI y un formulario SvelteKit con shadcn-svelte. Use when the user says 'qué hace esta macro', 'documenta este Excel', 'migra esta macro a Python', 'pasa este Excel a Python', 'tests para comparar con la macro', 'haz un formulario para este cálculo', 'explain this VBA', 'convert this spreadsheet to Python'."
argument-hint: "[libro de Excel o macro]"
---

# De la macro de Excel a Python verificado

El objetivo es un proceso en Python que dé **los mismos resultados** que el libro de Excel, con tests que lo demuestren, antes de mejorar nada. Excel es la referencia: lo que hace hoy la macro, incluidos sus errores, se fija primero y se corrige después, como decisión explícita del responsable del proceso.

Las rutas `scripts/...`, `references/...` y `templates/...` son relativas a la carpeta de esta skill. Lee cada referencia cuando llegues a su paso.

| Paso | Referencia |
|---|---|
| 1. Auditar el libro y la macro, y la propuesta | `references/audit.md` |
| 2. Casos de referencia desde Excel | `references/cases.md` |
| 3–4. Portar y fijar con tests | `references/port.md` |
| 6. API y formulario web | `references/web.md` |

## Dónde va cada cosa

Trabaja en la carpeta del proyecto, nunca en una carpeta temporal. Si ya hay un proyecto (`pyproject.toml`, `src/`, `AGENTS.md`), úsalo tal cual y añade solo estas piezas; si la carpeta está vacía, crea el paquete con `uv init --lib --name <project> --python 3.12 --vcs none` y un `AGENTS.md`.

```
workbooks/<libro>.xlsm          el libro original, sin modificar
docs/<process>.md               qué hace el proceso, en el idioma del usuario
docs/<process>-proposal.html    la propuesta que confirma el usuario (paso 1)
src/<project>/<process>.py      el proceso en Python
tests/cases/*.json              casos de referencia sacados de Excel
tests/test_<process>.py         tests de caracterización
src/<project>/api.py            API (paso 6, opcional)
app/                            formulario SvelteKit (paso 6, opcional)
```

Un proyecto con varios procesos tiene una sola API y un solo formulario: si ya existen `src/<project>/api.py` y `app/`, añade el endpoint del proceso nuevo a esa API y su ruta a esa app; no crees otras.

Nombres de ficheros, funciones y comandos en inglés; documentación y mensajes, en el idioma del usuario. No subas a ningún repositorio público libros, datos ni macros de un cliente.

## 1. Audita antes de escribir código

Ejecuta `uv run scripts/describe.py <libro>`: hojas, cabeceras, fórmulas y el código VBA completo. Con eso escribe `docs/<process>.md` (entradas, salidas, reglas, casos especiales y rarezas) y la propuesta de migración en `docs/<process>-proposal.html`: un único fichero que se abre sin conexión, con el árbol del proyecto, el modelo de datos, el diagrama del proceso y los casos de referencia con su resultado esperado (detalle en `references/audit.md`). Ábrela en el navegador. **Espera a que el usuario la confirme antes de escribir código**: es mucho más barato discutir aquí que con el código hecho, y corrige la propuesta con lo que te diga. Si la macro es grande, trocea el plan por módulos siguiendo sus dependencias y migra de uno en uno.

## Con la propuesta confirmada, de un tirón

Cuando el usuario confirme la propuesta y pida implementarla («implementa el plan aprobado», «hazlo todo hasta el formulario»), haz los pasos 2 a 5 seguidos, y el 6 si lo pide o la propuesta lo incluye. No pares entre pasos para pedir permiso: para solo si un caso de referencia no cuadra y no sabes por qué, o si una regla de la macro no se entiende. Al terminar, resume en un mensaje: los tests y su resultado, el total de Python frente al de la macro, las rarezas que se mantienen a propósito y, si hay web, los dos comandos para arrancar la API y el formulario.

## 2. Saca casos de referencia de Excel

Con Excel instalado, `uv run scripts/run_macro.py` ejecuta la macro sobre una copia con las entradas que elijas y guarda la salida en `tests/cases/`. Incluye los casos normales y los límite que encontraste en la auditoría. Sin Excel, o si el libro solo tiene fórmulas, sigue las alternativas de `references/cases.md`.

## 3. Porta el proceso

Una función que lee las entradas del libro y otra pura que calcula, en `src/<project>/<process>.py`. Reproduce también las rarezas (redondeos, valores vacíos, búsquedas que devuelven 0): cada una lleva un comentario y aparece en `docs/<process>.md`.

## 4. Fija el comportamiento con tests de caracterización

`tests/test_<process>.py` compara cada caso de `tests/cases/` con tolerancias explícitas. Añade un test por cada rareza documentada. Después añade al `AGENTS.md` del proyecto esta regla: «Tras cada cambio en `src/<project>/<process>.py`, ejecuta `uv run pytest`; un cambio de comportamiento acordado lleva su test nuevo».

## 5. Compara

En `docs/<process>.md`, una tabla con la macro frente a Python: tiempo de ejecución (`macro_seconds` de los casos frente al test), facilidad de mantenimiento y riesgos encontrados (lo que la macro hacía en silencio). Las correcciones se proponen aquí y se aplican solo si el usuario las acepta, cada una con su test.

## 6. Expón el proceso (si se pide)

Una API FastAPI cuyo modelo Pydantic es la única definición de las entradas, y un formulario SvelteKit con shadcn-svelte que valida con ese mismo esquema. Sigue `references/web.md` y copia `templates/app/`.

## Límites

- No cambies el libro original: `run_macro.py` trabaja siempre sobre una copia.
- No digas que Python reproduce la macro sin haber ejecutado los tests contra casos sacados de Excel.
- Si una regla de la macro no se entiende, pregúntala; no la inventes.
