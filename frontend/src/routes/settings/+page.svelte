<script>
	import 'bootstrap/dist/css/bootstrap.min.css';
	import { login } from '../login/+page.svelte';
	import { jwtDecode } from 'jwt-decode';
	import { onMount } from 'svelte';
	import { log } from '$lib/CustomLogger';
	import GridClient from '$lib/components/GridClient.svelte';
	import GridUsers from '$lib/components/GridUsers.svelte';
	import GridServer from '$lib/components/GridServer.svelte';
	import GridLogs from '$lib/components/GridLogs.svelte';
	import GridProfile from '$lib/components/GridProfile.svelte';

	/**
	 * @type {string}
	 */
	let token;

	let decodedToken = null;
	let current_user = 'Not Authenticated';
	let current_user_role = 'Not Authenticated';
	let isAuthenticated = false;


	// code executed on page load
	onMount(() => {
		(async () => {
			// wait for the authentication to finish (?)
			await Promise.allSettled([import('../+layout.svelte')]);

			// check if user is authenticated
			let returnValue = await login();
			if (returnValue) {
				token = returnValue;
			}

			// set isAuthenticated flag for conditional rendering
			isAuthenticated = token !== null ? true : false;
			log('admin', 'isAuthenticated: ' + isAuthenticated);

			// decode the token to get the user and role
			if (token) {
				log('admin', 'token is present, decoding... ');
				decodedToken = jwtDecode(token);
				if (decodedToken.sub) {
					current_user = decodedToken.sub;
				}
				// @ts-ignore
				if (decodedToken.role) {
					// @ts-ignore
					current_user_role = decodedToken.role;
					log('admin', 'determined user role');
				}
			}
			
		})();
	});


</script>

<main>
	<div class="container">
		<!-- components that are useful for both regular users and admins -->
		<div class="a grid-item p-3">
			<h2>Konto</h2>
			<GridProfile {current_user} {current_user_role} />
		</div>
		<div class="b grid-item p-3">
			<h2>Client</h2>
			<GridClient {token} />
		</div>

		
		{#if current_user_role === 'admin'}
			<!-- components that require admin role to be used -->
			<div class="c grid-item p-3">
				<h2>Nutzerverwaltung</h2>
				<GridUsers {token} {current_user_role} />
			</div>
			<div class="d grid-item p-3">
				<h2>Serververwaltung</h2>
				<GridServer {token}/>
			</div>
			<div class="e grid-item p-3">
				<h2>Logs</h2>
				<GridLogs {token} {current_user_role} />
			</div>
		{:else}
			<!-- blur the admin components for regular users -->
			<div class="c grid-item p-3 blur">
				<h2>Nutzerverwaltung</h2>
				<GridUsers {token} {current_user_role} />
			</div>
			<div class="d grid-item p-3 blur">
				<h2>Serververwaltung</h2>
				<GridServer {token}/>
			</div>
			<div class="e grid-item p-3 blur">
				<h2>Logs</h2>
				<GridLogs {token} {current_user_role} />
			</div>
		{/if}


	</div>
</main>

<style>

	@import "../../global.css";
	
	main {
		text-align: center;
		padding: 1em;
		margin: 0 auto;
	}


	.blur {
		
		pointer-events: none;
		filter: blur(4px) opacity(0.7);
	}


	.container {
		display: grid;
		grid-template-areas:
			'a c'
			'b c'
			'd d'
			'e e'
			'e e';
		height: fit-content;
		width: 94vw;
		display: grid;
		grid-gap: 2vh;
		overflow-y: auto;
		padding: 1vh;
		padding-right: 0;
	}

	.a {
		grid-area: a;
		overflow-y: auto;
	}

	.b {
		grid-area: b;
		overflow-y: auto;
	}

	.c {
		grid-area: c;
		overflow-y: auto;
	}

	.d {
		grid-area: d;
		overflow-y: auto;
	}

	.e {
		grid-area: e;
		overflow-y: auto;
	}

	h2 {
		font-size: x-large;
		margin: 0;
		padding: 0;
		margin-bottom: 1em;
	}

	.grid-item {
		/* filter: drop-shadow(rgb(210, 248, 174) 5px 5px); */
		padding: 10px;
		padding-top: 0;
		border-radius: 0.5rem;
		text-align: start;
		color: black;
		background-color: #D9D9D933;
	}
</style>
