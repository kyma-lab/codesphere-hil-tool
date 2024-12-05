<!-- shown above the process modeller for action buttons -->

<script>
	import { Tooltip } from '@svelte-plugins/tooltips';
	import LoadingButton from './LoadingButton.svelte';
	/**
	 * @type {() => void}
	 */
	 export let confirmAnnotations;
	export let downloadAnnotations;
	export let receiveAnnotations;
	export let downloadPDF;



	function warnThenConfirm() {
		// Show warning alert here
		if (confirm("Achtung: Dieser Vorgang wird den aktuell im Prozessmodellierer vorhandenen Inhalt (Text und Diagramm) überschreiben. Sind Sie sicher?")) {
			// Proceed with the action
			// Add your code here
			confirmAnnotations();
		} else {
			// Cancel the action
			// Add your code here
		}
	}


</script>

<div class="container">

	<button on:click={receiveAnnotations} class="button m-2"
	><Tooltip
		content=""
		position="left">Annotationen hochladen</Tooltip
	></button
>
	<button on:click={downloadAnnotations} class="button m-2">
		<Tooltip position="left" content="">
			Annotationen herunterladen
		</Tooltip></button
	>

	<button on:click={downloadPDF} class="button m-2">
		<Tooltip position="left" content="">
			Druckansicht
		</Tooltip></button
	>

	

	<button on:click={warnThenConfirm} class="button m-2 bg-green text-white"
		><Tooltip
			content="Daten zur Prozessmodellierung übernehmen"
			position="left">Zur Prozessmodellierung</Tooltip
		></button>

</div>

<style>
	.container {
		display: flex;
		z-index: 200;
		width: fit-content;
		width: 100%;
		flex-direction: row;
		justify-content: flex-end;
	}

	.button {
		padding: 5px;
		font-size: smaller;
		border: none;
		border-radius: 5px;
		cursor: pointer;
		position: relative;
		display: inline-flex;
		transition: background-color 0.3s ease, color 0.3s ease;
	}

	.bg-green {
		background-color: #4caf50;
	}

	.bg-green:hover {
		background-color: #3e8e41;
	}

</style>
