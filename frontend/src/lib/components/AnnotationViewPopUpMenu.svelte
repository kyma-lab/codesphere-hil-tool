<script>
	//@ts-nocheck
	import { Tooltip } from '@svelte-plugins/tooltips';
	import { onMount, afterUpdate } from 'svelte';
	import closeIcon from '$lib/assets/icons/Close.svg';
	import trashIcon from '$lib/assets/icons/Delete.svg';
	import searchIcon from '$lib/assets/icons/Search.svg';

	export let popupTop;
	export let popupLeft;
	export let popupWidth = 264;
	export let popupMaxHeight = 636;
	export let currentSelectionSpanIds = [];
	let searchValue = '';
	export let existedLabel = '';
	export let annotateSameTokensButton = true;
	export let showPopup;
	export let annotatedData = {};
	export let annotationType = ' ';
	export let currentIndex = '';
	export let words = [];
	export let previousLabel = '';
	export let annotationsForWords;
	export let isPopupClicked;
	export let filenames;

	// Reactive statement to update filteredAnnotations when searchValue or annotations change
	$: filteredAnnotations = possibleAnnotations.filter((annotation) =>
		annotation.toLowerCase().includes(searchValue.toLowerCase())
	);

	// list of annotations that can be chosen from in the popup
	const possibleAnnotations = [
		'Hauptakteur',
		'Ergebnisempfänger',
		'Mitwirkender',
		'Aktion',
		'Signalwort',
		'Dokument',
		'Bedingung',
		'Frist',
		'Datenfeld',
		'Handlungsgrundlage'
	];

	// reactive variable to allow for search in the popup
	$: filteredAnnotations = [
		...possibleAnnotations.filter((a) => a === existedLabel),
		...possibleAnnotations.filter(
			(a) => a !== existedLabel && a.toLowerCase().includes(searchValue.toLowerCase())
		)
	];

	// Declare popup but don't export it since it's a DOM reference
	let popup;

	// Adjust the popup position once it's mounted
	onMount(() => {
		updatePopupPosition();
	});

	function updatePopupPosition() {
		console.log('popup function');
		if (popup) {
			console.log('popup');
			requestAnimationFrame(() => {
				popup.style.top = `${popupTop}px`;
				popup.style.left = `${popupLeft}px`;
				popup.style.maxHeight = `${popupMaxHeight}px`;
				popup.style.width = `${popupWidth}px`;

				console.log(popupTop, popupLeft, popupMaxHeight, popupWidth);
				// Make sure the popup is visible after setting the position
				popup.style.visibility = 'visible';
			});
		}
	}

	function hidePopup() {
		showPopup = false;
	}

	function applyAnnotation(annotationLabel) {
		let newAnnotation = {
			label: annotationLabel,
			type: annotationType,
			start_word_index: parseInt(currentSelectionSpanIds[0]),
			end_word_index: parseInt(currentSelectionSpanIds[currentSelectionSpanIds.length - 1])
		};

		console.log('new annotation, ', newAnnotation);

		console.log('AnnotationEditor', 'Attempting to apply new annotation: ' + newAnnotation);
		// Check if the current selection is already annotated
		const existingAnnotationIndex = annotatedData.data[currentIndex].annotations.findIndex(
			(ann) =>
				ann.start_word_index === newAnnotation.start_word_index &&
				ann.end_word_index === newAnnotation.end_word_index
		);

		//console.log('existing Annotation', existingAnnotationIndex);

		if (existingAnnotationIndex !== -1) {
			// Editing an existing annotation
			annotatedData.data[currentIndex].annotations[existingAnnotationIndex] = newAnnotation;
		} else {
			// Adding a new annotation;
			annotatedData.data[currentIndex].annotations.push(newAnnotation);
		}

		let annotatedText = extractText(newAnnotation);
		let newAnnotatedWithText = {
			...newAnnotation,
			text: annotatedText,
			isExpanded: false,
			previousLabel: previousLabel
		};

		annotatedData.data[currentIndex].history = [
			newAnnotatedWithText,
			...annotatedData.data[currentIndex].history
		];

		//console.log('history, ', annotatedData.data[currentIndex].history);

		// Recalculate annotations for words
		annotationsForWords = words.map((_, index) =>
			annotatedData.data[currentIndex].annotations.find(
				(ann) => index >= ann.start_word_index - 1 && index <= ann.end_word_index - 1
			)
		);

		// After applying, hide the popup and reset the currentSelectionSpanIds
		showPopup = false;
		currentSelectionSpanIds = [];
		isPopupClicked = false;

		// Reset existedLabel
		// existedLabel = '';
		annotationLabel = '';

		saveToLocalStorage(); // Save the updated data to local storage for every change.
	}

	// // for applying to the CURRENT document's similar tokens
	// // Get the current document's data
	// const doc = annotatedData.data[currentIndex];

	// // Iterate over the text of the current document
	// doc.text.forEach((word, wordIndex) => {
	// 	// Check if the current word matches the selected text
	// 	if (word === selectedText) {
	// 		// Check if this word index is part of an existing annotation
	// 		const isAnnotated = doc.annotations.some(
	// 			(ann) => wordIndex >= ann.start_word_index - 1 && wordIndex <= ann.end_word_index - 1
	// 		);

	// 		// If not annotated, apply the new annotation
	// 		if (!isAnnotated) {
	// 			doc.annotations.push({
	// 				label: annotationLabel,
	// 				start_word_index: wordIndex + 1,
	// 				end_word_index: wordIndex + 1
	// 			});

	// 			// Optionally, update the history if needed
	// 			doc.history.unshift({
	// 				label: annotationLabel,
	// 				type: 'new',
	// 				start_word_index: wordIndex + 1,
	// 				end_word_index: wordIndex + 1,
	// 				text: word,
	// 				isExpanded: false
	// 			});
	// 		}
	// 	}
	// });

	function applyAnnotationToSameText(annotationLabel) {
		if (currentSelectionSpanIds.length === 0) return;

		// Extract the selected text sequence
		const selectedStartIndex = parseInt(currentSelectionSpanIds[0]);
		const selectedEndIndex = parseInt(currentSelectionSpanIds[currentSelectionSpanIds.length - 1]);
		const selectedText = annotatedData.data[currentIndex].text
			.slice(selectedStartIndex - 1, selectedEndIndex)
			.join(' ');

		// Iterate over all documents
		annotatedData.data.forEach((doc, docIndex) => {
			const docText = doc.text.join(' '); // Join the words into a single string for easier searching

			let startPos = 0;
			let foundIndex;

			// Search for the sequence in the document text
			while ((foundIndex = docText.indexOf(selectedText, startPos)) !== -1) {
				// Calculate the start word index based on the found character index
				const wordsBefore = docText.slice(0, foundIndex).split(' ').filter(Boolean).length;

				// Adjusting for any punctuation or extra spaces
				const numSelectedWords = selectedText.split(' ').length;

				// Set end word index based on the number of words in the selectedText
				const endWordIndex = wordsBefore + numSelectedWords;

				// Check if any part of this sequence is already annotated
				const isAnyPartAnnotated = doc.annotations.some(
					(ann) =>
						// Check if any part of the selected range overlaps with an existing annotation
						wordsBefore + 1 <= ann.end_word_index && endWordIndex >= ann.start_word_index
				);

				// If any part of the phrase is annotated, skip the whole phrase
				if (isAnyPartAnnotated) {
					startPos = foundIndex + selectedText.length; // Move to the next occurrence
					continue;
				}

				// If the sequence is not annotated, apply the new annotation
				doc.annotations.push({
					label: annotationLabel,
					start_word_index: wordsBefore + 1,
					end_word_index: endWordIndex
				});

				// Optionally, update the history if needed
				doc.history.unshift({
					label: annotationLabel,
					type: 'new',
					start_word_index: wordsBefore + 1,
					end_word_index: endWordIndex,
					text: selectedText,
					isExpanded: false
				});

				// Move the search start position past the found index to avoid infinite loops
				startPos = foundIndex + selectedText.length;
			}
		});

		// Recalculate annotations for words
		annotationsForWords = words.map((_, index) =>
			annotatedData.data[currentIndex].annotations.find(
				(ann) => index >= ann.start_word_index - 1 && index <= ann.end_word_index - 1
			)
		);

		// Update history for the current document (to refresh UI)
		annotatedData.data[currentIndex].history = [...annotatedData.data[currentIndex].history];

		// After applying, hide the popup and reset the currentSelectionSpanIds
		showPopup = false;
		currentSelectionSpanIds = [];
		isPopupClicked = false;

		// Reset annotation label
		annotationLabel = '';

		// Save changes to local storage
		saveToLocalStorage();
		console.log('Annotations updated with similar tokens');
	}

	function handleDelete() {
		annotationType = 'deleted';
		//console.log(
		//	'Initial annotations:',
		//	JSON.stringify(annotatedData.data[currentIndex].annotations)
		//);
		//console.log('deleteHandle function, ', currentSelectionSpanIds);

		const [startWordIdx, endWordIdx] = currentSelectionSpanIds.map(Number);

		let deletedAnnotation = {
			label: existedLabel,
			type: annotationType,
			start_word_index: startWordIdx,
			end_word_index: endWordIdx
		};

		let annotatedText = extractText(deletedAnnotation);
		let deletedAnnotatedWithText = {
			...deletedAnnotation,
			text: annotatedText,
			isExpanded: false
		};

		annotatedData.data[currentIndex].history = [
			deletedAnnotatedWithText,
			...annotatedData.data[currentIndex].history
		];

		//console.log('history, ', annotatedData.data[currentIndex].history);

		for (let i = 0; i < annotatedData.data[currentIndex].annotations.length; i++) {
			let annotation = annotatedData.data[currentIndex].annotations[i];
			//console.log('Checking annotation:', JSON.stringify(annotation));

			//console.log('Types:', typeof annotation.start_word_index, typeof startWordIdx); // Debug log
			//console.log(
			//	'Values:',
			//	annotation.start_word_index,
			//	startWordIdx,
			//	annotation.end_word_index,
			//	endWordIdx
			//); // Debug log

			if (
				annotation.start_word_index === startWordIdx &&
				annotation.end_word_index === endWordIdx
			) {
				//console.log('Match found. Deleting...');
				annotatedData.data[currentIndex].annotations.splice(i, 1);
				break; // Once the matching annotation is found and deleted, exit the loop
			}
		}

		// Recalculate annotations for words
		annotationsForWords = words.map((_, index) =>
			annotatedData.data[currentIndex].annotations.find(
				(ann) => index >= ann.start_word_index - 1 && index <= ann.end_word_index - 1
			)
		);

		showPopup = false;
		existedLabel = '';

		//console.log(
		//	'Updated annotations:',
		//	JSON.stringify(annotatedData.data[currentIndex].annotations)
		//);
		saveToLocalStorage();
	}

	function saveToLocalStorage() {
		console.log('AnnotationEditor', 'Saving to local storage');
		// Check if the code is running in a browser environment
		if (typeof window !== 'undefined') {
			localStorage.setItem('annotatedData', JSON.stringify(annotatedData));
			localStorage.setItem('annotation_view_meta', JSON.stringify(filenames));
		} else {
			console.log(
				'AnnotationEditor',
				'window undefined (localStorage is not available on the server to save)'
			);
		}
	}

	// Function to extract the text for the annotation using the word indices
	function extractText(annotation) {
		//console.log('annotation, ', annotation);
		let annotatedText = words.slice(annotation.start_word_index - 1, annotation.end_word_index).join(' ');
		return annotatedText;
	}
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->

