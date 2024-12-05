<script>
	//@ts-nocheck
	// Import necessary variables and functions (e.g., icons or utility methods)
	import { Tooltip } from '@svelte-plugins/tooltips';
	import undoIcon from '$lib/assets/icons/Refresh.svg';

	// Properties for the component
	$: displayHistory = annotatedData.data[currentIndex].history;

	export let annotatedData = {};
	export let currentIndex;
	export let annotationsForWords = [];
	export let words = [];

	function saveToLocalStorage() {
		console.log('AnnotationEditor', 'Saving to local storage');
		// Check if the code is running in a browser environment
		if (typeof window !== 'undefined') {
			localStorage.setItem('annotatedData', JSON.stringify(annotatedData));
		} else {
			console.log(
				'AnnotationEditor',
				'window undefined (localStorage is not available on the server to save)'
			);
		}
	}

	// Function to undo the previous action (That means, if the user wants retrieve the previous actions like new annotation, modified annotaiton, and deleted annotations)
	function unDoAction(annotation) {
		if (annotation.type === 'new') {
			// Logic to handle the reversal of a new annotation
			annotatedData.data[currentIndex].annotations = annotatedData.data[
				currentIndex
			].annotations.filter((ann) => {
				return !(
					ann.start_word_index === annotation.start_word_index &&
					ann.end_word_index === annotation.end_word_index &&
					annotation.type === 'new'
				);
			});

			annotatedData.data[currentIndex].history = annotatedData.data[currentIndex].history.filter(
				(ann) => {
					return !(
						ann.start_word_index === annotation.start_word_index &&
						ann.end_word_index === annotation.end_word_index &&
						ann.type === 'new'
					);
				}
			);

			// Recalculate the annotationsForWords array
			annotationsForWords = words.map((_, index) =>
				annotatedData.data[currentIndex].annotations.find(
					(ann) => index >= ann.start_word_index - 1 && index <= ann.end_word_index - 1
				)
			);

			// Force reactivity by reassigning the array
			annotationsForWords = [...annotationsForWords]; // Triggers reactivity in Svelte

			annotatedData = { ...annotatedData }; // Reassign annotatedData for reactivity
			saveToLocalStorage();
		} else if (annotation.type === 'modified') {
			// Logic to handle the reversal of a modified annotation
			const AnnotationExistingIndex = annotatedData.data[currentIndex].annotations.findIndex(
				(ann) =>
					ann.start_word_index === annotation.start_word_index &&
					ann.end_word_index === annotation.end_word_index
			);

			if (AnnotationExistingIndex !== -1) {
				annotatedData.data[currentIndex].annotations[AnnotationExistingIndex] = {
					...annotatedData.data[currentIndex].annotations[AnnotationExistingIndex],
					label: annotation.previousLabel
				};

				annotatedData.data[currentIndex].history = annotatedData.data[currentIndex].history.filter(
					(ann) => {
						return !(
							ann.start_word_index === annotation.start_word_index &&
							ann.end_word_index === annotation.end_word_index &&
							ann.type === 'modified' &&
							ann.label === annotation.label
						);
					}
				);
			}

			// Recalculate the annotationsForWords array
			annotationsForWords = words.map((_, index) =>
				annotatedData.data[currentIndex].annotations.find(
					(ann) => index >= ann.start_word_index - 1 && index <= ann.end_word_index - 1
				)
			);

			// Force reactivity by reassigning the array
			annotationsForWords = [...annotationsForWords]; // Triggers reactivity in Svelte

			annotatedData = { ...annotatedData }; // Reassign annotatedData for reactivity
			saveToLocalStorage();
		} else if (annotation.type === 'deleted') {
			// Logic to handle the reversal of a deleted annotation
			annotatedData.data[currentIndex].annotations.push(annotation);

			annotatedData.data[currentIndex].history = annotatedData.data[currentIndex].history.filter(
				(ann) => {
					return !(
						ann.start_word_index === annotation.start_word_index &&
						ann.end_word_index === annotation.end_word_index &&
						ann.type === 'deleted'
					);
				}
			);

			// Recalculate the annotationsForWords array
			annotationsForWords = words.map((_, index) =>
				annotatedData.data[currentIndex].annotations.find(
					(ann) => index >= ann.start_word_index - 1 && index <= ann.end_word_index - 1
				)
			);

			// Force reactivity by reassigning the array
			annotationsForWords = [...annotationsForWords]; // Triggers reactivity in Svelte

			annotatedData = { ...annotatedData }; // Reassign annotatedData for reactivity
			saveToLocalStorage();
		} else {
			// Optionally handle any other types or unexpected cases
		}
	}
</script>

