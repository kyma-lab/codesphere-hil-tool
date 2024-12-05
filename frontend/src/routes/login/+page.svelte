<script context="module">
	/* these functions are exported and available globally */
	import { jwtDecode } from 'jwt-decode';
	import { AuthorizationError } from '$lib/Errors.js';

	/**
	 * checks if a valid JWT is stored in the local storage
	 * if not, the user is redirected to the login page
	 * is used by many other components to check session state
	 */
	export async function login() {
		let token = await setJWT();

		let DEBUG = false;
		let isAuthenticated = false;

		if (!DEBUG) {
			if (token === undefined) {
				log('access_control', 'no token found, redirecting to login');
				jwt.set(null);
				goto('/login');
			} else {
				let decodedToken = jwtDecode(token);
				let currentTimestamp = Math.floor(Date.now() / 1000);

				if (decodedToken.exp === undefined) {
					log('access_control', 'no expiration date found in token, redirecting to login');
					jwt.set(null);
					localStorage.removeItem('jwt');
					goto('/login');
				} else if (decodedToken.exp < currentTimestamp) {
					log('access_control', 'token expired, redirecting to login');
					jwt.set(null);

					localStorage.removeItem('jwt');
					goto('/login');
				} else {
					log('access_control', 'token is valid');

					isAuthenticated = true;
				}
			}
		} else {
			isAuthenticated = true;
		}

		return token;
	}

	/**
	 * logs out the user by removing the JWT from the local storage,
	 * also adds the token to the blacklist in the backend and
	 * redirects the user to the login page
	 * @param {string} token
	 */
	export async function logout(token) {
		if (browser) {
			localStorage.removeItem('jwt');
		}

		// add error handling, user feedback
		let res = await db_logout(token);
		log('access_control', 'logout successful');

		await goto('/login');
	}

	/**
	 * extracts the role from the JWT token
	 * and returns it (as string) ("user" or "admin")
	 * todo: use enum here instead
	 * @param {string} token
	 */
	export async function getRole(token) {
		try {
			let role = JSON.parse(atob(token.split('.')[1])).role;
			return role;
		} catch (error) {
			console.error('error getting role from token', error);
			return 'user';
		}
	}

	/**
	 * checks if a valid JWT is stored in the local storage and returns it
	 * if not, returns undefined
	 */
	export async function setJWT() {
		let token = localStorage.getItem('jwt');

		if (token === null) {
			log('access_control', 'found no token in local storage');
			return undefined;
		} else {
			log('access_control', 'found token in local storage');
			return token;
		}
	}
</script>

<script>
	import { goto } from '$app/navigation';
	import { jwt } from './../../stores/store.js'; // import the token store
	import { fade } from 'svelte/transition';
	import { browser } from '$app/environment';
	import { db_login, db_logout } from '$lib/API.js';
	import { log } from '$lib/CustomLogger.js';

	// initialize variables with default values
	let serverError = false;
	let errorMessage = '';
	let isLoading = false;
	let username = '';
	let password = '';

	/**
	 * displays an boostrap-alert with the provided error message for 3 seconds
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
	 * handles the login form submission (should be moved to API.js)
	 */
	async function handleSubmit() {
		isLoading = true;

		try {
			let access_token = await db_login(username, password);

			jwt.set(access_token);
			localStorage.setItem('jwt', access_token);

			// reset form values
			username = '';
			password = '';

			// navigate to the home page
			log('access_control', 'login successful');
			goto('/');
		} catch (error) {

			console.log(error);
			if (error instanceof AuthorizationError) {
				isLoading = false;
				errorMessage = 'Benutzername oder Passwort falsch.';
				showErrorMessage(errorMessage);
				return;
			} else {
				
				isLoading = false;
				errorMessage =
					'Beim Herstellen der Verbindung zum Server ist ein Problem aufgetreten. Bitte versuchen Sie es später noch einmal.';
				showErrorMessage(errorMessage);
			}
		}
	}
</script>

<div class="container text-center">
	<div class="row align-items-center h-70vh">
		<div class="col" />
		<div class="col align-self-center">
			{#if serverError}
				<!-- shows feedback if login fails -->
				<div class="alert alert-warning" transition:fade={{ duration: 500 }} role="alert">
					{errorMessage}
				</div>
			{/if}

			<div class="container">
				<h1>Login</h1>

				<form on:submit|preventDefault={handleSubmit}>
					<!-- login form  -->
					<div class="form-outline">
						<input
							type="username"
							id="username"
							placeholder="Benutzername"
							bind:value={username}
							required
							class="form-control"
						/>
						<label class="form-label" for="username" />
					</div>
					<div class="form-outline">
						<input
							type="password"
							id="password"
							placeholder="Passwort"
							bind:value={password}
							required
							class="form-control"
						/>
						<label class="form-label" for="password" />
					</div>
					<button id="login" type="submit" class="btn btn-primary" disabled={isLoading}>
						Login
					</button>
				</form>
			</div>
		</div>
		<div class="col" />
	</div>
</div>

<style>
	@import '../../global.css';
</style>
