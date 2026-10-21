/* Client for the Python API. The form's schema comes from its OpenAPI document, and the API validates again when it receives the data: if it rejects a field, the error is shown on that field. */
import type { ValidationAdapter } from 'sveltekit-superforms/adapters';
import { schemasafe } from 'sveltekit-superforms/adapters';
import { asJsonSchema, type RequestSchema } from '#lib/schema.ts';

const API_URL = process.env.API_URL ?? 'http://127.0.0.1:8000';

type OpenApi = { paths: Record<string, { post?: { requestBody?: { content: Record<string, { schema: { $ref: string } }> } } }>; components: { schemas: Record<string, Omit<RequestSchema, 'type' | 'additionalProperties'>> } };

/* The JSON schema of the body that `POST path` expects. */
export async function requestSchema(path: string): Promise<RequestSchema> {
	const spec = (await (await fetch(`${API_URL}/openapi.json`)).json()) as OpenApi;
	const ref = spec.paths[path]?.post?.requestBody?.content['application/json'].schema.$ref;
	if (!ref) throw new Error(`La API no publica un cuerpo JSON para POST ${path}`);
	const { properties, required = [] } = spec.components.schemas[ref.split('/').pop()!];
	return { type: 'object', properties, required, additionalProperties: false };
}

/* Server-side Superforms validation from the API's schema. The fields are only known at runtime, so the adapter is typed as a generic record. */
export const validator = (schema: RequestSchema) => schemasafe(asJsonSchema(schema)) as unknown as ValidationAdapter<Record<string, unknown>>;

export type CallResult<T> = { ok: true; data: T } | { ok: false; errors: Record<string, string> };

/* POST to the API. A 422 becomes one message per field; anything else, a message for the whole form under "". */
export async function post<T>(path: string, body: unknown): Promise<CallResult<T>> {
	const res = await fetch(`${API_URL}${path}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
	if (res.ok) return { ok: true, data: (await res.json()) as T };
	if (res.status === 422) {
		const { detail } = (await res.json()) as { detail: { loc: (string | number)[]; msg: string }[] };
		return { ok: false, errors: Object.fromEntries(detail.map((d) => [String(d.loc.at(-1)), d.msg])) };
	}
	return { ok: false, errors: { '': `La API respondió ${res.status}: ${await res.text()}` } };
}
