<!-- used for displaying the annotated text in the process view without editing capabilities -->

<script>
	import { log } from '$lib/CustomLogger';

	// @ts-nocheck
	// import { convertIOBToAnnotationsJson } from '../routes/annotation-editor/+page.svelte';

	// Function to convert IOB format to annotations
	function convertIOBToAnnotationsJson(iobText) {
		log('AnnotatedView', 'converted iob to json (internel representation)');
		const annotations = [];
		const lines = iobText
			.trim()
			.split('\n')
			.filter((line) => line.trim() !== '');
		const text = [];

		let currentAnnotation = null;
		let currentTag = null;

		for (let i = 0; i < lines.length; i++) {
			const line = lines[i];

			const words = line.trim().split(' ');

			if (words.length > 1) {
				const firstWord = words[0];
				text.push(firstWord);

				const secondWord = words[1];

				if (secondWord.startsWith('B-')) {
					if (currentAnnotation !== null) {
						annotations.push(currentAnnotation);
					}

					currentTag = secondWord.split('-')[1];
					currentAnnotation = {
						start_word_index: i + 1,
						end_word_index: i + 1,
						label: currentTag
					};
				} else if (secondWord === `I-${currentTag}` && currentAnnotation !== null) {
					currentAnnotation.end_word_index = i + 1;
				} else {
					if (currentAnnotation !== null) {
						annotations.push(currentAnnotation);
						currentAnnotation = null;
					}
					currentTag = null;
				}
			}
		}

		if (currentAnnotation !== null) {
			annotations.push(currentAnnotation);
		}

		//console.log('words', text);

		return { annotations: annotations, text: text, history: [] };
	}

	/**
	 * @type {string | null | undefined}
	 */

	export let current_page_iob = '';

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

	// Corrected the mapping and reactive statement
	$: data = convertIOBToAnnotationsJson(current_page_iob);

	// Corrected the mapping and reactive statement
	$: annotationsForWords = data.text.map((_, index) =>
		data.annotations.find(
			(ann) => index >= ann.start_word_index - 1 && index <= ann.end_word_index - 1
		)
	);
</script>

<div class="text-container">
	{#each data.text as word, index}
		<span
			class={`annotated-word
                        ${annotationsForWords[index] ? 'annotated' : ''}
                        ${
													annotationsForWords[index] &&
													index === annotationsForWords[index].start_word_index - 1
														? 'start'
														: ''
												}
                        ${
													annotationsForWords[index] &&
													index === annotationsForWords[index].end_word_index - 1
														? 'end'
														: ''
												}
                        `}
			style="background-color: {annotationsForWords[index]
				? annotationColorStyles[annotationsForWords[index].label].backgroundColor
				: 'transparent'}"
		>
			{#if annotationsForWords[index] && index === annotationsForWords[index].start_word_index - 1}
				<span class="annotation-label">
					{annotationsForWords[index].label}
				</span>
			{/if}
			{word}
		</span>
	{/each}
</div>

<style>
	.annotated-word {
		padding-left: 4px;
		padding-top: 1px;
		padding-bottom: 1px;
		text-align: justify;
		display: inline;
	}

	.start {
		border-top-left-radius: 13px;
		border-bottom-left-radius: 13px;
	}

	.end {
		border-top-right-radius: 13px;
		border-bottom-right-radius: 13px;
	}

	.text-container {
		text-align: justify;
		line-height: 1.75;
	}

	.annotation-label {
		cursor: pointer;
		position: relative;
		bottom: 3px;
		font-size: 50%;
		background-color: white;
		color: black;
		border-radius: 13px;
		padding: 2px 7px;
	}
</style>
