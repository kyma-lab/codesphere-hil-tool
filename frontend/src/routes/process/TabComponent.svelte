<!-- TabComponent.svelte -->
<script>
	import ModellerToolbar from '$lib/components/ModellerToolbar.svelte';
	import { createEventDispatcher } from 'svelte';

	// Create a dispatcher, for the tab change event
	const dispatch = createEventDispatcher();

	// todo: use enum instead of strings here
	let oldTab = 'tab1';
	export let activeTab = 'tab1'; // Default active tab

	// Functions that will be received & passed to the toolbar
	export let showOverlay;
	export let deleteDiagramAction;
	export let downloadDiagramAction;
	export let saveDiagramAction;

	/** Function that updates the active tab
	 * @param {string} tab
	 */
	function setActiveTab(tab) {
		oldTab = activeTab;
		activeTab = tab;
		dispatch('tabchange', { oldTab, activeTab });
	}
</script>

<div class="container">
	<!-- navigation tabs -->
	<ul class="nav nav-tabs">
		<li class="d-flex">
			<button
				class="nav-link {activeTab === 'tab1' ? 'active' : ''}"
				on:click={() => setActiveTab('tab1')}>BPMN Tool</button
			>
		</li>
		<li class="d-flex">
			<button
				class="nav-link {activeTab === 'tab2' ? 'active' : ''}"
				on:click={() => setActiveTab('tab2')}>Texte</button
			>
		</li>
		<li class="d-flex">
			<button
				class="nav-link {activeTab === 'tab3' ? 'active' : ''}"
				on:click={() => setActiveTab('tab3')}>Kombinierte Ansicht</button
			>
		</li>

		<li class="toolbar-container">
			<ModellerToolbar
				showSummaryAction={showOverlay}
				{downloadDiagramAction}
				{saveDiagramAction}
				{deleteDiagramAction}
			/>
		</li>
	</ul>

	<!-- actual tab contents -->
	<div class="w-100 border">
		{#if activeTab === 'tab1'}
			<div class="w-100" id="tab1Content">
				<slot name="tab1">Default content for Tab 1</slot>
			</div>
		{/if}
		{#if activeTab === 'tab2'}
			<div class="w-100" id="tab2Content">
				<slot name="tab2">Default content for Tab 2</slot>
			</div>
		{/if}
		{#if activeTab === 'tab3'}
			<div class="w-100" id="tab3Content">
				<slot name="tab3">Default content for Tab 3</slot>
			</div>
		{/if}
	</div>
</div>

<style>
	.container {
		max-width: none;
		width: 100%;
		padding: 0;
		margin: 0;
	}

	.toolbar-container {
		align-self: flex-end;
		display: flex;
		flex-grow: 5;
		justify-content: end;
	}

	.nav-tabs {
		display: flex;
		flex-direction: row;
		justify-content: flex-start;
		align-items: center;
	}

	.nav-link {
		/* color: #9999ff; */
		color: black;
		font-weight: 600;
	}

	.nav-link:hover {
		/* color: #9999ff; */
		color: black;
		background-color: #ecf0f1;
	}
</style>
