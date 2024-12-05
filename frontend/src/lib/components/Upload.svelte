<!-- component that is shown on the home page, for uploading files to the server -->

<script>
	import { onMount } from 'svelte';
	import { annotationIntake } from './../../stores/store.js';
	import { goto } from '$app/navigation';
	import { fade } from 'svelte/transition';
	import { Tooltip } from "@svelte-plugins/tooltips";
	import { send_selected_to_intake } from '$lib/API.js';
	import AnnotatedFiles from '$lib/AnnotatedFiles.js';
	import DocumentContainer from '$lib/DocumentContainer.js';
	import { retrieveFromLocalStorage } from '$lib/LocalStorage.js';
	import { log } from '$lib/CustomLogger.js';
	import closeIcon from '$lib/assets/icons/DeleteAlternative.svg';

	const apiUrl = import.meta.env.VITE_SERVER_HOST_LOCATION;

	/**
	 * @type {string | undefined}
	 */
	let token;

	let serverError = false;
	let errorMessage = 'Serverfehler. Bitte versuchen Sie es später noch einmal.'

	let isLoading = false;
	/**
	 * @type {string[]}
	 */
	let fileNames = [];
	/** this should actually be a file, no idea what the file type for that is 
	 * @type {any[]}
	 */
	let allSelectedFiles = [];


	// code executed on page load
	onMount(() => {
		token = localStorage.getItem('jwt') ?? undefined;
		log("upload_component", "retrieved token from local storage");
	});

	// @ts-ignore
	function updateNames(event) {
		const newFiles = event.target.files;
		for (let file of newFiles) {
			// Check if the file is already in allSelectedFiles
			const index = allSelectedFiles.findIndex((f) => f.name === file.name);
			if (index === -1) {
				// File is not in the list, add it
				allSelectedFiles.push(file);
			} else {
				// File is already in the list, remove it
				allSelectedFiles.splice(index, 1);
			}
		}
		// Update fileNames array for display
		fileNames = allSelectedFiles.map((file) => file.name);
	}

	/**
	 * @param {number} index
	 */
	function removeFile(index) {
		allSelectedFiles.splice(index, 1);
		fileNames = allSelectedFiles.map((file) => file.name);
	}

	/**
	 * @param {string} message
	 */
	function showErrorMessage(message) {
		serverError = true;
		errorMessage = message;
		setTimeout(() => {
			serverError = false;
		}, 3000);
	}

	/**
	 * @param {Blob} file
	 */
	async function readTextFile(file) {
		// If the file is not a PDF, read it as text
		const fileReader = new FileReader();

		// Wrap file reading in a promise-like syntax
		const contentPromise = new Promise((resolve, reject) => {
			fileReader.onload = (event) => {
				// @ts-ignore
				const content = event.target.result.trim();
				resolve(content);
			};

			fileReader.onerror = (event) => {
				// @ts-ignore
				reject(event.target.error);
			};
		});

		// Read the file as text
		fileReader.readAsText(file);

		try {
			// Wait for the file content to be loaded
			const content = await contentPromise;
			log('upload_component', 'read uploaded text file');
			return content;
		} catch (error) {
			console.error(error);
			showErrorMessage('Fehler bei der Verarbeitung der Datei.');
		}
	}


	// TODO: move this function into lib/API.js
	/**
	 * @param {FormData} formData
	 * @param {string} token
	 */
	async function postExtraction(formData, token) {
		// returns string array with pdf file contents (multiple files supported)
		try {
				const response = await fetch(apiUrl + '/api/extract', {
					method: 'POST',
					body: formData,
					headers: {
						Authorization: `Bearer ${token}`
					}
				});

				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`);
				}

				const content = await response.json();
				log('upload_component', 'extracted text from uploaded pdf files');
				return content.texts;
				
			} catch (error) {
				console.error(error);
				showErrorMessage('Serverfehler C01. Bitte versuchen Sie es später noch einmal.');
			} finally {
				isLoading = false;
			}
	}

	async function handleFileUpload() {
		if (token === undefined) {
			showErrorMessage('Serverfehler C04AUTH. Bitte versuchen Sie es später noch einmal.');
			return;
		}

		log('upload_component', 'Found ' +  allSelectedFiles.length + ' files');

		/**
		 * @type {string[]}
		 */
		let fileContent = []; // will be payload for post request
		isLoading = true;
		const formData = new FormData();
		

		// Process each uploaded file

		let pdfCounter = 1;
		for (let i = 0; i < allSelectedFiles.length; i++) {
			let file = allSelectedFiles[i];

			log('upload_component', 'Processing file: ' + file.name);
			// it shows 4 files here, and processes all of them?

			// Handle depending on file type
			if (file.type === 'application/pdf') {
				formData.append('file' + (pdfCounter), file);
				pdfCounter++;
				log('upload_component', 'added pdf file to processing queue');
			} else {
				let tmpContent = await readTextFile(file);
				fileContent = fileContent.concat(tmpContent);
				log('upload_component', 'found & processed non-pdf file');
			}
		}

		// Send the PDF files to the backend if at least 1 exists
		if (formData.has('file1')) {
			let tmpContent = await postExtraction(formData, token);
			fileContent = fileContent.concat(tmpContent);
		}

		log('upload_component', 'received extraction response for PDF: ' + fileContent.length);

		// construct payload for annotation intake (AnnotatedFiles object with DocumentContainer objects)
		let payload = new AnnotatedFiles(DocumentContainer.build_array(fileNames, fileContent));

		// this parameter should be set by the user in the future
		let selected_method = retrieveFromLocalStorage('backendMethod') ?? 'bilstm_crf';

		// send to annotationIntake for annoation view
		isLoading = true;
		let res = await send_selected_to_intake({files: payload.files, method: selected_method}, token);

		if (res.status === 200) {
			let payload = new AnnotatedFiles(res.data.files);
			annotationIntake.set(payload);
			log('upload_component', 'received response from backend, moving to annotation page');
			goto('/annotation-editor');
		} else {
			showErrorMessage('Serverfehler C05. Bitte versuchen Sie es später noch einmal.');

			// TODO if code is 401, token is invalid, redirect to login, delete current token

		}
		isLoading = false;
	}

</script>

<p>Laden Sie ihre eigenen Dokumente hoch
	<Tooltip content="Sie können hier bis zu 10 Dokumente à 10MB im Dateiformat PDF oder TXT hochladen.">
		💡
	</Tooltip>

</p>
<form class="m-3" id="uploadForm" method="post" enctype="multipart/form-data">
	{#if !isLoading}
		<div>
			<label for="file" class="custom-file-upload"
				>
					Datei(en) auswählen
				
				<input type="file" id="file" name="file" multiple on:change={updateNames} />
			</label>
			<br>
			<!-- svelte-ignore empty-block -->
			{#if fileNames.length === 0}
				<!-- put some info here? -->
			{:else}
				<br />

					{#each fileNames as name, index (name)}
						<div class="file-listing border m-1">
								{name}
								<button
									class="file-remove-button"
									on:click={() => removeFile(index)}
								>
								<img class="close-icon" src={closeIcon} alt="remove file" />
								</button>
							</div>
					{/each}
			{/if}
		</div>
		<div>
			<button
				class="custom-button m-2"
				id="upload-button"
				type="submit"
				on:click|preventDefault={handleFileUpload}
				disabled={fileNames.length === 0}>
				<Tooltip content="Dies kann einen Moment dauern.">
					Upload
				</Tooltip>
			</button>
			
		</div>
	{:else}
		<div class="loader" />
	{/if}
</form>

{#if serverError}
<div class="alert alert-warning infoposition p-1" transition:fade={{ duration: 400 }} role="alert">
	{errorMessage}
</div>
{/if}

<style>
	/* styling of file upload https://stackoverflow.com/questions/572768/styling-an-input-type-file-button*/
	@import '../../global.css';

	.close-icon {
		height: 1em;
	}

	.file-listing {
		background-color: #f8f8f8;;
		width: fit-content;
		border-radius: 15px;
		margin: 10px;
		padding: 5px 10px;
	}

	input[type='file'] {
		display: none;
	}

	.infoposition {
		position: absolute;
		bottom: 2em;
		left: 50%;
		transform: translateX(-50%);
		width: 25%;
		text-align: center;
	}


	.custom-file-upload {
		border: 1px solid #ccc;
		display: inline-block;
		padding: 6px 12px;
		cursor: pointer;
		border-radius: 5px;
		background-color: white;
	}

	.file-remove-button {
		position: relative;
		padding: 0;
		margin: 5px;
		border: none;
		background: none;
		cursor: pointer;
		border-radius: 50%; /* Adjust border radius as needed */
	}

	.file-remove-button:hover svg {
		transform: scale(1.50); /* Scale the SVG by 1.03 on hover */
	}

	/* for loading animation */
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
</style>
