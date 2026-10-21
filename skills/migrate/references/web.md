# API y formulario web

Una sola definición de las entradas: el modelo Pydantic de la API. El formulario la lee del `openapi.json` de la API, Superforms valida con ella en el navegador y en el servidor de SvelteKit, y la API vuelve a validar al recibir. Nunca escribas una regla de validación en el formulario.

## La API

```python
# src/<project>/api.py
class <Process>Request(BaseModel):
    losses: float = Field(0.045, ge=0, le=0.2, title="Pérdidas", description="…")
```

- `title` es la etiqueta del campo y `description` su ayuda; `ge`, `le`, `Literal[...]` y los tipos son su validación.
- Un endpoint `POST /<process>` que llama a la función pura del módulo y devuelve un modelo de respuesta.
- Comando en `pyproject.toml`: `[project.scripts] api = "<project>.api:main"`, con `uvicorn.run` en `main`. Se arranca con `uv run api` (http://127.0.0.1:8000, documentación en `/docs`).
- Dependencias: `uv add fastapi uvicorn` y, para sus tests, `uv add --dev httpx`.
- Tests: la API reproduce el total de un caso, rechaza un valor fuera de rango con el nombre del campo, y su esquema publica los límites que usa el formulario.

## El formulario

SvelteKit con Bun, shadcn-svelte para los componentes y Superforms con el adaptador `schemasafe` para validar con el JSON Schema. Si está disponible la skill oficial de shadcn-svelte, úsala para cualquier componente nuevo.

```bash
bunx sv create app --template minimal --types ts --no-add-ons --install bun
cd app
bunx sv add "tailwindcss=plugins:none" --install bun
bunx --bun shadcn-svelte@latest init --base-color neutral --css src/routes/layout.css \
  --lib-alias '#lib' --components-alias '#lib/components' --utils-alias '#lib/utils' \
  --hooks-alias '#lib/hooks' --ui-alias '#lib/components/ui'
bunx --bun shadcn-svelte@latest add form field input button table card select checkbox alert --yes
bun add -d sveltekit-superforms @exodus/schemasafe
```

- `init` pregunta por un preset: el primero de la lista vale. Con SvelteKit 2 los alias son `$lib` en vez de `#lib`.
- Copia `templates/app/src/lib/` (`schema.ts`, `SchemaForm.svelte`, `server/api.ts`) y crea la ruta del proceso como en el ejemplo (`examples/settlement/reference/app/src/routes/settle/`): `load` pide el esquema y crea el formulario con `superValidate(validator(schema))`; la acción valida, llama a la API y devuelve el resultado con `message`.
- La URL de la API sale de `API_URL` (por defecto `http://127.0.0.1:8000`). Para desarrollar: `uv run api` en una terminal y `API_URL=… bun run dev` en otra.
- Los errores de validación llegan como ruta de la regla (`#/properties/losses/maximum`); `errorMessage()` de `schema.ts` los convierte en frases con los límites del esquema.

## Comprobación

Con los dos servidores en marcha: el formulario muestra un campo por cada entrada de la API con su etiqueta y sus límites; un valor fuera de rango se marca en el campo sin llegar a la API; un envío válido muestra el mismo total que el test de caracterización.
