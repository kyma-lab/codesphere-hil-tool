
<!-- document selector pane that is shown in annotation editor and process view -->


<script>
	// @ts-nocheck

	import AnnotatedView from '$lib/components/AnnotatedView.svelte';
	import AnnotatedFiles from '$lib/AnnotatedFiles.js';
	import { Tooltip } from '@svelte-plugins/tooltips';
	import DocumentSelector from './DocumentSelector.svelte';
	import DocumentContainer from '$lib/DocumentContainer';
	import { log } from '$lib/CustomLogger';

	/**
	 * @type {AnnotatedFiles}
	 */
	export let annotated_files_container;

	let currentIndex = 0;
	let documentSelectorShown = true;
	let style = 'width:250px; height: 80vh; ;';
	let hideButtonStyle = 'left:240px';
	let filenames;
	let current_page_iob;
	let current_doc;
	let no_content = false;

	if (
		annotated_files_container === undefined ||
		annotated_files_container === null ||
		annotated_files_container.is_empty()
	) {
		annotated_files_container = new AnnotatedFiles([new DocumentContainer('', '')]);
		no_content = true;
		log('AnnotatedDocumentHolder', 'No content');
	}

	log('AnnotatedDocumentHolder', 'contains titles:' + annotated_files_container.get_titles());

	$: current_doc = annotated_files_container.get_file(currentIndex);
	$: current_page_iob = current_doc.content;
	$: filenames = annotated_files_container.get_titles();

	function handleIndexChange(event) {
		// Update the variables based on the dispatch event received from document selector
		currentIndex = event.detail;
	}

	function toggleDocumentSelector() {
		if (style.includes('width:250px')) {
			style = 'width:1px; height: 80vh;';
			hideButtonStyle = 'left:-10px';
			documentSelectorShown = false;
		} else {
			style = 'width:250px;height: 80vh;';
			hideButtonStyle = 'left:240px';
			documentSelectorShown = true;
		}
	}
</script>

<!-- svelte-ignore non-top-level-reactive-declaration -->
<div class="h-100 w-100">
	<!-- Content for left column -->

	{#if !annotated_files_container.is_empty() && !no_content}
		<div class="m-0 p-0 rounded-top w-100 h-90 position-relative">
			<button style={hideButtonStyle} on:click={toggleDocumentSelector} class="hide-button">
				{#if documentSelectorShown}
					<Tooltip content="Dokumentenauswahl verstecken">«</Tooltip>
				{:else}
					<Tooltip content="Dokumentenauswahl anzeigen">»</Tooltip>
				{/if}
			</button>

			<section class="parent">
				<div class="left" {style}>
					<DocumentSelector {filenames} on:currentIndexChange={handleIndexChange} />
				</div>

				<div class="h-80vh right">
					<div class="row align-items-center justify-content-between p-2">
						<!-- Document's Name -->
						<div class="col d-flex justify-content-center flex-grow-1 document-name-header">
							{current_doc.title}
						</div>
					</div>
					<div class="scrollable-div">
						<AnnotatedView {current_page_iob} />
					</div>
				</div>
			</section>
		</div>
	{:else}
		<!-- shown if no documents were uploaded -->
		<div class="row align-items-center rounded h-80vh w-100">
			<div class="col-12">
				<p class="text-center">
					Aktuell keine Daten ausgewählt. <br /> Daten können auf der Startseite und über die Suche
					ausgewählt werden. <br /><br />

					BPMN-Dateien koennen direkt durch Drag-und-Drop in den Modeller hochgeladen werden.
				</p>
			</div>
		</div>
	{/if}
</div>

<style>
	@import '../../global.css';

	/* Apply styles to make the div scrollable */
	.scrollable-div {
		overflow-y: auto; /* Enable vertical scrolling if content exceeds the height */
		padding: 10px; /* Optional: Add padding for better spacing */
		border-radius: 5px;
		padding: 20px;
		max-height: 95%;
	}

	.parent {
		display: flex;
		height: 80vh; /* Ensure the parent takes up the full viewport height */
	}

	.left {
		width: 250px; /* Initial width of the left div */
		overflow-y: auto; /* Handle overflow if content exceeds the height */
		transition: width 0.3s; /* Smooth transition for width changes */
	}

	.right {
		flex: 1; /* Take up the remaining space */
		overflow-y: auto; /* Handle overflow for the main content */
		overflow-x: hidden;
	}

	.document-name-header {
		font-size: 1.25rem;
	}

	.hide-button {
		position: absolute;
		top: 10px;
		border-radius: 100%;
		height: 30px;
		width: 30px;
		border: none;
		background-color: #9999ff;
		z-index: 1000;
		color: white;
	}

	.hide-button:hover {
		background-color: #8585fa;
	}
</style>
