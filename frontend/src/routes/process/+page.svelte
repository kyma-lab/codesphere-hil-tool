<script>
	import { getContext, onDestroy, onMount, setContext } from 'svelte';
	import { processIntake } from './../../stores/store.js';
	import BpmnModeler from './BpmnModeler.svelte';
	import TabComponent from './TabComponent.svelte';
	import generate_bpmn from '$lib/bpmn_generator.js';
	import { fade } from 'svelte/transition';
	import { login } from '../login/+page.svelte';
	import { extract_entities } from '$lib/IOBProcessing.js';
	import { create_generator_input, extract_entities_of_type } from '$lib/XMLGenerator.js';
	import { saveToLocalStorage, retrieveFromLocalStorage } from '$lib/LocalStorage.js';
	import AnnotatedFiles from '$lib/AnnotatedFiles.js';
	import AnnotatedDocumentHolder from '$lib/components/AnnotatedDocumentHolder.svelte';
	import AdditionalInfoBox from '$lib/components/AdditionalInfoBox.svelte';
	import { log } from '$lib/CustomLogger.js';

	// can use the following to import static resources as template:
	//import parentData from '../../resources/flow.bpmn';

	// initialisation of variables

	/** the bpmn modeller instance shown in the modeler view
	 * @type {BpmnModeler}
	 */
	let bpmnModeler1;

	/** the bpmn modeller instance shown in the split view
	 * @type {BpmnModeler}
	 */
	let bpmnModeler2;

	/** the data fields extracted from the annotated files, for the additional info box
	 * @type {string[]}
	 */
	let Datenfelder;

	/** the documents extracted from the annotated files, for the additional info box
	 * @type {string[]}
	 */
	let Dokumente;

	/** the conditions extracted from the annotated files, for the additional info box
	 * @type {string[]}
	 */
	let Bedingungen;

	// active tab in the tab component
	let active_tab = 'tab3';

	// authentication flag for conditional rendering etc
	let isAuthenticated = false;
	let token;

	// the xml data for the bpmn diagram (?)
	let parentData = '';

	// buffer variable where the input for the bpmn generator is stored (built from annotated files)
	let bpmnSourceInfo = [['']];

	/**
	 * contains the annotated files/documents that are to be displayed in the AnnotatedDocumentHolder
	 * @type {AnnotatedFiles}
	 */
	let annotated_files_container;

	// for boostrap-alerts, in either danger or info style
	let blue_message_shown = false;
	let blue_message = '';
	let red_message_shown = false;
	let red_message = 'Error: Daten konnten nicht geladen werden.';

	/**
	 * A function that merges the IOB content of all annotated files in the container.
	 * Concatenates the content of all files with a newline character in between.
	 *
	 * @param {AnnotatedFiles} annotated_files_container
	 */
	function merge_content(annotated_files_container) {
		let mergedContent = '';
		annotated_files_container.files.forEach((/** @type {{ content: string; }} */ file) => {
			mergedContent += '\n\n' + file.content;
		});
		return mergedContent;
	}

	/**
	 * Checks whether a checkpoint is available in local storage.
	 * This refers to a bpmn-modeller xml checkpoint.
	 * @returns {boolean}
	 */
	function is_checkpoint_available() {

		// TODO: change name of this checkpoint in all places to something more descriptive
		log("process_view", "checking if checkpoint is available")
		let tmpParentData = retrieveFromLocalStorage('checkpoint');
		if (tmpParentData) {
			return true;
		} else {
			return false;
		}
	}

	/**
	 * Determines whether to load a checkpoint or generate a new diagram.
	 * If new incoming data (from AnnotationView) is available, the checkpoint will be ignored.
	 * If a checkpoint is available and no new data is incoming, the checkpoint will be restored.
	 *
	 * @param {boolean} checkpoint_available
	 * @param {AnnotatedFiles} annotated_files_container
	 */
	function should_load_checkpoint(checkpoint_available, annotated_files_container) {
		log("process_view", "checking if checkpoint should be loaded")
		// if there is a checkpoint available and no new data is incoming, restore
		if (checkpoint_available && annotated_files_container.is_empty()) {
			return true;
		} else {
			return false;
		}
	}

	/**
	 * A convenience function for displaying info-level messages.
	 * @param {string} message
	 */
	function show_blue_message(message) {
		//show message
		blue_message = message;
		blue_message_shown = true;
		setTimeout(() => {
			blue_message_shown = false;
		}, 3000);
	}

	/**
	 * A convenience function for displaying alert-level messages.
	 * @param {string} message
	 */
	function show_red_message(message) {
		//show message
		red_message = message;
		red_message_shown = true;
		setTimeout(() => {
			red_message_shown = false;
		}, 3000);
	}

	/**
	 * A function that will load the annotated files container checkpoint and the BPMN diagram checkpoint.
	 * The loaded checkpoints (text and xml) may be empty, which will result in an empty diagram being generated.
	 */
	function load_checkpoint() {
		show_blue_message('Letzte Sitzung wurde wiederhergestellt.');

		// restore annotated files container from local storage (json format)
		let restored_json_iob_files = retrieveFromLocalStorage('process_view_text_checkpoint') ?? '';

		// convert json to annotated files container
		annotated_files_container = AnnotatedFiles.from_json(restored_json_iob_files);

		// process the restored annotated files container to generate BPMN
		if (annotated_files_container.is_empty()) {
			// empty text -> empty diagram
			log('process_view', 'Loaded checkpoint but it is empty.');
			bpmnSourceInfo = [['']];
		} else {
			// text available -> prepare bpmn-generator input, in case bpmn-checkpoint is not available
			log('process_view', 'Loaded checkpoint and restored BPMN from IOB data.');
			bpmnSourceInfo = extract_entities(merge_content(annotated_files_container));
		}

		// if annotated files container was checkpointed, there will also be a checkpoint for xml data (bpmn diagram)
		// load this and pass to the modeller
		let tmp = retrieveFromLocalStorage('checkpoint') ?? '';

		if (tmp !== '') {
			// if the bpmn-checkpoint was available, restore the diagram stored in that
			// in this case the generated bpmnSourceInfo is not needed
			parentData = tmp;
		} else {
			log('process_view', 'Error: Could not load checkpoint.');
			show_red_message('Fehler: Letzte Sitzung konnte nicht wiederhergestellt werden.');
			// if the bpmn-checkpoint was not available, re-generate the diagram based on the bpmnSourceInfo extracted
			// from the annotated files container (which was successfully restored)
			parentData = bpmn_xml_wrapper(bpmnSourceInfo);
		}
	}

	/**
	 * A function that will generate a new diagram based on the annotated files container input.
	 * If the input is empty, an empty diagram will be generated.
	 * Also saves the received annotated files container as a checkpoint.
	 * @param {AnnotatedFiles} annotated_files_container_input
	 */
	function generate_anew(annotated_files_container_input) {
		blue_message_shown = false;

		if (annotated_files_container_input.is_empty()) {
			bpmnSourceInfo = [['']];
			log('process_view', 'No annotated data available, generating empty diagram.');
		} else {
			// extract entities from received annotated iob data
			bpmnSourceInfo = extract_entities(merge_content(annotated_files_container_input));
		}

		// save text as checkpoint
		saveToLocalStorage('process_view_text_checkpoint', annotated_files_container_input.to_json());

		// assign xml as string here, will be passed to BpmnModeler.svelte
		parentData = bpmn_xml_wrapper(bpmnSourceInfo);
	}

	/**
	 * @param {string[][]} bpmnSourceInfo - The information needed to generate the BPMN.
	 *
	 * Wrapper function for generating BPMN based on the given list of entity - class pairs.
	 *
	 * @returns {string} - The generated BPMN.
	 */
	function bpmn_xml_wrapper(bpmnSourceInfo) {
		let input = [['Hauptakteur']];
		try {
			input = create_generator_input(bpmnSourceInfo);
		} catch (error) {
			log('process_view', 'Error: Could not generate BPMN template. Base template loaded.');
			console.error('An error occurred:', error);
			show_red_message('BPMN-Vorlage konnte nicht generiert werden.');
		}

		// OVERRIDE: for the study, we disable this feature:
		input = [];

		return generate_bpmn(input);
	}

	/**
	 * @param {string[][]} bpmnSourceInfo
	 *
	 * Function that extracts additional information for display in the AdditionalInfoBox.
	 * Returns nothing but updates global variables.
	 */
	function extract_additional_info(bpmnSourceInfo) {
		// extract entities of each type from the list of entities
		Datenfelder = extract_entities_of_type(bpmnSourceInfo, 'Datenfeld');
		Bedingungen = extract_entities_of_type(bpmnSourceInfo, 'Bedingung');
		Dokumente = extract_entities_of_type(bpmnSourceInfo, 'Dokument');
	}

	/**
	 * A function that attempts to create a checkpoint for the passed bpmn modeler
	 * @param {BpmnModeler} modeler
	 */
	function create_modeler_checkpoint(modeler) {
		if (modeler != null) {
			log('process_view', 'Creating checkpoint for modeler');
			return modeler.createCheckpoint();
		} else {
			log('process_view', 'Could not create checkpoint, modeler is not initialized.');
		}
	}

	/**
	 *
	 * A function that listens for a tab change event and creates a checkpoint for the old tab and restores the diagram for the new tab.
	 * Saves the diagram currently stored in the modeler in tab the we are leaving, so that it can be loaded by the modeler.
	 * Also updates the global variable active_tab (where is that used?).
	 *
	 * @param {{ detail: { oldTab: string; activeTab: string; }; }} event
	 */
	async function handleTabChange(event) {
		active_tab = event.detail.activeTab;

		if (event.detail.oldTab === 'tab1') {
			// switched from tab1 to another tab, so save the diagram in tab1 (most recently used)
			// @ts-ignore
			parentData = await create_modeler_checkpoint(bpmnModeler1);
		} else if (event.detail.oldTab === 'tab3') {
			// switched from tab3 to another tab, so save the diagram in tab3 (most recently used)
			// @ts-ignore
			parentData = await create_modeler_checkpoint(bpmnModeler2);
		}
	}

	// for conditional rendering of the AdditionalInfoBox overlay
	let showOverlayFlag = false;

	// hide the overlay
	function showOverlay() {
		showOverlayFlag = true;
	}

	// show the overlay
	function hideOverlay() {
		showOverlayFlag = false;
	}

	// function for the button in the toolbar
	function saveDiagramAction() {
		log("process_view", "triggered checkpointing of modeler: " + active_tab)
		if (active_tab === 'tab1') {
			create_modeler_checkpoint(bpmnModeler1);
		} else if (active_tab === 'tab3') {
			create_modeler_checkpoint(bpmnModeler2);
		}
	}

	// function for the button in the toolbar
	function downloadDiagramAction() {
		if (active_tab === 'tab1') {
			bpmnModeler1.downloadDiagram();
		} else if (active_tab === 'tab3') {
			bpmnModeler2.downloadDiagram();
		}
	}

	// function for the button in the toolbar
	function deleteDiagramAction() {
		if (active_tab === 'tab1') {
			bpmnModeler1.clearModeler();
		} else if (active_tab === 'tab3') {
			bpmnModeler2.clearModeler();
		}
	}

	// stuff that happens on mount of the component
	onMount(async () => {

		token = await login();
		isAuthenticated = token !== null ? true : false;

		// flag to check if data has been read from the store
		let firstDataReceived = false;

		/**
		 * @type {import("svelte/store").Unsubscriber}
		 */
		let unsubscribe;

		// the goal here is to read the data from the intake once, then unsubscribe
		// otherwise the processIntake would keep emitting new values and the diagram would be re-generated, overwriting user changes
		unsubscribe = processIntake.subscribe((value) => {
			if (!firstDataReceived) {
				annotated_files_container = value;
				firstDataReceived = true;
				if (typeof unsubscribe === 'function') {
					unsubscribe();
				} else {
					console.error('unsubscribe is not a function');
				}
			}
		});

		// depending on whether a checkpoint is available and new incoming data is empty (data store),
		// or we get new data, we either restore or generate a new diagram
		let checkpoint_available = is_checkpoint_available();
		if (should_load_checkpoint(checkpoint_available, annotated_files_container)) {
			log('process_view', 'Flow: Restoring checkpoint.');
			load_checkpoint();
		} else {
			log('process_view', 'Flow: Generating anew.');
			generate_anew(annotated_files_container);
			processIntake.set(new AnnotatedFiles([]));
		}

		// lists of entities not incorporated into the diagram yet, used as additional information
		extract_additional_info(bpmnSourceInfo);
	});

	onDestroy(() => {
		saveDiagramAction();
	});
