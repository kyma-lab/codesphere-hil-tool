<script>
	import { change_password, db_add_user } from '$lib/API';
	import { log } from '$lib/CustomLogger';
	import { Tooltip } from '@svelte-plugins/tooltips';
	import LoadingButton from './LoadingButton.svelte';
	import { fade } from 'svelte/transition';


    const apiUrl = import.meta.env.VITE_SERVER_HOST_LOCATION;

    /**
	 * @type {string}
	 */
	export let token;
    /**
	 * @type {string}
	 */
     export let current_user_role;



	$: if (token && current_user_role != "Not Authenticated") {
        init();
    }



	let users = [];
	let usernameInput = '';
	let passwordInput = '';
	let newPasswords = {};

	let showErrorAlert = false;
	let errorMessage = '';

	// for storing the input values for the new password fields
	$: users.forEach((user) => {
		if (!(user in newPasswords)) {
			// @ts-ignore
			newPasswords[user] = '';
		}
	});


	async function init() {
	
		if (current_user_role === 'admin') {
				users = await getUsers(token);
			} else {
				users = [];
			}
	}


    	/**
	 * @param {string} token
	 */
	async function getUsers(token) {
		try {
			const response = await fetch(apiUrl + '/api/get_users', {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!response.ok) {
				console.error('Error fetching users');
				return;
			}

			let data = await response.json();
			log('admin', 'retrieved registered users');

			// extract the username for each user and store it in the users array
			// @ts-ignore
			return data.users.map((user) => user.username);
		} catch (error) {
			console.error('Error fetching users', error);
		}
	}


		/**
	 * @param {string} token
	 * @param {string} username
	 * @param {string} password
	 */
	 async function addUser(token, username, password) {
		const res = await db_add_user(token, username, password);

		if (res.status != 200) {
			console.error('Registration failed 01');
			showErrorMessage('Nutzer konnte nicht hinzugefuegt werden');
			throw new Error('Registration failed 01');
		} else {
			users = [...users, username];
			//showSuccessMessage('Nutzer erfolgreich hinzugefuegt');

			// reset the form
			usernameInput = '';
			passwordInput = '';
			return;
		}
	}

	/**
	 * @param {string} token
	 * @param {string} username
	 */
	async function changePassword(token, username) {
		// @ts-ignore
		const newPassword = newPasswords[username];
		const result = await change_password(username, token, newPassword);
		// reset the new password field
		// @ts-ignore
		newPasswords[username] = '';

		if (result.status == 200) {
			
			return;
			//showSuccessMessage('Passwort erfolgreich geändert');
		} else {
			showErrorMessage('Passwort konnte nicht geändert werden');
			throw new Error('Password change failed');
		}
	}

	// send delete request to the server
	/**
	 * @param {string} username
	 * @param {string} token
	 */
	async function deleteUser(token, username) {
		try {
			const response = await fetch(apiUrl + '/api/delete_user', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({ username })
			});

			if (!response.ok) {
				console.error('User deletion failed 01');
				showErrorMessage('User deletion failed');
				throw new Error('User deletion failed 01');
			} else {
				users = users.filter((user) => user !== username);
				return;
			}
		} catch (error) {
			console.error('User deletion failed 02');
			console.error(error);
			showErrorMessage('User deletion failed');
			throw new Error('User deletion failed 02');
		}
	}

		/**
	 * @param {string} msg
	 */
	 function showErrorMessage(msg) {
		showErrorAlert = true;
		errorMessage = msg;
		setTimeout(() => {
			showErrorAlert = false;
		}, 3000);
	}

</script>

<div>
	<div class="d-flex flex-column align-items-start m-2">
		<h3>Information</h3>
		<p class="infotext text-start">
            Nutzername und Passwort müssen jeweils aus mindestens 4 und maximal 20 Zeichen
            bestehen. Es sind nur Buchstaben und Zahlen erlaubt.
            Leerzeichen am Anfang und Ende von Nutzername und Passwort werden ignoriert.
            Nutzernamen müssen einzigartig sein, andernfalls wird der Nutzer nicht angelegt.</p>
	</div>

    <h3 class="m-2">Verwalten</h3>
	<div class="user-list flex-column align-items-start rounded d-flex m-2 mx-3">
        
		<div class="d-flex m-1 p-1 w-100 flex-column align-items-start">
			{#each users as user}
				<div class="d-flex m-1 p-1 w-99">
					<div class="d-flex w-100 flex-row justify-content-between align-items-center">
						<span class="username-element p-2">{user}</span>

						<div class="d-flex align-items-center">

							<input
                                class="m-1 p-1 input-password border rounded"
								type="text"
								id="newPassword"
								placeholder="Neues Passwort"
								bind:value={newPasswords[user]}
							/>

							<LoadingButton style="min-width: 140px;" buttonText="Passwort ändern" onClick={() => changePassword(token, user)}> </LoadingButton>


							<Tooltip content="Nutzer und alle assoziierten Daten löschen" position="left">

								<LoadingButton style="min-width: 97px;" classes="m-1" buttonText="Entfernen" onClick={() => deleteUser(token, user)}> </LoadingButton>

							</Tooltip>
						</div>
					</div>
				</div>
			{/each}
		</div>
	</div>

	<div class="mx-3 flex-row rounded d-flex m-2">
		<div class="d-flex input-container p-1">
			<input
				class="m-1 p-1 custom-input border rounded"
				type="text"
				bind:value={usernameInput}
				placeholder="Benutzername"
			/>
			<input
				class="m-1 p-1 custom-input border rounded"
				type="text"
				bind:value={passwordInput}
				placeholder="Passwort"
			/>

			<LoadingButton style="font-size:smaller; width: 30px; height: 30px;" classes="m-1" buttonText="+" onClick={() => addUser(token, usernameInput, passwordInput)}>
				
			</LoadingButton>	
		</div>


	</div>

		{#if showErrorAlert}
		<div transition:fade={{ duration: 400 }} class="alert p-2" role="alert">
			{errorMessage}
		</div>
		{/if}
</div>

<style>
	    @import "../../global.css";

	.input-password {
		width: 180px; display: inline; font-size: smaller;
	}

	.custom-input {
		font-size: smaller;
		width: 100px;
		display: flex;
		flex: 1 1 0; /* Flex-grow: 1; flex-shrink: 1; flex-basis: 0; */
		min-width: 0; /* Ensure it can shrink */
	}

	.alert {
		font-weight: 800;
		color: red;
		background-color: none;
	}

	.input-container {
		justify-content: space-around; 
		background-color: white;
		flex: 0 1 500px; 
		border-radius: 0.5rem;
	}

	.user-list {
		width: 97%;
		min-height: 20%;
		background-color: white;
	}

	h3 {
		font-size: smaller;
		font-weight: bold;
		margin-bottom: 0.5em;
	}

	.infotext {
		font-weight: lighter;
        color: #616161;
		padding-left: 10px;
	}
</style>
