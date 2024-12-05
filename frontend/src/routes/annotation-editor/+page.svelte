<script>
	// @ts-nocheck
	import 'bootstrap/dist/css/bootstrap.min.css';
	import { processIntake, annotationIntake } from '../../stores/store.js';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { login } from '../login/+page.svelte';
	import { Tooltip } from '@svelte-plugins/tooltips';
	import AnnotationInfobox from '$lib/components/AnnotationInfobox.svelte';
	import AnnotatedFiles from '$lib/AnnotatedFiles.js';
	import DocumentSelector from '$lib/components/DocumentSelector.svelte';
	import AnnotationViewPopUpMenu from '$lib/components/AnnotationViewPopUpMenu.svelte';
	import HistoryOfChanges from '$lib/components/HistoryOfChanges.svelte';
	import DocumentContainer from '$lib/DocumentContainer.js';
	import { send_to_database } from '$lib/API.js';
	import { log } from '$lib/CustomLogger.js';
	import undoIcon from '$lib/assets/icons/Refresh.svg';
	import closeIcon from '$lib/assets/icons/Close.svg';
	import trashIcon from '$lib/assets/icons/Delete.svg';
	import searchIcon from '$lib/assets/icons/Search.svg';
	import AnnotatorToolbar from '$lib/components/AnnotatorToolbar.svelte';
	import { helpTextList } from '$lib/helpTextData.js';
	import MiniLabel from '$lib/components/MiniLabel.svelte';
	import { convertIOBToAnnotationsJson, convertJsonToIOB } from '$lib/Converter.js';

	// let html2pdf;

	// global variables to store the token and the authentication status
	let token;
	let isAuthenticated;

	// code executed on page load, checks if user is authenticated
	onMount(async () => {
		log('AnnotationEditor', 'onMount called');
		(async () => {
			token = await login();
			isAuthenticated = token !== null ? true : false;
		})();

		// only import on client side
		// if (typeof window !== 'undefined') {
        //     html2pdf = (await import('html2pdf.js')).default;
        // }
	});

	// variables that store the data received from the annotation intake store
	let resultData;
	let filenames;

	// annotation intake store is where the homepage leaves the data after receiving the predictions from the backend
	// update internal variables with the content received into the annotation intake store
	if (annotationIntake) {
		annotationIntake.subscribe((value) => {
			filenames = value.get_titles();

			value = value.get_contents();

			if (value.length == 0) {
				value = [''];
			}

			resultData = value;
		});
	}

	// will be the main data structure that is used to store the annotations and the
	let annotatedData = {
		data: []
	};

	// converts the IOB documents into a json structure
	resultData.forEach((element) => {
		let annotatedDataIndividualData = convertIOBToAnnotationsJson(element);

		annotatedData.data.push(annotatedDataIndividualData);

		// Ensure there is data to check and it's in the expected format
		if (
			annotatedData.data.length > 0 &&
			'text' in annotatedData.data[0] &&
			annotatedData.data[0].text.length > 0
		) {
			saveToLocalStorage(); // Save the updated data to local storage
		} else {
			log(
				'AnnotationEditor',
				'Not saving to local storage because the first text is empty or incorrect format'
			);
			loadFromLocalStorage();
		}
	});

	/**
	 * Function to save the annotated data to local storage.
	 * Stores the annotated data and the metadata (filenames)
	 */
	function saveToLocalStorage() {
		log('AnnotationEditor', 'Saving to local storage');
		// Check if the code is running in a browser environment
		if (typeof window !== 'undefined') {
			localStorage.setItem('annotatedData', JSON.stringify(annotatedData));
			localStorage.setItem('annotation_view_meta', JSON.stringify(filenames));
		} else {
			log(
				'AnnotationEditor',
				'window undefined (localStorage is not available on the server to save)'
			);
		}
	}

	/**
	 * Function to download the content of the annotation editor as a PDF.
	*/
	async function downloadPDF() {
		const element = document.getElementById('downloadArea');
		const clonedElement = element.cloneNode(true);

		// Create a new document and append the cloned element
		const newWindow = window.open('', '', 'width=800,height=600');
		newWindow.document.body.appendChild(clonedElement);

		// Copy all stylesheets from the original document to the new document
		const stylesheets = Array.from(document.styleSheets);
		stylesheets.forEach((stylesheet) => {
			if (stylesheet.href) {
				const link = document.createElement('link');
				link.rel = 'stylesheet';
				link.href = stylesheet.href;
				newWindow.document.head.appendChild(link);
			} else if (stylesheet.cssRules) {
				const style = document.createElement('style');
				Array.from(stylesheet.cssRules).forEach((rule) => {
					style.appendChild(document.createTextNode(rule.cssText));
				});
				newWindow.document.head.appendChild(style);
			}
		});

		// in the new window, modify element with text-with-annotations class, remove max-height and set height to auto
		const textWithAnnotations = newWindow.document.querySelector('.text-with-annotations');
		textWithAnnotations.style.maxHeight = 'none';
		textWithAnnotations.style.height = 'auto';

		// remove bg-light and border from downloadArea
		const downloadArea = newWindow.document.getElementById('downloadArea');
		downloadArea.classList.remove('bg-light');
		downloadArea.classList.remove('border');

		const options = {
			margin:       0,
			filename:     'download.pdf',
			image:        { type: 'jpeg', quality: 1 },
			html2canvas:  { scale: 2 },
			jsPDF:        { unit: 'cm', format: 'a4', orientation: 'portrait' },
			pagebreak:    { mode: ['avoid-all', 'css', 'legacy'] }
		};

		// get root element of the new window
		const root = newWindow.document.documentElement;

		// disabled because html2pdf cannot handle the "complex" styling of the text segments

		//html2pdf().from(root).set(options).save();
	}

	/**
	 * Function to load the annotated data from local storage.
	 * Retrieves the annotated data and the metadata (filenames)
	 */
	function loadFromLocalStorage() {
		// Check if the code is running in a browser environment
		if (typeof window !== 'undefined') {
			const storedData = localStorage.getItem('annotatedData');
			const storedFilenamesData = localStorage.getItem('annotation_view_meta');
			log('AnnotationEditor', 'Loading from local storage');
			if (storedData) {
				filenames = JSON.parse(storedFilenamesData);
				annotatedData = JSON.parse(storedData);
			}
		} else {
			log(
				'AnnotationEditor',
				'window undefined (localStorage is not available on the server to load)'
			);
		}
	}

	// this determines which of the documents is currently displayed
	let currentIndex = 0;

	// start and end index of the annotation that was clicked, required for deletion
	let currentSelectionSpanIds = [];

	// determines whether the popup menu is shown or not
	let showPopup = false;

	// determine the x and y position of the popup menu
	let popupTop = 400;
	let popupLeft = 750;

	// differentiate between "new", "modified" and "deleted" annotations
	let annotationType = '';

	/**
	 * Function that toggles between showing and hiding the popup menu.
	 */
	function hidePopup() {
		showPopup = false;
	}

	/**
	 * Checks if the given node is a text node that contains only whitespace characters.
	 * This is useful for ignoring nodes that do not contribute visible content to the DOM.
	 *
	 * @param {Node} node - The DOM node to check.
	 * @returns {boolean} True if the node is a text node containing only whitespace, otherwise false.
	 */
	function isSpaceNode(node) {
		return node && node.nodeType === Node.TEXT_NODE && /^\s+$/.test(node.nodeValue);
	}

	/**
	 * Adjusts the given node's reference by navigating to an adjacent sibling if certain conditions are met.
	 * - If the node is a text node that is not wrapped inside a <span>, it checks whether the node is a whitespace-only node.
	 *   - If it is a whitespace node, the function returns the next sibling.
	 *   - If it is not a whitespace node, it returns the previous sibling.
	 * - If the node is not a text node, the function returns its parent node.
	 * This function can be used when adjusting positions in the DOM for text processing or cleaning up node references.
	 *
	 * @param {Node} node - The DOM node to adjust.
	 * @returns {Node} The adjusted node based on the given criteria.
	 */
	function adjustNode(node) {
		if (node.nodeType === Node.TEXT_NODE && node.parentNode.tagName !== 'SPAN') {
			// If the node is a whitespace text node, return the next sibling; otherwise, return the previous sibling.
			return isSpaceNode(node) ? node.nextSibling : node.previousSibling;
		}
		// For non-text nodes, return the parent node.
		return node.parentNode;
	}

	// flag to determine if the user wants to annotate the same tokens with the same label across all documents
	let annotateSameTokensButton = true;

	// dimensions of the popup menu for selecting the label for selected text segment
	let popupWidth = 264;
	let popupMaxHeight = 636;

	/**
	 * Function that handles the selection of text-spans and subsequent display of the popup menu.
	 * TODO: documentation required, and also split up into more smaller functions
	 * @param node
	 */
	function handleSelectionChange() {
		existedLabel = '';
		annotationType = 'new';

		const selection = window.getSelection();

		if (selection.rangeCount > 0 && selection.toString().trim() !== '') {
			const range = selection.getRangeAt(0);
			const rect = range.getBoundingClientRect(); // Get the selection's position in the viewport

			let spanIds = [];
			const commonAncestor = range.commonAncestorContainer;
			let nodes = Array.from(commonAncestor.childNodes).filter((node) => node.tagName === 'SPAN');
			const startNode = adjustNode(range.startContainer);
			const endNode = adjustNode(range.endContainer);

			const startIndex = nodes.indexOf(startNode);
			const endIndex = nodes.indexOf(endNode);

			if (startIndex === endIndex) {
				spanIds = [startNode.id];
				annotateSameTokensButton = true;
			} else {
				spanIds = nodes.slice(startIndex, endIndex + 1).map((node) => node.id);
				annotateSameTokensButton = true;
			}

			let selectedIndices = { start: -1, end: -1 };
			if (startIndex !== -1 && endIndex !== -1) {
				selectedIndices = {
					start: parseInt(startNode.id),
					end: parseInt(endNode.id)
				};
			}

			const isOverlap = annotatedData.data[currentIndex].annotations.some(
				(ann) =>
					selectedIndices.start <= ann.end_word_index && selectedIndices.end >= ann.start_word_index
			);

			if (isOverlap) {
				console;
				alert(
					'Selected text overlaps with an existing annotation. Please select a different range.'
				);
				return;
			}

			if (spanIds.length > 0) {
				showPopup = true;
				currentSelectionSpanIds = spanIds;

				requestAnimationFrame(() => {
					// Calculate popup width and height
					popupWidth = 264; // Default width (you can adjust this if necessary)
					popupMaxHeight = 636; // Max height as defined in CSS (you can adjust this if necessary)

					// Simulate the clientX and clientY based on the middle of the selected text
					const clickX = (rect.left + rect.right) / 2; // Horizontal center of the selection
					const clickY = rect.bottom; // Bottom of the selection

					// Calculate available space above and below the selection
					const spaceBelow = window.innerHeight - clickY;
					const spaceAbove = clickY;

					// Adjust popup position based on available space
					if (spaceBelow < popupMaxHeight && spaceAbove < popupMaxHeight) {
						console.log(
							'Space below is less than popupMaxHeight and space above is less than popup maximum height'
						);
						if (spaceAbove > spaceBelow) {
							// More space above: reduce height and position above
							console.log('space above > space below');
							popupMaxHeight = spaceAbove - 20; // 20px padding
							popupTop = clickY - popupMaxHeight - 20; // 15px padding
						} else {
							// More space below: reduce height and position below
							popupMaxHeight = spaceBelow - 20; // 20px padding
							popupTop = clickY + 10; // 10px padding
						}
					} else if (spaceBelow < popupMaxHeight) {
						// Not enough space below: position above
						popupTop = clickY - popupMaxHeight + 10; // 10px padding
					} else {
						// Enough space below: position below
						popupTop = clickY + 10; // 10px padding
					}

					// Calculate left position to center the popup horizontally
					popupLeft = window.scrollX + (rect.left + rect.right) / 2 - popupWidth / 2;

					// Ensure popup stays within screen horizontally
					const minLeft = 10; // Minimum distance from left
					const maxLeft = window.innerWidth - popupWidth - 10; // Maximum distance from right

					if (popupLeft < minLeft) {
						popupLeft = minLeft;
					} else if (popupLeft > maxLeft) {
						popupLeft = maxLeft;
					}

					// At this point, you have the values for:
					// - popupTop
					// - popupLeft
					// - popupMaxHeight
					// - popupWidth
					// These can now be passed to your child component for further use
				});

				console.log(popupMaxHeight, popupWidth, popupLeft, popupTop);
			} else {
				showPopup = false;
			}
		}
	}

	// important !
	// reacetive statement that updates the words array when the currentIndex changes (document change)
	$: words = annotatedData.data[currentIndex].text;

	// important !
	// reacetive statement that updates the annotationsForWords array when the currentIndex changes (document change)
	$: annotationsForWords = words.map((_, index) =>
		annotatedData.data[currentIndex].annotations.find(
			(ann) => index >= ann.start_word_index - 1 && index <= ann.end_word_index - 1
		)
	);

	let popup; // reference to the popup DOM element

	// variables describing the attributes of the annotation that was clicked
	let existedStartIndex;
	let existedEndIndex;

	// label before the change, for the history
	let previousLabel;

	// variable that contains the label of the annotation that was clicked
	let existedLabel = '';

	/**
	 * Function to handle the click event on an annotation.
	 * This function is called when the user clicks on an existing annotation.
	 * The function extracts the text of the annotation and displays a popup menu to edit or delete the annotation.
	 * @param event
	 */
	function handleAnnotationClick(event) {
		annotateSameTokensButton = false;
		event.stopPropagation();
		log('AnnotationEditor', 'Annotation clicked');
		annotationType = 'modified';

		// Get the start and end indices of the annotation
		existedStartIndex = event.currentTarget.getAttribute('data-start-index');
		existedEndIndex = event.currentTarget.getAttribute('data-end-index');
		existedLabel = event.currentTarget.getAttribute('data-label');

		currentSelectionSpanIds = [existedStartIndex, existedEndIndex];
		previousLabel = existedLabel;

		// Show the popup
		showPopup = true;

		// Capture the click position using event.clientX and event.clientY
		const clickX = event.clientX; // X-coordinate relative to the viewport
		const clickY = event.clientY; // Y-coordinate relative to the viewport

		requestAnimationFrame(() => {
			// Calculate popup width and height
			popupWidth = 264; // Default width (adjust this value as needed)
			popupMaxHeight = 636; // Max height as defined in CSS (adjust this value as needed)

			// Calculate available space relative to the viewport
			const spaceBelow = window.innerHeight - clickY;
			const spaceAbove = clickY;

			if (spaceBelow < popupMaxHeight && spaceAbove < popupMaxHeight) {
				if (spaceAbove > spaceBelow) {
					// More space above: reduce height and position above
					popupMaxHeight = spaceAbove - 20; // 20px padding
					popupTop = clickY - popupMaxHeight - 10; // 10px padding
				} else {
					// More space below: reduce height and position below
					popupMaxHeight = spaceBelow - 20; // 20px padding
					popupTop = clickY + 10; // 10px padding
				}
			} else if (spaceBelow < popupMaxHeight) {
				// Not enough space below: position above
				popupTop = clickY - popupMaxHeight - 10; // 10px padding
			} else {
				// Enough space below: position below
				popupTop = clickY + 10; // 10px padding
			}

			// Calculate left position to center the popup horizontally on the click
			popupLeft = clickX - popupWidth / 2;

			// Boundary checks to prevent the popup from going off-screen horizontally
			const minLeft = 10; // Minimum 10px from the left edge
			const maxLeft = window.innerWidth - popupWidth - 10; // Maximum 10px from the right edge

			if (popupLeft < minLeft) {
				popupLeft = minLeft;
			} else if (popupLeft > maxLeft) {
				popupLeft = maxLeft;
			}
		});
	}

	/**
	 * Function to handle the deletion of an annotation.
	 * This function is called when the user clicks the delete button in the popup menu.
	 * The function extracts the text of the annotation, creates a history entry, and deletes the annotation.
	 */
	function handleDelete() {
		function extractText(annotation) {
			let annotatedText = words.slice(annotation.start_word_index - 1, annotation.end_word_index).join(' ');
			return { annotatedText };
		}

		annotationType = 'deleted';

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

		for (let i = 0; i < annotatedData.data[currentIndex].annotations.length; i++) {
			let annotation = annotatedData.data[currentIndex].annotations[i];

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

		// Save the updated data to local storage
		saveToLocalStorage();
	}

	async function sendToProcessView() {
		log('AnnotationEditor', 'Sending to Process View');

		saveToLocalStorage(); // Save the updated data to local storage

		// Show a confirmation dialog to the user
		//const isConfirmed = confirm('Are you sure you want to confirm all the annotations?');
		let isConfirmed = true;

		if (isConfirmed) {
			let isLoading = true;

			let iobString = convertJsonToIOB(annotatedData.data);

			// create a new AnnotatedFiles object with titles and content
			let docs = DocumentContainer.build_array(filenames, iobString);

			let payload = new AnnotatedFiles(docs);

			// for testing purposes, we can disable the contribution to the backend
			let disable_contribution = false;

			if (!disable_contribution) {
				log('AnnotationEditor', 'Contribution enabled, sending to database');
				// because this is async, we need the loading icon
				const result = await send_to_database({ files: payload.files }, token);
				log('AnnotationEditor', 'Contribution response status: ' + JSON.stringify(result.status));
			}

			// save data to processIntake, for reading it from the process view again
			processIntake.set(payload);
			log('AnnotationEditor', 'saved data to process intake store');
			goto('/process');

			// disable loading icon
			isLoading = false;
		} else {
			log('AnnotationEditor', 'User aborted on confirmation dialog');
		}
	}

	/**
	 * Function that receives callback from the DocumentSelector component and updates the currentIndex,
	 * resulting in the content of the selected document being displayed in the middle
	 * @param event
	 */
	function handleFileChange(event) {
		// Update the variables based on the dispatch event received from document selector
		currentIndex = event.detail;
	}

	/**
	 * Function to receive annotations from a JSON file.
	 * This way, users can upload a JSON file they created previously.
	 * The metadata and annotations from the JSON data are used to populate the annotation editor.
	 *
	 * @returns {void}
	 */
	function receiveAnnotations() {
		const fileInput = document.createElement('input');
		fileInput.type = 'file';
		fileInput.accept = 'application/json';
		fileInput.onchange = async (event) => {
			const file = event.target.files[0];
			if (file) {
				const text = await file.text();
				const data = JSON.parse(text);
				filenames = data.metadata;
				annotatedData = data.annotations;
				currentIndex = 0;
			}
		};
		fileInput.click();
	}

	/**
	 * Function to download annotations into a JSON file.
	 * This way, users can later continue working on a specific set of documents by uploading it again.
	 *
	 * @returns {void}
	 */
	function downloadAnnotations() {
		let payload = {
			annotations: annotatedData,
			metadata: filenames
		};

		// create json file from tmp and download it to the users computer
		let dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(payload));
		let downloadAnchorNode = document.createElement('a');
		downloadAnchorNode.setAttribute('href', dataStr);

		let date = new Date();
		let dateString = date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate();
		downloadAnchorNode.setAttribute('download', 'annotations_' + dateString + '.json');
		document.body.appendChild(downloadAnchorNode); // required for firefox
		downloadAnchorNode.click();
	}

	// global variables relevant for the document selector pane (left side next to main content)
	let documentSelectorShown = true;
	let style = 'width:250px; transition: 0.5s; height: 90vh;';
	let hideButtonStyle = 'left:250px';

	// modify global variables to hide or show the document selector pane
	function toggleDocumentSelector() {
		if (style.includes('width:250px')) {
			style = 'width:1px';
			hideButtonStyle = 'left:0px';
			documentSelectorShown = false;
		} else {
			style = 'width:250px';
			hideButtonStyle = 'left:250px';
			documentSelectorShown = true;
		}
	}

	// checks if click was on valid annotation, if yes, returns/runs the click handler (function)
	function getOnClickHandler(index, annotationsForWords, handleAnnotationClick) {
		const annotation = annotationsForWords[index];
		if (
			annotation &&
			index >= annotation.start_word_index - 1 &&
			index <= annotation.end_word_index - 1
		) {
			return handleAnnotationClick;
		}
		return undefined;
	}

	// retrieves class for the annotation (start, end or middle)
	function getSegmentClasses(index, annotationsForWords) {
		const annotation = annotationsForWords[index];
		const classes = [];

		if (annotation) classes.push('annotation');
		if (index === annotation?.start_word_index - 1) classes.push('start-annotation');
		if (index === annotation?.end_word_index - 1) classes.push('end-annotation');

		return classes.join(' ');
	}

	function getSegmentStyles(annotation) {
		// map annotation labels to colors
		let annotationColorStyles = {
			Hauptakteur: { backgroundColor: '#E1FFB3' }, // Light green
			Ergebnisempfänger: { backgroundColor: '#FFCC99' }, // Light Orange
			Mitwirkender: { backgroundColor: '#FFD1DC' }, // Light Pink
			Aktion: { backgroundColor: '#CCE5F3' }, // Light Blue
			Signalwort: { backgroundColor: '#FF9999' }, // Light red // No such color as 'lightred', consider using another color
			Dokument: { backgroundColor: '#FFFF99' }, // Light yellow
			Bedingung: { backgroundColor: '#E0E0E0' }, // light grey
			Frist: { backgroundColor: '#D8BFD8' }, // Light Purple (very light E6E6FA, light CBA3FF)
			Datenfeld: { backgroundColor: '#D3A3A3' }, // Light Brown
			Handlungsgrundlage: { backgroundColor: '#FFA07A' } // Medium grey
		};

		if (!annotation) return '';
		const bgColor = annotationColorStyles[annotation.label]?.backgroundColor || 'lightgreen';
		return `background-color: ${bgColor};`;
	}
