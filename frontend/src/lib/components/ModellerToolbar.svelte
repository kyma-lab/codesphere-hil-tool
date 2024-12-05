<!-- shown above the process modeller for action buttons -->

<script>
	import { Tooltip } from '@svelte-plugins/tooltips';
	import LoadingButton from './LoadingButton.svelte';
	export let showSummaryAction;
	export let deleteDiagramAction;
	export let downloadDiagramAction;
	export let saveDiagramAction;
</script>

<div class="container">
	<button on:click={showSummaryAction} class="button m-2"
		><Tooltip
			content="Hier werden annotierte Dokumente, Datenfelder und Bedingungen gelistet."
			position="left">Zusammenfassung anzeigen</Tooltip
		></button
	>
	<button on:click={deleteDiagramAction} class="button m-2">
		<Tooltip position="left" content="Löscht den aktuellen Inhalt (BPMN-Diagramm)">
			Diagramm löschen
		</Tooltip></button
	>
	<button on:click={downloadDiagramAction} class="button m-2"
		><Tooltip position="left" content="Lädt das BPMN-Diagramm als .bpmn Datei herunter"
			>Diagramm herunterladen</Tooltip
		></button
	>
	<LoadingButton
		buttonText="Diagramm speichern"
		classes="m-2"
		style="min-width:122px;"
		onClick={saveDiagramAction}
	/>
</div>

<style>
	.container {
		display: inline-flex;
		z-index: 200;
		width: fit-content;
	}

	.button {
		padding: 5px;
		font-size: smaller;
		border: none;
		border-radius: 5px;
		cursor: pointer;
		position: relative;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		transition: background-color 0.3s ease, color 0.3s ease;
	}
</style>
