<script>
	import { log } from '$lib/CustomLogger';

	/**
	 * @type {string[]}
	 */
	let outputList = [];
	let selectedOption = 2;

	// get from parent component
	/**
	 * @type {string[]}
	 */
	export let Datenfelder;
	/**
	 * @type {string[]}
	 */
	export let Bedingungen;
	/**
	 * @type {string[]}
	 */
	export let Dokumente;

	select_additional_info_category(selectedOption);

	/**
	 * @param {number} option
	 */
	// selects the category of additional information to display below bpmn modeler
	function select_additional_info_category(option) {
		log('AdditionalInfoBox', 'selected option: ' + option);
		switch (option) {
			case 1: // Datenfelder
				selectedOption = 1;
				// @ts-ignore
				Datenfelder = [...new Set(Datenfelder)];
				outputList = Datenfelder;
				log('AdditionalInfoBox', 'Datenfelder: ' + Datenfelder);
				break;
			case 2: //Bedingungen
				selectedOption = 2;
				Bedingungen = [...new Set(Bedingungen)];
				outputList = Bedingungen;
				log('AdditionalInfoBox', 'Bedingungen: ' + Bedingungen);
				break;
			case 3: // Dokumente
				selectedOption = 3;
				// remove duplicates from list of Dokumente
				Dokumente = [...new Set(Dokumente)];
				outputList = Dokumente;
				log('AdditionalInfoBox', 'Dokumente: ' + Dokumente);
				break;
			default:
				log('AdditionalInfoBox', 'Input is not 1, 2, or 3. This should not happen.');
				break;
		}
	}
</script>

<div class="mt-4">
	<div class="switch-container bg-light">
		<div class="container-fluid inner-container">
			<div class="row align-items-center justify-content-between">
				<div class="col d-flex justify-content-center flex-grow-1">
					<button
						class={`switch-button ${selectedOption === 1 ? 'switch-button-selected' : ''}`}
						on:click={() => select_additional_info_category(1)}
					>
						Datenfelder
					</button>
					<button
						class={`switch-button ${selectedOption === 2 ? 'switch-button-selected' : ''}`}
						on:click={() => select_additional_info_category(2)}
					>
						Bedingungen
					</button>
					<button
						class={`switch-button ${selectedOption === 3 ? 'switch-button-selected' : ''}`}
						on:click={() => select_additional_info_category(3)}
					>
						Dokumente
					</button>
				</div>
			</div>
		</div>
	</div>
	{#if outputList.length === 0}
		<div class="d-flex justify-content-center align-items-center">
			<p class="nicetext">Keine Annotationen gefunden.</p>
		</div>
	{:else}
		<div>
			<p class="nicetext">
				{#each outputList as str (str)}
					<div class="circular-box">
						{str}
					</div>
				{/each}
			</p>
		</div>
	{/if}
</div>

<style>
	@import '../../global.css';

	.inner-container {
		min-width: 410px;
	}

	.circular-box {
		width: fit-content;
		height: fit-content;
		border-radius: 10px;
		border: 0.4mm solid #ccc;
		display: flex;
		justify-content: center;
		align-items: center;
		margin: 4px;
		padding: 5px;
	}

	.nicetext {
		border: 0px solid #ccc;
		border-radius: 10px;
		background-color: #fff;
	}

	.switch-container {
		display: flex;
		justify-content: space-around;
		margin: 10px;
		background-color: #fff;
		border: 1px solid #ccc;
		border-radius: 10px;
		min-width: 350px;
	}

	.switch-button {
		padding: 5px 10px;
		cursor: pointer;
		border: 0px solid #ccc;
		border-radius: 10px;
		background-color: rgba(var(--bs-light-rgb), var(--bs-bg-opacity));
		transition: background-color 0.3s;
	}
	.switch-button:hover {
		background-color: #ccc;
	}

	.switch-button-selected {
		background-color: #9999ff;
		color: #fff;
	}

	.switch-button-selected:hover {
		background-color: #9999ff;
		color: #fff;
	}
</style>
