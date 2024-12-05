
<!-- document selector pane that is shown in annotation editor and process view -->

<script>
	import { createEventDispatcher } from 'svelte';

	export let filenames;

	if (!filenames) {
		filenames = [];
	}

	let currentIndex = 0;
	const dispatch = createEventDispatcher();

	/**
	 * @param {number} i
	 */
	function handleClick(i) {
		currentIndex = i;
		dispatch('currentIndexChange', i);
	}
</script>

<div class="document-selector-column w-100 rounded border bg-light">
	<div>
		<!-- for each file, display a list item that is also a button -->
		{#each filenames as filename, i}
			<button
				class="document-item p-2"
				on:click={() => handleClick(i)}
				disabled={currentIndex === i}
			>
				<div class="container d-flex align-items-center">
					<!-- number the documents  -->
					<div class="doc-number">{i + 1}</div>
					<div title={filename} class="doc-name">
						<!-- shorten name if too long -->
						{filename.length > 25 ? `${filename.slice(0, 12)}...${filename.slice(-10)}` : filename}
					</div>
				</div>
			</button>
		{/each}
	</div>
</div>

<style>
	.document-selector-column {
		height: 100%;
		max-height: 90vh;
		float: left;
		overflow: hidden;
	}

	.container {
		gap: 4px;
		justify-content: flex-start;
	}

	.doc-number {
		opacity: 0.3;
		border-radius: 100%;
		width: 20px;
		height: 20px;
		font-size: smaller;
		margin: 0;
		padding: 0;
	}

	.doc-name {
		margin: 0;
		padding: 0;
		white-space: nowrap; /* Prevent the text from wrapping */
		flex-grow: 0; /* Prevent growing */
		flex-shrink: 1; /* Allow shrinking if space is constrained */
		font-weight: 400;
	}

	.document-item {
		width: 100%;
		border-radius: 0;
		padding: 6px;
		border: 0mm;
		background-color: transparent;
	}

	.document-item:hover {
		background-color: #ecf0f1;
	}

	.document-item:disabled {
		width: 100%;
		border-radius: 0;
		font-weight: 1000;
		color: black;
		background-color: #ecf0f1;
		border: 0mm;
	}
</style>
