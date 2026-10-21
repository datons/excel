<script lang="ts">
	/* One shadcn-svelte control per property of the API's request schema. Labels, help, limits and errors come from the schema and from Superforms, so this component never repeats a validation rule. */
	import type { SuperForm } from 'sveltekit-superforms';
	import * as Form from '#lib/components/ui/form/index.ts';
	import { Input } from '#lib/components/ui/input/index.ts';
	import { Checkbox } from '#lib/components/ui/checkbox/index.ts';
	import * as Select from '#lib/components/ui/select/index.ts';
	import { errorMessage, type FieldSchema, type RequestSchema } from '#lib/schema.ts';

	interface Props {
		form: SuperForm<Record<string, unknown>>;
		schema: RequestSchema;
		submit?: string;
	}

	let { form, schema, submit = 'Calcular' }: Props = $props();
	const { form: data, errors, enhance, allErrors, submitting } = $derived(form);
	const fields = $derived(Object.entries(schema.properties) as [string, FieldSchema][]);
</script>

<form method="POST" use:enhance class="grid max-w-md gap-6">
	{#each fields as [name, field] (name)}
		<Form.Field {form} {name}>
			<Form.Control>
				{#snippet children({ props })}
					<Form.Label>{field.title ?? name}</Form.Label>
					{#if field.enum}
						<Select.Root type="single" bind:value={$data[name] as string} name={props.name}>
							<Select.Trigger {...props}>{$data[name] ?? 'Elige una opción'}</Select.Trigger>
							<Select.Content>
								{#each field.enum as option (option)}<Select.Item value={option}>{option}</Select.Item>{/each}
							</Select.Content>
						</Select.Root>
					{:else if field.type === 'boolean'}
						<Checkbox {...props} bind:checked={$data[name] as boolean} />
					{:else if field.type === 'number' || field.type === 'integer'}
						<Input {...props} type="number" step={field.type === 'integer' ? 1 : 'any'} min={field.minimum} max={field.maximum} bind:value={$data[name] as number} />
					{:else}
						<Input {...props} type={field.format === 'date' ? 'date' : 'text'} bind:value={$data[name] as string} />
					{/if}
				{/snippet}
			</Form.Control>
			{#if field.description}<Form.Description>{field.description}</Form.Description>{/if}
			{#each (($errors as Record<string, string[] | undefined>)[name] ?? []) as error (error)}
				<p class="text-destructive text-sm">{errorMessage(schema, error)}</p>
			{/each}
		</Form.Field>
	{/each}
	{#each $allErrors.filter((e) => e.path === '_errors') as error (error.messages)}
		<p class="text-destructive text-sm">{error.messages.join(' ')}</p>
	{/each}
	<Form.Button disabled={$submitting}>{submit}</Form.Button>
</form>