<div class="overlay" on:click={hidePopup}>
	<div
		class="popup-menu"
		bind:this={popup}
		style="top: {popupTop}px; left: {popupLeft}px;"
		on:click={() => {
			isPopupClicked = true;
			event.stopPropagation();
		}}
	>
		<div class="popup-search m-1 p-2">
			<!-- ... other code ... -->
			<!-- You can replace the following SVG with any preferred icon -->
			<!-- svelte-ignore a11y-img-redundant-alt -->
			<img class="search-icon m-1" style="height: 1em;" alt="search image" src={searchIcon} />
			<input
				class="d-flex p-1 w-50 rounded border"
				type="text"
				bind:value={searchValue}
				placeholder="Suchbegriff"
			/>
			<!-- svelte-ignore a11y-no-static-element-interactions -->
			<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
			<img
				style="height: 1em;"
				class="close-icon m-2"
				src={closeIcon}
				alt="remove file"
				on:click={() => {
					showPopup = false;
					existedLabel = '';
				}}
			/>
		</div>

		{#each filteredAnnotations as annotation, index}
			<div class="p-2">
				<!-- svelte-ignore a11y-click-events-have-key-events -->
				<div class={annotation === existedLabel ? 'current-label' : ''}>
					{#if existedLabel === annotation}
						<div class="annotation-with-delete">
							<div>
								<span id="selected-annotation">{annotation}</span>
							</div>

							<!-- svelte-ignore a11y-missing-attribute -->
							<!-- svelte-ignore a11y-missing-attribute -->
							<div>
								<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
								<img src={trashIcon} on:click={handleDelete} class="delete-icon" />
							</div>
						</div>
						<!-- svelte-ignore a11y-no-static-element-interactions -->
					{:else}
						<!-- svelte-ignore a11y-no-static-element-interactions -->
						<div
							on:click={() => applyAnnotation(annotation)}
							class={annotation === existedLabel ? 'current-label' : ''}
						>
							<span class="annotation-option" id="select-annotation">{annotation}</span>

							{#if annotateSameTokensButton}
								<button
									class="all-button"
									on:click={(event) => {
										event.stopPropagation();
										applyAnnotationToSameText(annotation);
									}}
								>
									<Tooltip
										content="Alle identischen Textsegmente ebenfalls annotieren"
										position="left"
									>
										Alle
									</Tooltip></button
								>
							{/if}
						</div>
					{/if}
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	@import '../../global.css';

	.popup-menu {
		position: absolute;
		margin-top: 0px;
		margin-bottom: 0ox;
		border: 1px solid #ddd;
		border-radius: 5px;
		background-color: #fff;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
		cursor: pointer;
		max-height: 640px;
		max-width: 400px !important;
		overflow-y: auto;
		overflow-x: hidden !important;
	}

	.annotation-option {
		line-height: 1.5;
	}

	.popup-menu .popup-search {
		display: flex;
		align-items: center;
		border-bottom: 1px solid #ddd;
		cursor: default;
	}

	.search-icon {
		cursor: default;
	}

	.popup-menu .popup-search input {
		flex: 1;
		margin-left: 8px;
		border: none;
		outline: none;
	}

	.popup-menu div {
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.popup-menu div:hover {
		background-color: #f5f5f5;
	}

	.popup-menu .popup-search .close-icon {
		/* Adjust the margin for proper positioning */
		cursor: pointer; /* Change cursor to indicate it's clickable */
	}

	/* Custom scrollbar for Webkit browsers */
	.popup-menu::-webkit-scrollbar {
		width: px;
	}

	.popup-menu::-webkit-scrollbar-thumb {
		background-color: #ccc;
		border-radius: 4px;
	}

	.popup-menu::-webkit-scrollbar-track {
		background-color: #f5f5f5;
	}

	.current-label {
		font-weight: bold;
	}

	.annotation-with-delete {
		display: flex;
		align-items: center; /* vertically centers the items */
		justify-content: space-between; /* spaces the items apart */
		cursor: grabbing;
	}

	.delete-icon {
		cursor: pointer;
		padding: 4px;
		width: 30px;
		height: 30px;
		margin-right: 8px;
	}

	.delete-icon:hover {
		background-color: #ffffff;
		border: 1px solid #ff0000;
		border-radius: 25px;
	}

	.all-button {
		background-color: white;
		float: right;
		color: darkslategray;
		border: 0.1mm solid darkslategray;
		border-radius: 10px;
		padding-left: 5px;
		padding-right: 5px;
		margin-right: 8px;
		cursor: pointer;
	}

	.all-button:hover {
		background-color: whitesmoke;
	}

	.overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.2); /* Adjust the opacity as needed */
		z-index: 9999; /* Make sure the overlay is on top of other elements */
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>