</script>

{#if isAuthenticated}
	<div>
		<!-- not yet sure if this is neccessary, when I delete it nothing happens, but was in documentation... -->
		<link rel="stylesheet" href="https://unpkg.com/bpmn-js@14.2.0/dist/assets/bpmn-js.css" />
		<link rel="stylesheet" href="https://unpkg.com/bpmn-js@14.2.0/dist/assets/diagram-js.css" />

		<div class="row mt-2">
			<div class="col-1" />

			<!-- main content -->
			<div class="col-10">
				<!-- overlay for the additional info box -->
				{#if showOverlayFlag}
					<!-- svelte-ignore a11y-click-events-have-key-events -->
					<!-- svelte-ignore a11y-no-static-element-interactions -->
					<!-- svelte-ignore a11y-no-static-element-interactions -->
					<div class="overlay" on:click={hideOverlay}>
						<div class="popup" on:click|stopPropagation>
							<!-- Content of the popup -->
							<div class="popup-content">
								<!-- Information to display -->
								<p class="small-hint" style="text-align: center;">
									Außerhalb der Box klicken, um das Fenster zu schließen
								</p>
								<div class="d-flex justify-content-center">
									<div class="alert alert-info m-0 p-0" role="alert">
										<p class="small-hint alert p-1 m-0">
											💡 Klasse wählen, dessen Vorkommen angezeigt werden sollen
										</p>
									</div>
								</div>

								<AdditionalInfoBox {Datenfelder} {Bedingungen} {Dokumente} />
							</div>
						</div>
					</div>
				{/if}

				<!-- contains main content, need to pass toolbar functions here -->
				<TabComponent
					{showOverlay}
					{downloadDiagramAction}
					{saveDiagramAction}
					{deleteDiagramAction}
					on:tabchange={handleTabChange}
					activeTab="tab3"
				>
					<!-- Content for Tab 1 (exclusive modeler view) -->
					<div slot="tab1">
						<div class="container-fluid h-80vh">
							<div class="w-100 h-100">
								<div class="h-100 w-100 rounded">
									<BpmnModeler childData={parentData} bind:this={bpmnModeler1} />
								</div>
							</div>
						</div>
					</div>

					<!-- Content for Tab 2 (exclusive text view) -->
					<div slot="tab2">
						<div class="container-fluid mx-1 p-0">
							<div class="h-80vh">
								<AnnotatedDocumentHolder {annotated_files_container} />
							</div>
						</div>
					</div>
					<!-- Content for Tab 3 (split view) -->
					<div slot="tab3">
						<div class="container-fluid m-0 p-0">
							<div class="row h-80vh m-0 p-0">
								<div class="col-6 mx-1 p-0">
									<div class="border rounded vh-80">
										<AnnotatedDocumentHolder {annotated_files_container} />
									</div>
								</div>

								<div class="col mx-1 p-0">
									<div class="border rounded w-100 h-100">
										<BpmnModeler childData={parentData} bind:this={bpmnModeler2} />
									</div>
								</div>
							</div>
						</div>
					</div>
				</TabComponent>
			</div>
			<div class="col-1" />
		</div>
	</div>

	<!-- bootstrap-5 alers for user feedback -->
	{#if blue_message_shown}
		<div class="alert alert-info infoposition p-1" transition:fade={{ duration: 400 }} role="alert">
			{blue_message}
		</div>
	{/if}
	<!-- bootstrap-5 alers for user feedback -->
	{#if red_message_shown}
		<div
			class="alert alert-warning infoposition p-1"
			transition:fade={{ duration: 400 }}
			role="alert"
		>
			{red_message}
		</div>
	{/if}
{:else}
	<!-- empty space here is required so default page when logged out is empty -->
{/if}

<style>
	@import '../../global.css';

	.infoposition {
		position: absolute;
		bottom: 1em;
		left: 50%;
		transform: translateX(-50%);
		width: 25%;
		text-align: center;
	}

	.overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5); /* Adjust the opacity as needed */
		z-index: 9999; /* Make sure the overlay is on top of other elements */
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.popup {
		background-color: white;
		padding: 20px;
		border-radius: 5px;
		width: 50%;
		height: 50%;
	}

	.popup-content {
		margin-bottom: 10px;
	}

	.small-hint {
		font-size: 0.8em;
		font-style: italic;
		text-align: center;
	}
</style>
