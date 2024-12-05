<script>
	// @ts-nocheck
	
	import { goto } from '$app/navigation';
	import { annotationIntake } from '../../stores/store';
	import { onMount } from 'svelte';
	import { search_parameters, search_selection } from '../../stores/store.js';
	import { login } from '../login/+page.svelte';
	import { fade } from 'svelte/transition';
	import { semantic_search_request, search_request, send_selected_to_intake } from '$lib/API.js';
	import { Tooltip } from "@svelte-plugins/tooltips";
	import { log } from '$lib/CustomLogger';
	import { retrieveFromLocalStorage } from '$lib/LocalStorage';

	import CollapsibleSection from './CollapsibleSection.svelte';
	import AnnotatedFiles from '$lib/AnnotatedFiles';
	import DocumentContainer from '$lib/DocumentContainer';

	import searchIcon from '$lib/assets/icons/Search.svg';
	import deleteIcon from '$lib/assets/icons/DeleteAlternativeRed.svg';
	import TipBox from '$lib/components/Tippbox.svelte';

	// information shown in tip box
	let tips = [
		{ title: 'Tipp 1', description: 'Die semantische Suche lohnt sich erst ab 2 oder mehr Suchbegriffen.' },
		{ title: 'Tipp 2', description: 'Die Datenbank ist aktuell noch sehr klein.' }
	];

	// flag for conditional rendering of page
	let isAuthenticated = false;
	let token;

	// variables that will be initialized from the search_parameters store
	// only used for search requests triggered from the landing page
	let search_type = 'init';
	let search_query = '';

	// flag for conditional rendering of the error message
	let serverError = false;
	let errorMessage = 'Verbindung zum Server konnte nicht hergestellt werden.';

	// flag for conditional rendering of the search results
	let performedSearch = false;

	// flag for toggle of semantic search
	let semanticSearchEnabled = false;
	
	onMount(() => {
		(async () => {
			// This code handles authentication
			token = await login();
			isAuthenticated = token !== null ? true : false;

			// This code handles the incoming search requests from the landing page (if available)
			search_parameters.subscribe((value) => {
				search_query = value['search_query'];
				search_type = value['search_type'];
				log('search_parameters: received', value);
			});

			if (search_type === 'init') {
				log('search_parameters: no valid search type passed (default), restoring previous search results');

				// retrieve previous selected search results from the store
				// makes it possible to select results from multiple search requests
				search_selection.subscribe((value) => {
					selectedResults = value;
				});

			} else if (search_type === 'semantic') {
				searchQuery = search_query;
				console.log('searching semantic');
				await search_semantic();
			} else {
				searchQuery = search_query;
				await search();
			}

			// reset search type to init
			search_parameters.set({
				search_query: '',
				search_type: 'init'
			});
			
		})();
	
	});
	

	// used for the search request
	let searchQuery = '';

	// stores the results from most recent search request
	let searchResults = [];

	// variable that stores the selected results locally for display in left sidebar
	let selectedResults = [];

	let isloading = false; // show or hide loading spinner
	let show = true; // not sure what this is for (Friedrich)

	/**
	 * Wrapper function for the search request.
	 * Will perform a normal search or a semantic search, depending on the global flags.
	 * @param searchQuery
	 */
	async function search() {
		if (!validateQuery(searchQuery)) {
			return;
		}
	
		if (semanticSearchEnabled) {
			await search_semantic();
		} else {
			let res = await search_request(searchQuery, token);
	
			if (res.status == 200) {
				searchResults = res.data;
				performedSearch = true;
			} else {
				console.error('Error:', res);
				showErrorMessage('Verbindung zum Server konnte nicht hergestellt werden.');
			}
		}
	}
	
	/**
	 * Function that validates the search query string.
	 * If the search query is empty, an error message is shown.
	 * @param {String} searchQuery - The search query that should be validated.
	 * @returns {Boolean} - True if the search query is valid, false otherwise.
	 */
	function validateQuery(searchQuery) {
		if (searchQuery == '') {
			errorMessage = 'Bitte geben Sie einen Suchbegriff ein.';
			serverError = true;
			setTimeout(() => {
				serverError = false;
			}, 3000);
			return false;
		}
		return true;
	}


	/**
	 * Function that shows an error message for a short period of time.
	 * Uses the bootstrap alert.
	 * @param {String} message - The message that should be shown.
	 */
	function showErrorMessage(message) {
		serverError = true;
		errorMessage = message;
		setTimeout(() => {
			serverError = false;
		}, 3000);
	}

	/**
	 * Function that sends a request to the server to perform a semantic search.
	 * The search query is sent to the server and the results are stored in the searchResults array.
	 * Used onMount or when the search-Function is called with the semanticSearchEnabled flag set to true.
	 */
	async function search_semantic() {
		if (!validateQuery(searchQuery)) {
			return;
		}

		let res = await semantic_search_request(searchQuery, token);

		if (res.status == 200) {
			searchResults = res.data;
			performedSearch = true;
		} else {
			console.error('Error:', res);
			showErrorMessage('Verbindung zum Server konnte nicht hergestellt werden.');
		}
	}

	/**
	 * Function that is called when a result is selected or deselected.
	 * If the result is already selected, it will be removed from the selected results.
	 * If the result is not selected, it will be added to the selected results.
	 * The selected results store is updated accordingly.
	 * @param {Object} result - The result that should be toggled.
	 */
	function toggleSelected(result) {
		const index = selectedResults.findIndex((r) => r.id === result.id);

		if (index === -1) {
			// If not already selected, add to selectedResults array
			selectedResults = [
				...selectedResults,
				{ id: result.id, title: result.title, content: result.content }
			];
		} else {
			// If already selected, remove from selectedResults array
			selectedResults = selectedResults.filter((r) => r.id !== result.id);
		}

		// store the selected results in the store
		search_selection.set(selectedResults);
		log('search_selection', "stored selection in store");
	}


	/**
	 * Function that resets the search results and the selected results.
	 * Helper function called after each search.
	 */
	function reset_search() {
		searchQuery = '';
		searchResults = [];
		selectedResults = [];
		search_selection.set([]);
	}

	/**
	 * Function that sends the selected results to the intake.
	 * The selected results are then displayed in the annotation editor.
	 * During the process, a loading spinner is shown.
	 * Triggered by the upload button.
	 */
	async function uploadResults() {
		log('uploadResults', 'uploading selected results to intake');

		// extract titles and contents from selected results and build AnnotatedFiles object
		let titles = selectedResults.map((r) => r.title);
		let contents = selectedResults.map((r) => r.content);
		let payload = new AnnotatedFiles(DocumentContainer.build_array(titles, contents));

		isloading = true; // show loading spinner

		// collect method for getting predictions, default is bilstm_crf
		let selected_method = retrieveFromLocalStorage('backendMethod') ?? 'bilstm_crf';
		log('uploadResults', 'retrieved selected method:', selected_method);
		log('uploadResults', 'sending selected results to intake:', payload);

		// makes request to the /api/getpredictions endpoint to get the predictions
		let res = await send_selected_to_intake({ files: payload.files, method: selected_method }, token);
		log('uploadResults', 'response:', res);

		if (res.status == 200) {
			// on success, the user is redirected to the annotation editor
			reset_search();
			let payload = new AnnotatedFiles(res.data.files);
			annotationIntake.set(payload); // where the annotation editor reads from
			goto('/annotation-editor');
		} else {
			console.error('Error:', res);
			showErrorMessage('Verbindung zum Server konnte nicht hergestellt werden.');
		}

		isloading = false; // hide loading spinner
	}

	/**
	 * Function that handles the search bar input.
	 * Sends a search request to the server when the user presses the enter key.
	 */
	function handleSearchKeyPress(event) {
		if (event.key === 'Enter') {
			search();
		}
	}

