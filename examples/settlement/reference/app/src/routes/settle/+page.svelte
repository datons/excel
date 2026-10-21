<script lang="ts">
	import { untrack } from 'svelte';
	import { superForm } from 'sveltekit-superforms';
	import { schemasafeClient } from 'sveltekit-superforms/adapters';
	import SchemaForm from '#lib/SchemaForm.svelte';
	import * as Card from '#lib/components/ui/card/index.ts';
	import * as Table from '#lib/components/ui/table/index.ts';
	import * as Alert from '#lib/components/ui/alert/index.ts';
	import { asJsonSchema } from '#lib/schema.ts';
	import type { Settlement } from './+page.server.ts';

	let { data } = $props();
	/* The form is created once from the first load; Superforms keeps it in sync after each submit. */
	const form = untrack(() => superForm(data.form, { validators: schemasafeClient(asJsonSchema(data.schema)), resetForm: false }));
	const { message } = form;
	const settlement = $derived($message as Settlement | undefined);
	const eur = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' });
	const mwh = new Intl.NumberFormat('es-ES', { maximumFractionDigits: 3 });
	const warnings = (d: Settlement['days'][number]) => [d.without_measures ? 'sin medidas' : '', d.missing_prices.length ? `sin precio en las horas ${d.missing_prices.join(', ')}` : ''].filter(Boolean).join('; ');
</script>

<main class="mx-auto grid max-w-4xl gap-8 p-8">
	<h1 class="text-2xl font-semibold">Liquidación de una instalación</h1>
	<SchemaForm {form} schema={data.schema} submit="Liquidar" />

	{#if settlement}
		<Card.Root>
			<Card.Header><Card.Title>Resultado: {eur.format(settlement.total_eur)}</Card.Title></Card.Header>
			<Card.Content>
				<Table.Root>
					<Table.Header>
						<Table.Row><Table.Head>Día</Table.Head><Table.Head>Horas</Table.Head><Table.Head>Estimadas</Table.Head><Table.Head>Energía (MWh)</Table.Head><Table.Head>Importe</Table.Head><Table.Head>Avisos</Table.Head></Table.Row>
					</Table.Header>
					<Table.Body>
						{#each settlement.days as d (d.day)}
							<Table.Row><Table.Cell>{d.day}</Table.Cell><Table.Cell>{d.hours}</Table.Cell><Table.Cell>{d.estimated_hours}</Table.Cell><Table.Cell>{mwh.format(d.energy_mwh)}</Table.Cell><Table.Cell>{eur.format(d.amount_eur)}</Table.Cell><Table.Cell>{warnings(d)}</Table.Cell></Table.Row>
						{/each}
					</Table.Body>
				</Table.Root>
				{#if settlement.days.some((d) => d.missing_prices.length)}
					<Alert.Root class="mt-4"><Alert.Title>Horas sin precio</Alert.Title><Alert.Description>Se han liquidado a 0, como hacía la macro. Revisa la hoja de precios.</Alert.Description></Alert.Root>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}
</main>
