<script>
	// @ts-nocheck
	import { onMount } from 'svelte';
	import { login } from './login/+page.svelte';
	import Search from '$lib/components/Search.svelte';
	import Upload from '$lib/components/Upload.svelte';

	// declare variables
	let isAuthenticated = false;
	let token;

	// on mount, check if user is authenticated
	onMount(async () => {
		(async () => {
			token = await login();
			isAuthenticated = token !== null ? true : false;
		})();
	});
</script>

<!-- if user is authenticated, show the main page -->
{#await token}
	<p>Loading</p>
{:then}
	{#if isAuthenticated}
		<!-- user is authenticated, show grid with two options (components)-->
		<main>
			<h1 class="page-header">Normenanalyse</h1>

			<div class="row pt-4">
				<div class="grid-item p-3">
					<h2>Suche</h2>
					<div>
						<Search />
					</div>
				</div>
				<div class="grid-gap" />
				<div class="grid-item p-3">
					<h2>Annotation</h2>
					<div>
						<Upload />
					</div>
				</div>
			</div>
		</main>
	{:else}
		<!-- empty space here is required so default page is empty -->
	{/if}
{:catch error}
	<p style="color:red;">{error.message}</p>
{/await}

<style>
	@import '../global.css';

	main {
		color: black;
		margin: 100px auto 0 auto;
		width: 80%;
	}
	.grid-item {
		float: left;
		padding: 10px;
		background-color: #e6e6ff;
		width: 45%;
	}
	.grid-gap {
		float: left;
		padding: 10px;
		/*background-color: coral;*/
		width: 10%;
	}

	@media screen and (max-width: 600px) {
		.grid-item,
		.grid-gap {
			width: 100%;
		}
	}

	.page-header {
		color: #9999ff;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
		text-align: center;
	}
	.row::after {
		content: '';
		display: table;
		clear: both;
	}

	* {
		box-sizing: border-box;
	}
</style>