</script>

{#if isAuthenticated}
	<main class="">
		<div class="search-container">
			<!-- container that shows the search bar and its options -->
			
			{#if serverError}
				<!-- search errors are shown here -->
				<div
					class="alert alert-warning infoposition p-1"
					transition:fade={{ duration: 500 }}
					role="alert"
				>
					{errorMessage}
				</div>
			{/if}
			
			{#await token}
				<!-- empty space here is required so per default it is empty -->
			{:then}
			<div class="container inner-search-container">
				<div class="input-container">
					<!-- div that contains the text input field for the search and the search button -->
					<input
						type="text"
						bind:value={searchQuery}
						placeholder="Suchbegriff eingeben..."
						class="input-text-container"
						on:keypress={handleSearchKeyPress}
					/>
					<button class="btn custom-button" on:click={search}>
						<img class="search-icon" src={searchIcon} alt="Lupensymbol"/>
					</button>
				</div>
				<div class="display-buttons">
					<!-- div that contains toggle to enable semantic search -->
					<label class="toggle-container">
						<input type="checkbox" bind:checked={semanticSearchEnabled}>					
						<span class="toggle-slider"></span>
					</label>

					Semantische Suche nutzen
					<div class="spacer"></div>
					<Tooltip content="Die semantische Suche verbessert die Genauigkeit und Relevanz der Suchergebnisse, indem sie den Kontext und die Bedeutung hinter Ihren Suchanfragen versteht." position="right" autoPosition="true" align="center">
						💡
					</Tooltip>
				</div>

			</div>

				
			{:catch error}
				<p>Error: {error.message}</p>
			{/await}
			
		</div>

		<div class="outer-container">
			<!-- container that shows the search results and the current selection infobox -->

			<div class="container-fluid">
				<div class="row d-flex">
					<!-- Left side, current selection sticky col -->

					{#if selectedResults.length > 0}
						<div class="col-2 bg-custom rounded">
							<div class="inner-selection-container">
								<div class="bg-custom rounded border p-2 inner-inner-selection-container">
									<div class="text-start m-2">
										<div
											class="upload-button-container"
										>
											<h5 style="margin-right: auto; margin-top: 10px;">Aktuelle Auswahl</h5>

											{#if !isloading}
												<button class="btn upload-button" title="Dies kann einen Moment dauern." on:click={uploadResults} class:show>
													Upload
												</button>
											{:else}
												<div class="loader" />
											{/if}
										</div>
									</div>

									{#if selectedResults.length > 0}
										{#each selectedResults as selectedResult}
											<div class="selected-result-box border" key={selectedResult.id}>
												<div class="d-flex flex-row justify-content-between">
													<span class="" style="">
														<p class="infotag"><strong>ID:</strong> {selectedResult.id}</p>
														<p class="infotag"><strong>Titel:</strong> {selectedResult.title}</p>
													</span>

													
													<button
														class="btn"
														title="Entfernen"
														on:click={toggleSelected({
															id: selectedResult.id,
															title: selectedResult.title,
															content: selectedResult.content
														})}
													>	
													
														<img style="height: 16px; width: 16px;" src={deleteIcon}/>
												
													</button>
												</div>
											</div>
										{/each}
									{:else}
										<p class="text-center">Leer</p>
									{/if}
								</div>
							</div>
						</div>
					{:else}
						<div class="col-2 bg-custom rounded" />
					{/if}

					<!-- main content, the search results -->
					<div class="col-8">
						{#if performedSearch && searchResults.length > 0}
							<div class="results border rounded">
								{#each searchResults as result (result.id)}
									<div class="search-results-container">
										<CollapsibleSection
											headerText={result.jurabk + ' ' + result.enbez + ' : ' + result.title}
										>
											<!-- this should be a component -->
											<div class="content">
												<div class="result-box">
													<!-- svelte-ignore missing-declaration -->
													<!-- svelte-ignore a11y-click-events-have-key-events -->
													<!-- svelte-ignore a11y-no-static-element-interactions -->
													<div class="result">
														<p><strong>ID:</strong> {result.id}</p>
														<p><strong>Gehört zu Gesetz:</strong> {result.jurabk}</p>
														<p><strong>Engere Bezeichnung:</strong> {result.enbez}</p>
														<p><strong>Titel:</strong> {result.title}</p>
														<p><strong>Inhalt:</strong> {result.content}</p>
														{#if result.link.startsWith('http://www.gesetze-im-internet.de/')}
															<p>
																<strong>Link:</strong>
																<a href={result.link} target="_blank">{result.link}</a>
															</p>
														{:else}
															<p><strong>Link:</strong> {result.link}</p>
														{/if}

														<button
															on:click={() => toggleSelected(result)}
															disabled={selectedResults.some((r) => r.id === result.id)}
															class="btn btn-primary {selectedResults.some(
																(r) => r.id === result.id
															)
																? 'added-result'
																: ''}"
																id="add-result-button"
														>
															{selectedResults.some((r) => r.id === result.id) ? '✓' : 'Hinzufügen'}
														</button>
													</div>
												</div>
											</div>
										</CollapsibleSection>
									</div>
								{/each}
							</div>
						{:else if performedSearch && searchResults.length == 0}
							<div class="results border rounded">
								<p>Keine Ergebnisse gefunden.</p>
							</div>
						{:else}
							<!-- Leer -->
						{/if}
					</div>

					<div class="col-2 bg-custom rounded" />
				</div>
			</div>
		</div>
	
		<TipBox {tips} top= "14em" left= "50%" pageId="page1"/>

	</main>
{:else}
	<!-- empty space here is required so default page is empty -->
{/if}

<style>
	.selected-result-box {
		background: #f8f8f8; /* A lighter background for differentiation */
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		border-radius: 8px;
		padding: 15px;
		margin-bottom: 10px;
		transition: transform 0.3s;
	}

	.added-result {
		background: white; /* Lighter background for better focus */
		color: green;
		border: 1mm solid green;
		cursor: not-allowed;
		min-width: 107px;
	}

	.added-result:hover {
		background: white; /* Lighter background for better focus */
		color: green;
		border: 1mm solid green;
		cursor: not-allowed;
		min-width: 107px;
	}

	.selected-result-box:hover {
		transform: scale(1); /* Slightly different hover effect for emphasis */
		/* background: #f0f0f0; Lighter background on hover for better focus */
	}

	.selected-result-box p {
		margin: 5px 0;
		color: #333;
	}

	.selected-result-box strong {
		color: #555;
	}
	.infoposition {
		position: absolute;
		bottom: 2em;
		left: 50%;
		transform: translateX(-50%);
		width: 25%;
		text-align: center;
	}

	.infotag {
		text-align: start;
	}

	.results {
		padding-top: 20px;
		margin-top: 20px;
		display: flex;
		flex-direction: column; /* Stack elements vertically. Change to row for horizontal stacking */
		justify-content: center; /* Center horizontally in the flex container */
		align-items: center; /* Center vertically in the flex container */
		text-align: center; /* Center the text inside the divs */
	}

	.result {
		text-align: justify;
	}

	.selected-result-box {
		border: 1px solid black;
		padding: 10px;
		margin: 10px;
		border-radius: 10px;
		width: 90%;
		text-align: justify;
		align-items: center;
	}

	.result-box {
		padding: 15px;
		margin-bottom: 10px;
		border-radius: 10px;
		width: 95%;
		text-align: justify;
	}

	.result-box:hover {
		transform: scale(1); /* Slightly different hover effect for emphasis */
		/* background: #f5f2f2; Lighter background on hover for better focus */
	}

	.loader {
		border: 8px solid #f3f3f3;
		border-top: 8px solid #9999ff;
		border-radius: 50%;
		width: 60px;
		height: 60px;
		animation: spin 2s linear infinite;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.display-buttons {
		display: flex;
		align-self: flex-start;
	}

	.spacer {
		width: 0.4em;
	}

	.outer-container {
		margin-top: 10px; margin-right:10px; margin-left:10px;
	}

	.inner-selection-container {
		position: sticky; top: 5vh;
	}

	.search-results-container {
		width: 100%;
	}

	.inner-inner-selection-container {
		width: 300px;
	}

	.upload-button-container {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}




	.inner-search-container {
		justify-content: center; display: flex; flex-direction: column; width: 45%
	}

	.search-container {
		margin-top: 250px;
		display: flex;
		justify-content: center;
		align-items: center;
		flex-direction: column; /* Stack elements vertically */
		/* height: 25vh;   Full viewport height */
		text-align: center; /* Center the text for aesthetics */
	}

	.search-icon {
		height: 1em; width: 3em; filter: invert(100%);
	}

	.input-container {
		width: 100%;
		display: flex;
		align-self: center;
		margin-bottom: 20px; /* Space between input and buttons */
		padding-left: 0px;
		padding-right: 0px;
		padding-top: 1px;
		padding-bottom: 1px;
		border-radius: 50px; /* Rounded corners for the input */
		border: 1px solid #ddd; /* Light border for the input */
		font-size: 16px; /* Larger font size for better readability */
	}

	.input-text-container {
		padding: 11px 15px;
		font-size: 16px; /* Larger font size for better readability */
		border-style: none; /* Removes the border for input text box */
		outline: none; /* Removes the border when clicking inside (focus in the box) the text box*/
		flex-grow: 1; /* Allow the input field to take up remaining space */
		border-radius: 50px 0 0 50px; /* Only round the left side of the input */
	}

	.custom-button {
		margin: 0;
		padding: 12px 10px;
		background-color: #9999ff; /* A blue background for the buttons */
		color: white; /* White text color */
		cursor: pointer; /* Pointer cursor on hover */
		font-size: 18px; /* Larger font size for better readability */
		border: none;
		border-radius: 50px 50px 50px 50px; 
	}

	.upload-button {
		padding: 5px 10px;
		margin-left: auto;
		border: none; /* Remove border */
		background-color: #9999ff; /* A green background for the buttons */
		color: white; /* White text color */
		cursor: pointer; /* Pointer cursor on hover */
		font-size: 14px; /* Larger font size for better readability */
	}

	.upload-button:hover {
		background-color: #8383ff; /* Darker shade on hover */
	}

	.custom-button:hover {
		background-color: #8383ff; /* Darker shade on hover */
	}

    .toggle-container {
        position: relative;
        display: inline-block;
        width: 40px;
        height: 20px;
		margin-right: 10px;
    }

    .toggle-container input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .toggle-slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: 0.4s;
        border-radius: 20px;
    }

    .toggle-slider:before {
        position: absolute;
        content: "";
        height: 16px;
        width: 16px;
        left: 2px;
        bottom: 2px;
        background-color: white;
        transition: 0.4s;
        border-radius: 50%;
    }

    input:checked + .toggle-slider {
        background-color: #9999ff;
    }

    input:checked + .toggle-slider:before {
        transform: translateX(20px);
    }

</style>