<div class="p-2 border rounded-top">
	<!-- Left sidebar content goes here -->
	<div class="column-header">
		Änderungverlauf
		<Tooltip
			content="Verlauf der vorgenommenen Änderungen an vorgeschlagenen Annotationen"
			position="right"
		>
			💡
		</Tooltip>
	</div>
</div>

<!-- Legend for annotation types -->
<div class="border">
	<div class="annotations-legend">
		<div class="legend-item">
			<span class="legend-color legend-new-annotation" />
			<span>Neue Annotation</span>
		</div>
		<div class="legend-item">
			<span class="legend-color legend-modified-annotation" />
			<span>Änderung</span>
		</div>
		<div class="legend-item">
			<span class="legend-color legend-deleted-annotation" />
			<span>Entfernte Annotation</span>
		</div>
	</div>
</div>

<!-- Conditional border display once history of changes is available -->
<div class="p-2 border rounded-bottom">
	<div class="annotations-history">
		{#each displayHistory as annotation, index}
			<div class="annotation-history-item {annotation.type}-annotation">
				<div class="history-annotation-icons">
					<div>
						<span id="history-text" class="annotations-history {annotation.type}-annotation-label">
							<!-- svelte-ignore a11y-click-events-have-key-events -->
							<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
							<strong
								on:click={() => (annotation.isExpanded = !annotation.isExpanded)}
								title={annotation.isExpanded ? 'Text ausblenden' : 'Text anzeigen'}
								style="cursor: pointer;"
							>
								{annotation.label}
							</strong>
						</span>
					</div>
					<div class="icons">
						{#if index === 0}
							<!-- svelte-ignore a11y-click-events-have-key-events -->
							<!-- svelte-ignore a11y-no-static-element-interactions -->
							<span
								class="undo-icon-container"
								title="go to previous action"
								on:click={() => unDoAction(annotation)}
							>
								<img class="undo-icon" src={undoIcon} alt="undo" />
							</span>
						{/if}
					</div>
				</div>

				{#if annotation.isExpanded}
					<div>
						<span id="text-container">
							<p id="history-text">
								<span class="history-text-container">{annotation.text}</span>
								<br />
							</p>
						</span>
					</div>
				{/if}
			</div>
		{/each}
	</div>
</div>

<style>
	@import '../../global.css';

	/* Add your custom styles for the component */
	.column-header {
		text-align: center;
		position: relative;
		padding-right: 5px;
		padding-left: 5px;
		padding-top: 5px;
		padding-bottom: 5px;
	}

	.legend-color {
		width: 10px;
		height: 10px;
		margin-right: 5px;
		border-radius: 50%;
	}

	.legend-new-annotation {
		background-color: green;
	}

	.legend-modified-annotation {
		background-color: orange;
	}

	.legend-deleted-annotation {
		background-color: red;
	}

	.annotation-history-item {
		margin-bottom: 10px;
	}

	.history-annotation-icons {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.undo-icon {
		width: 20px;
		height: 20px;
		cursor: pointer;
	}

	#history-text {
		cursor: pointer;
	}
	.history-text-container {
		display: block; /* Ensures the text container takes up a full line */
		max-width: 100%; /* Limits the width of the text to the container */
		line-height: 1.5; /* Adjusts spacing between lines */
		word-wrap: break-word; /* Breaks long words to fit within the container */
		text-align: justify; /* Aligns text to both left and right, creating even lines */
	}

	.undo-icon {
		height: 1.2em;
		margin-bottom: 4px;
	}

	.undo-icon-container {
		cursor: pointer;
		position: relative;
		color: black;
		border-radius: 13px;
		padding-right: 10px;
		padding-left: 10px;
		padding-bottom: 5px;
	}

	.button-container {
		display: flex; /* Aligns child divs horizontally */
		justify-content: space-between; /* Centers the child divs horizontally */
		align-items: center; /* Centers the child divs vertically */
		width: 100%;
	}

	.button-box {
		display: flex; /* Aligns buttons horizontally */
		border-radius: 5px;
		padding: 10px;
		justify-content: center;
		width: fit-content;
		margin-top: 11px;
		margin-bottom: 2px;
		margin-left: 5px;
		margin-right: 5px;
	}
	.bg-custom {
		background-color: #e1e1fc;
	}

	.page-button {
		cursor: pointer;
		padding: 5px 10px;
		background-color: #9999ff;
		color: #fff;
		border: none;
		border-radius: 5px;
	}

	.annotations-history {
		line-height: 1.75;
		height: 83vh;
		max-height: 83vh;
		overflow-y: auto;
		padding-right: 1px;
		/* border: 1px solid #ccc; */
	}

	/* Color for new annotations */
	.annotations-history .new-annotation-label {
		background-color: rgba(255, 255, 255, 0.726);
		position: relative;
		bottom: 3px;
		border-radius: 13px;
		padding-right: 7px;
		padding-left: 8px;
		padding-top: 2px;
		padding-bottom: 3px;
	}

	/* Color for deleted annotations */
	.annotations-history .deleted-annotation-label {
		background-color: rgba(255, 255, 255, 0.777);
		position: relative;
		bottom: 3px;
		border-radius: 13px;
		padding-right: 7px;
		padding-left: 8px;
		padding-top: 2px;
		padding-bottom: 3px;
	}

	/* Color for modified annotations */
	.annotations-history .modified-annotation-label {
		background-color: rgba(255, 255, 255, 0.678);
		/* You can use lightyellow or another color of your choice */
		position: relative;
		bottom: 3px;
		border-radius: 13px;
		padding-right: 7px;
		padding-left: 8px;
		padding-top: 2px;
		padding-bottom: 3px;
	}

	/* Styling the scrollbar for webkit browsers */
	.annotations-history::-webkit-scrollbar {
		width: 6px; /* Width of the scrollbar */
		border-radius: 10px;
	}

	.annotations-history::-webkit-scrollbar-track {
		background: #f1f1f1; /* Color of the track */
		border-radius: 10px;
	}

	.annotations-history::-webkit-scrollbar-thumb {
		background: #888; /* Color of the scrollbar itself */
		border-radius: 10px;
	}

	.annotations-history::-webkit-scrollbar-thumb:hover {
		background: #555; /* Color when you hover over the scrollbar */
		border-radius: 10px;
		width: 10px;
	}

	.annotation-history-item {
		margin-bottom: 1px; /* Optional spacing between history items */
		padding-left: 20px;
		padding-top: 8px;
		padding-right: 8px;
		border: 1px solid #ccc;
		border-radius: 5px;
		align-items: center; /* Center items vertically */
		position: relative;
	}

	.annotation-history-item::before {
		content: ''; /* Required for the pseudo-element to be generated */
		position: absolute;
		left: 0; /* Aligns the line to the left edge of the item */
		top: 0; /* Positions it at the middle vertically */
		bottom: 0;
		width: 13px; /* Width of the indicator line */
		border-top-left-radius: 4px;
		border-bottom-left-radius: 4px;
		background-color: #000; /* Default color, will be overridden based on annotation type */
	}

	.annotation-history-item.new-annotation::before {
		background-color: rgba(64, 148, 64, 0.726); /* Green for new annotations */
	}

	.annotation-history-item.deleted-annotation::before {
		background-color: rgba(206, 57, 57, 0.777); /* Red for deleted annotations */
	}

	.annotation-history-item.modified-annotation::before {
		background-color: rgba(227, 227, 88, 0.678); /* Yellow for modified annotations */
	}

	.history-annotation-icons {
		display: flex;
		justify-content: space-between; /* This will push the child elements to opposite sides */
		align-items: center; /* To align items vertically in the center, if needed */
		width: 100%; /* Ensure the container takes full width */
	}
	.btn-cnf-ann {
		color: #ffffff; /* Text color */
		background-color: #007bff; /* Button background color */
		border: 2px solid #0056b3; /* Button border color and width */
		padding: 8px 15px; /* Button padding */
		font-size: 16px; /* Text size */
		border-radius: 5px; /* Border radius for rounded corners */
		transition: background-color 0.3s, color 0.3s, border-color 0.3s; /* Transition effect */
	}

	.btn-cnf-ann:hover {
		background-color: #cfd84c; /* Darker background color on hover */
		color: #0056b3; /* Text color on hover (if needed to be changed) */
		border-color: #004085; /* Darker border color on hover */
	}

	.documents-remaining {
		margin-left: 8px; /* Adjust based on your design needs */
		font-size: 14px; /* Adjust font size as needed */
	}
	/* Include additional styles for .btn-cnf-ann if necessary */

	.annotations-legend {
		display: flex;
		justify-content: space-evenly;
		padding-top: 3px; /* Adjust the space between the legend and the content above */
		padding-bottom: 3px;
		font-size: x-small;
	}

	.legend-item {
		display: flex;
		align-items: center;
	}

	.legend-color {
		width: 15px; /* Size of the color box */
		height: 15px;
		border-radius: 3px; /* Optional: if you prefer rounded corners */
		margin-right: 5px; /* Space between color box and text */
	}

	.legend-new-annotation {
		background-color: rgba(64, 148, 64, 0.726); /* Green */
	}

	.legend-modified-annotation {
		background-color: rgba(255, 238, 0, 0.678); /* Yellow */
	}

	.legend-deleted-annotation {
		background-color: rgba(206, 57, 57, 0.777); /* Red */
	}
</style>
