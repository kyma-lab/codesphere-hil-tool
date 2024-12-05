<!-- component that is shown on the home page, for searching documents in the database-->

<script>
	import { goto } from '$app/navigation';
	import { search_parameters } from './../../stores/store.js';
	import { Tooltip } from '@svelte-plugins/tooltips';
	import { log } from '$lib/CustomLogger.js';
	import searchIcon from '$lib/assets/icons/Search.svg';

	// @ts-nocheck

	let search_query = '';
	let semantic_search = false;

	function goToSearch() {
		goto('/search');

		let stype = '';

		stype = semantic_search ? 'semantic' : 'normal';

		let params = {
			search_query: search_query,
			search_type: stype
		};

		search_parameters.set(params);
		log('Search', 'sending: ' + params);
	}

	//enter button search functions
	function handleKeyPress(event) {
		if (event.key === 'Enter') {
			goToSearch();
		}
	}

	import TipBox from '$lib/components/Tippbox.svelte';

	let tips = [
		{
			title: 'Tipp 1',
			description: 'Die semantische Suche lohnt sich erst ab 2 oder mehr Suchbegriffen.'
		},
		{ title: 'Tipp 2', description: 'Die Datenbank ist aktuell noch sehr klein.' }
	];
</script>

<p>Suchen Sie hier nach Dokumenten in unserer Datenbank.</p>

<TipBox {tips} top="42em" left="50%" pageId="page2" />

<div class="p-2 rounded-top">
	<div class="container-fluid">
		<div class="row align-items-center justify-content-between">
			<div class="col-12">
				<div class="input-group rounded">
					<input
						type="search"
						id="search-box"
						bind:value={search_query}
						class="form-control rounded"
						placeholder="Suchbegriff"
						aria-label="Search"
						aria-describedby="search-addon"
						on:keydown={handleKeyPress}
					/>
					<span class="input-group-text border-0" id="search-addon">
						<button class="btn" on:click={goToSearch}>
							<img class="search-icon" src={searchIcon} alt="search symbol" />
						</button>
					</span>
				</div>

				<div class="form-check form-switch m-2 cursor">
					<input
						bind:checked={semantic_search}
						class="form-check-input cursor"
						type="checkbox"
						role="switch"
						id="flexSwitchCheckDefault"
					/>
					<label class="form-check-label" for="flexSwitchCheckDefault">
						Semantische Suche nutzen
						<Tooltip
							content="Die semantische Suche verbessert die Genauigkeit und Relevanz der Suchergebnisse, indem sie den Kontext und die Bedeutung hinter Ihren Suchanfragen versteht."
							position="right"
							autoPosition="true"
							align="center"
						>
							💡
						</Tooltip>
					</label>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.cursor {
		cursor: pointer;
	}

	.search-icon {
		height: 1em;
	}
</style>
