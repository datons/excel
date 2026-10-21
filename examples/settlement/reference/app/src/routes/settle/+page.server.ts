import { fail } from '@sveltejs/kit';
import { message, setError, superValidate } from 'sveltekit-superforms';
import { post, requestSchema, validator } from '#lib/server/api.ts';

type Day = { day: string; hours: number; estimated_hours: number; energy_mwh: number; amount_eur: number; without_measures: boolean; missing_prices: number[] };
export type Settlement = { days: Day[]; total_eur: number };

export const load = async () => {
	const schema = await requestSchema('/settle');
	return { schema, form: await superValidate(validator(schema)) };
};

export const actions = {
	default: async ({ request }) => {
		const form = await superValidate(await request.formData(), validator(await requestSchema('/settle')));
		if (!form.valid) return fail(400, { form });
		const result = await post<Settlement>('/settle', form.data);
		if (!result.ok) {
			for (const [field, error] of Object.entries(result.errors)) setError(form, field as '', error);
			return fail(422, { form });
		}
		return message(form, result.data);
	}
};
