<script>
	import { onMount } from 'svelte';
	import 'bpmn-js/dist/assets/diagram-js.css';
	import 'bpmn-js/dist/assets/bpmn-font/css/bpmn.css';
	import 'bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css';
	import 'bpmn-js/dist/assets/bpmn-font/css/bpmn-codes.css';
	import generate_bpmn from '$lib/bpmn_generator';
	import { db_store_bpmn } from '$lib/API';
	import { log } from '$lib/CustomLogger';
	import AdditionalInfoBox from '$lib/components/AdditionalInfoBox.svelte';

	// to get bpmn xml from parent component
	// this is the variable holding the content that will be loaded into the modeler
	export let childData;

	export let actorsTags = {};

	/**
	 * @type {import("bpmn-js/lib/Modeler").default}
	 */
	let modeler;

	let isLoading = false;

	// bootstrap-alert flag
	let showSavedHint = false;

	// to make it available for the toolbar (in the parent component)
	export { downloadDiagram, clearModeler };

	/**
	 * Create ONLY BPMN pools (participants) from actorsTags.
	 * Each actor string becomes its own participants.
	 *
	 * @param {import("bpmn-js/lib/Modeler").default} modeler
	 * @param {Record<string, string[]>} actorsTags
	 */
	async function createAutomaticDiagram(modeler, actorsTags) {
		const elementFactory = modeler.get('elementFactory');
		const modeling = modeler.get('modeling');
		const canvas = modeler.get('canvas');
		const moddle = modeler.get('moddle');

		// layout defaults
		const startX = 150;
		const startY = 80;
		const poolWidth = 300;
		const poolHeight = 180;
		const hSpacing = 60;
		const vSpacing = 40;

		const root = canvas.getRootElement();

		// Ensure Collaboration root
		let collaboration = root;
		if (root.type !== 'bpmn:Collaboration') {
			collaboration = moddle.create('bpmn:Collaboration', {
				id: `Collaboration_${Date.now()}`
			});
			canvas.setRootElement(collaboration);
		}

		// Flatten actors into a single list
		const actorList = [...new Set(Object.values(actorsTags).flatMap((actors) => actors))];

		console.log('actorList', actorList);

		const poolsPerRow = 2;

		actorList.forEach((item, index) => {
			const col = index % poolsPerRow;
			const row = Math.floor(index / poolsPerRow);

			const x = startX + col * (poolWidth + hSpacing);
			const y = startY + row * (poolHeight + vSpacing);

			const processBO = moddle.create('bpmn:Process', {
				id: `Process_${Date.now()}_${item.replace(/\s+/g, '_')}`,
				isExecutable: false
			});

			const participantBO = moddle.create('bpmn:Participant', {
				name: item,
				processRef: processBO
			});

			const participantShape = elementFactory.createShape({
				type: 'bpmn:Participant',
				businessObject: participantBO
				//  isExpanded: true
			});

			modeling.createShape(
				participantShape,
				{ x, y, width: poolWidth, height: poolHeight },
				collaboration
			);
		});
	}

	onMount(async () => {
		// this is a mess, but there is no proper documentation for it

		//const bpmnjs = (await import('bpmn-js')).default;
		const BpmnModeler = (await import('bpmn-js/lib/Modeler')).default;
		const BpmnPaletteModule = (await import('bpmn-js/lib/features/palette')).default;
		// https://stackoverflow.com/questions/72682047/sveltekit-importing-esm-package-produces-errors-that-works-with-vite

		const container = document.getElementById('bpmn-container');

		if (container) {
			modeler = new BpmnModeler({
				container: container,
				additionalModules: [BpmnPaletteModule]
			});
			// can load bpmn from any other source here, as desired (e.g. from a file)
			init(modeler, container, childData, actorsTags);
			registerFileDrop(modeler, container, handleFileDrop);
			modeler.get('canvas').zoom('fit-viewport');
		} else {
			console.error('BPMN container not found');
		}
	});

	/**
	 * This function initializes the modeler with the given bpmn xml
	 * @param {any} modeler
	 * @param {HTMLElement} container
	 * @param {string} diagramXML
	 * @param {Record<string, string[]>} actorsTags
	 */
	async function init(modeler, container, diagramXML, actorsTags) {
		// change this if we want to use an imported file
		//let bpmnXML = await readLocalFile(diagramXML);

		let bpmnXML = diagramXML;
		await openDiagram(modeler, bpmnXML, container, actorsTags);
	}

	/**
	 * This function reads a file from the local file system.
	 * Currently not used.
	 * @param {string} filePath
	 * @returns {Promise<string>}
	 */
	async function readLocalFile(filePath) {
		try {
			const response = await fetch(filePath);
			if (!response.ok) {
				throw new Error(`Failed to fetch BPMN file: ${response.status} ${response.statusText}`);
			}

			const text = await response.text();
			return text;
		} catch (error) {
			if (error instanceof Error) {
				throw new Error(`Error reading BPMN file: ${error.message}`);
			} else {
				throw new Error('Error reading BPMN file');
			}
		}
	}

	/**
	 * This function creates a checkpoint of the current BPMN diagram.
	 * The checkpoint is stored in the local storage.
	 * It also posts the diagram to the database.
	 * Only used for the study, not for the actual application.
	 */
	async function createCheckpointWithPOST() {
		saveBpmnToLocalStorage(modeler);

		try {
			const token = localStorage.getItem('jwt');
			let username = '';
			if (token) {
				const bpmnXML = await getXML(modeler);
				const response = await db_store_bpmn(bpmnXML, username, token);

				if (response.status === 200) {
					log('bpmnmodeler', 'BPMN XML received by database server');
				} else {
					console.error('Error storing bpmn xml:', response);
				}
			}
		} catch (error) {
			console.error('Error storing bpmn xml', error);
		}

		return saveBpmnToLocalStorage(modeler);
	}

	/**
	 * This function creates a checkpoint of the current BPMN diagram.
	 * The checkpoint is stored in the local storage.
	 * Triggered by the save-diagram button in the toolbar and on tab changes.
	 */
	export async function createCheckpoint() {
		showSavedHint = true;
		setTimeout(() => {
			showSavedHint = false;
		}, 700);

		return saveBpmnToLocalStorage(modeler);
	}

	/**
	 * This function handles the drop of a file into the modeler.
	 * It reads the file and opens the diagram with the provided XML.
	 * @param {any} modeler
	 * @param {File} file
	 * @param {HTMLElement} container
	 */
	async function handleFileDrop(modeler, file, container) {
		log('bpmnmodeler', 'File dropped: ' + file.name);
		try {
			if (file instanceof Blob) {
				const xml = await readFileAsText(file);
				log('bpmnmodeler', 'extracted dropped file contents, opening...');
				await openDiagram(modeler, xml, container, {});
			} else {
				log('bpmnmodeler', 'Error: could not read and process file contents');
				throw new Error('ungültiger Dateityp');
			}
		} catch (error) {
			console.error('Error handling file drop:', error);
		}
	}

	/**
	 * This function registers the drop of a file into the modeler.
	 * It calls the provided callback function with the modeler, the file and the container.
	 * The handleFileDrop function should be used as the callback.
	 * @param {any} modeler
	 * @param {HTMLElement} container
	 * @param {Function} callback
	 */
	function registerFileDrop(modeler, container, callback) {
		function handleFileSelect(e) {
			e.stopPropagation();
			e.preventDefault();

			const files = e.dataTransfer.files;

			if (files.length > 0) {
				const file = files[0];
				callback(modeler, file, container);
			}
		}

		function handleDragOver(e) {
			e.stopPropagation();
			e.preventDefault();
			e.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
		}

		container.addEventListener('dragover', handleDragOver, false);
		container.addEventListener('drop', handleFileSelect, false);
	}

	/**
	 * This function opens the provided XML in the modeler.
	 * @param {any} modeler
	 * @param {string} xml
	 * @param {HTMLElement} container
	 * @param {Record<string, string[]>} actorsTags
	 */
	async function openDiagram(modeler, xml, container, actorsTags) {
		log('bpmnmodeler', 'Opening diagram with provided XML');
		try {
			await modeler.importXML(xml);
			log('bpmnmodeler', 'BPMN diagram loaded successfully');
			container.classList.remove('with-error');
			container.classList.add('with-diagram');

			// CALL AUTOMATIC TASK CREATION HERE
			await createAutomaticDiagram(modeler, actorsTags);
		} catch (err) {
			container.classList.remove('with-diagram');
			container.classList.add('with-error');
			console.error(err);
		}
	}

	/**
	 * This function reads a file as text.
	 * It returns a promise that resolves with the text content of the file.
	 * @param {File} file
	 * @returns {Promise<string>}
	 */
	async function readFileAsText(file) {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();

			reader.onload = function (e) {
				const text = e.target.result;
				resolve(text);
			};

			reader.onerror = function (e) {
				reject(e.target.error);
				log('bpmnmodeler', 'Error reading file as text: ' + e.target.error);
			};

			reader.readAsText(file);
		});
	}

	/**
	 * This function gets the XML of the current diagram from the modeler.
	 * Useful for creating checkpoints and downloading the diagram.
	 * @param {any} modeler
	 * @returns {Promise<string>}
	 */
	async function getXML(modeler) {
		try {
			const bpmnXMLResult = await modeler.saveXML({ format: true });
			const bpmnXML = bpmnXMLResult.xml;
			return bpmnXML;
		} catch (err) {
			console.error('Error getting bpmnxml:', err);
			// Handle error, e.g., display an error message to the user\
			return '';
		}
	}

	/**
	 * This function saves the BPMN diagram to the local storage.
	 * It creates a checkpoint of the current diagram.
	 * Used by the createCheckpoint function.
	 * @param {any} modeler
	 */
	async function saveBpmnToLocalStorage(modeler) {
		try {
			const bpmnXML = await getXML(modeler);
			localStorage.setItem('checkpoint', bpmnXML);

			/* TODO: create user feedback; last auto-save x seconds ago */
			return bpmnXML;
		} catch (err) {
			console.error('Error creating bpmnxml checkpoint in local storage:', err);
			// Handle error, e.g., display an error message to the user
		}
	}

	/**
	 * This function downloads the current diagram as a BPMN file.
	 * Triggered by the download button in the toolbar.
	 * Uses the downloadFile and getXML functions.
	 */
	async function downloadDiagram() {
		try {
			let bpmnXML = await getXML(modeler);
			downloadFile(bpmnXML, 'diagram.bpmn');
		} catch (err) {
			console.error('Error downloading diagram:', err);
			// Handle error, e.g., display an error message to the user
		}
	}

	/**
	 * This function starts a download of a file with the provided content and file name.
	 * The file is created dynamically in the browser and downloaded by the user.
	 * @param {BlobPart} content
	 * @param {string} fileName
	 */
	function downloadFile(content, fileName) {
		const blob = new Blob([content], { type: 'application/xml' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = fileName;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	}

	/**
	 * This function clears the modeler.
	 * It creates an empty BPMN diagram.
	 * Triggered by the clear button in the toolbar.
	 */
	async function clearModeler() {
		try {
			await modeler.clear();
			// have to re-initialize the modeler after clearing it, to fix its internal state
			// generate_bpmn([]) creates an empty bpmn diagram
			const container = document.getElementById('bpmn-container');
			if (!container) {
				console.error('BPMN container not found');
				return;
			}
			await openDiagram(modeler, generate_bpmn([]), container, {});
			log('bpmnmodeler', 'Modeler cleared (manual canvas reset)');
		} catch (err) {
			console.error('Error clearing modeler:', err);
			// Handle error, e.g., display an error message to the user
		}
	}
</script>

{#if isLoading}
	<div>Loading...</div>
{:else}
	<!-- main content -->
	<div id="bpmn-container" class="h-100" style="width: inherit;" />
{/if}