</script>

	<div class="container-fluid">
		<div class="row d-flex">
			<li class="toolbar-container">
				<AnnotatorToolbar
					confirmAnnotations={sendToProcessView}
					{downloadAnnotations}
					{receiveAnnotations}
					downloadPDF={downloadPDF}
				/>
			</li>

			<div class="col-2 rounded">
				<HistoryOfChanges {annotatedData} {currentIndex} bind:annotationsForWords />
			</div>

			{#if filenames.length > 0 && filenames[0] != ''}
				<!-- Main Content-->
				<div class="col-8 position-relative">
					<button style={hideButtonStyle} on:click={toggleDocumentSelector} class="hide-button">
						{#if documentSelectorShown}
							<Tooltip content="Dokumentenauswahl verstecken">«</Tooltip>
						{:else}
							<Tooltip content="Dokumentenauswahl anzeigen">»</Tooltip>
						{/if}
					</button>

					<section class="d-flex h-100">
						<div class="collapsible-pane " {style}>
							<DocumentSelector {filenames} on:currentIndexChange={handleFileChange} />
						</div>

						<section class="main-pane h-100">
							<!-- Main content goes here -->

							<div id="downloadArea" class="p-3 border rounded-top bg-light h-100">
								<div class="container-fluid top-pane-container">
									<div class="row align-items-center justify-content-between">
										<!-- Document's Name -->
										<div class="col-6 d-flex justify-content-center align-items-center flex-grow-2">
											<h5 class="m-0">{filenames[currentIndex]}</h5>
										</div>
									</div>
								</div>

								<!--  Area where the actual text with the highlighted background and labels is created -->
								<div>
									<!-- svelte-ignore a11y-no-static-element-interactions -->
									<div class="w-100 h-100 m-0 p-0">
										<div class="text-with-annotations m-0 p-3" on:mouseup={handleSelectionChange}>
											<!-- loop through the tokens, for each token, check if it is inside of an annotation -->
											<!-- depending on token environment, set style and classes dynamically -->
											{#each words as word, index}
												<!-- svelte-ignore a11y-click-events-have-key-events -->
												<span
													id={index + 1}
													annotationInfo={annotationsForWords[index]}
													class={getSegmentClasses(index, annotationsForWords)}
													on:click={getOnClickHandler(
														index,
														annotationsForWords,
														handleAnnotationClick
													)}
													data-start-index={annotationsForWords[index]?.start_word_index}
													data-end-index={annotationsForWords[index]?.end_word_index}
													data-label={annotationsForWords[index]?.label}
													style={getSegmentStyles(annotationsForWords[index])}
												>
													{#if index === annotationsForWords[index]?.start_word_index - 1}
														<!-- this is the mini-text-label for the class, added in front of the annotation -->
														<MiniLabel {handleAnnotationClick} {annotationsForWords} {index} />
													{/if}
													{word}
												</span>
											{/each}
										</div>
									</div>
								</div>
							</div>
						</section>
					</section>
				</div>
			{:else}
				<div class="col-8">
					<div class="container h-100">
						<div class="row align-items-center h-100">
							<div class="col-12">
								<p class="text-center">
									Aktuell keine Daten ausgewählt. <br /> Daten können auf der Startseite und über die
									Suche ausgewählt werden.
								</p>
							</div>
						</div>
					</div>
				</div>
			{/if}

			<div class="col-2 border rounded m-0 p-0">
				<!-- Right sidebar content goes here -->
				<div class="p-2 rounded-top">
					<div class="column-header">
						Klassendefinitionen
						<Tooltip content="Vorschlag für ein Annotationsschema" position="left">💡</Tooltip>
					</div>
				</div>

				<!-- Give a condition that shows the border once the data available-->
				<div class="p-2 rounded-bottom border-top">
					<div class="right-column">
						<!-- for each element in helpTextList -->
						{#each helpTextList as item}
							<AnnotationInfobox {item} />
						{/each}
					</div>
				</div>
			</div>
		</div>
	</div>

<!-- the parameters passed to this popup component should be reduced / cleaned up -->
{#if showPopup}
	<AnnotationViewPopUpMenu
		bind:popupTop
		bind:popupLeft
		bind:popupMaxHeight
		bind:popupWidth
		{currentSelectionSpanIds}
		{existedLabel}
		bind:showPopup
		{annotatedData}
		{annotationType}
		{currentIndex}
		{words}
		{previousLabel}
		bind:annotationsForWords
		{filenames}
		bind:annotateSameTokensButton
	/>
{/if}

<style>
	@import '../../global.css';

	/* part of minimizable document selector pane */
	.main-pane {
		flex: 1; /* Take up the remaining space */
		max-height: 90vh;
	}

	/* Styling for the textsegments that are part of annotations */
	.annotation {
		padding-right: 2px;
		padding-left: 2px;
		padding-top: 3px;
		padding-bottom: 1.5px;
		margin-right: 0px;
		margin-left: 0px;
		cursor: pointer;
		user-select: none;
	}

	/* Styling for the textsegments that are the last segment of annotated segments */
	.end-annotation {
		border-top-right-radius: 13px;
		border-bottom-right-radius: 13px;
		margin-right: 2px;
		padding-right: 7px;
	}

	/* Styling for the textsegments that are the first segment of annotated segments */
	.start-annotation {
		margin-left: 4px;
		padding-left: 3px;
		border-top-left-radius: 13px;
		border-bottom-left-radius: 13px;
	}

	/* Styling for the container that contains the selected document name */
	.top-pane-container {
		flex: 0 1 auto;
	}

	/* Styling for right column header*/
	div .column-header {
		text-align: center;
		position: relative;
		padding-right: 5px;
		padding-left: 5px;
		padding-top: 5px;
		padding-bottom: 5px;
	}

	/* Styling for right column*/
	.right-column {
		height: 84vh;
		max-height: 84vh;
		overflow-y: auto;
		padding-right: 1px;
	}

	/* The container for text with annotaitons*/

	/* Additional custom styles if needed */
	.text-with-annotations {
		text-align: justify;
		line-height: 1.75;
		max-height: 80vh;
		overflow-y: auto;
	}

	.text-with-annotations::-webkit-scrollbar {
		width: 6px; /* Width of the scrollbar */
		border-radius: 10px;
	}

	.text-with-annotations::-webkit-scrollbar-track {
		background: #f1f1f1; /* Color of the track */
		border-radius: 10px;
	}

	.text-with-annotations::-webkit-scrollbar-thumb {
		background: #888; /* Color of the scrollbar itself */
		border-radius: 10px;
	}

	.text-with-annotations::-webkit-scrollbar-thumb:hover {
		background: #555; /* Color when you hover over the scrollbar */
		border-radius: 10px;
		width: 10px; /* Increase width when hovered */
	}

	/* Styling for the button to collapse the document selector */
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

	/* part of minimizable document selector pane */
	.collapsible-pane {
		width: 250px;
		overflow-y: auto;
		transition: width 0.3s;
	}

	/* Styling for the button to collapse the document selector */
	.hide-button:hover {
		background-color: #8585fa;
	}

	/* Styling for the toolbar situated above the columns */
	.toolbar-container {
		align-self: flex-end;
		display: flex;
		flex-grow: 6;
		justify-content: end;
	}
</style>
