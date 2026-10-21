/* The request schema the Python API publishes in its OpenAPI document. It is the only definition of the form's fields and validation: Superforms validates with it on the server and in the browser, and the form draws one control per property. */
import type { JSONSchema } from 'sveltekit-superforms';

export interface FieldSchema {
	type?: 'number' | 'integer' | 'string' | 'boolean';
	title?: string;
	description?: string;
	default?: unknown;
	minimum?: number;
	maximum?: number;
	format?: string;
	enum?: string[];
}

export interface RequestSchema {
	type: 'object';
	properties: Record<string, FieldSchema>;
	required: string[];
	additionalProperties: false;
}

export const asJsonSchema = (schema: RequestSchema) => schema as unknown as JSONSchema;

const num = new Intl.NumberFormat('es-ES', { maximumFractionDigits: 6 });

/* Superforms' JSON Schema validator reports the broken rule as a path ("#/properties/losses/maximum"); this turns it into a sentence with the limit taken from the same schema. Any other message (one the API wrote) is shown as it is. */
export function errorMessage(schema: RequestSchema, raw: string): string {
	const [, field, keyword] = raw.match(/^#\/properties\/([^/]+)\/(\w+)$/) ?? [];
	const rule = field ? schema.properties[field] : undefined;
	if (!rule) return raw === '#/required' ? 'Falta un campo obligatorio.' : raw;
	switch (keyword) {
		case 'minimum':
			return `Debe ser como mínimo ${num.format(rule.minimum!)}.`;
		case 'maximum':
			return `Debe ser como máximo ${num.format(rule.maximum!)}.`;
		case 'type':
			return rule.type === 'number' || rule.type === 'integer' ? 'Debe ser un número.' : 'Valor no válido.';
		case 'enum':
			return `Elige una de estas opciones: ${rule.enum!.join(', ')}.`;
		default:
			return raw;
	}
}
