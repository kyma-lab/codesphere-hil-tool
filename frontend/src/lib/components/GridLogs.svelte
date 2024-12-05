<script>
	import { log } from '$lib/CustomLogger';
	import { LogContainer, LogEntry } from '$lib/Logs';
	import { onDestroy } from 'svelte';
	import refreshIcon from '$lib/assets/icons/Refresh.svg';
	import downloadIcon from '$lib/assets/icons/Download.svg';
	import { fade } from 'svelte/transition';

	/**
	 * @type {string}
	 */
	export let current_user_role;
	/**
	 * @type {string}
	 */
	export let token;

	const apiUrl = import.meta.env.VITE_SERVER_HOST_LOCATION;

	// global variables for showing error messages
	let showErrorAlert = false;
	let errorMessage = '';

	/**
	 * @type {number | undefined}
	 */
	let intervalId;

	// Log Display Component
	let logSource = 'server';
	let logLevel = 'INFO';
	let autoRefresh = false;
	let logs = new LogContainer([], [], []);

	// fetches the logs once the component is initialized
	$: if (token && current_user_role != 'Not Authenticated') {
		init();
	}

	// related to the auto-refresh feature of the logs
	$: if (autoRefresh) {
		intervalId = setInterval(async () => {
			if (current_user_role === 'admin') {
				const fetchedLogs = await getLogs(token);
				logs = fetchedLogs ? fetchedLogs : new LogContainer([], [], []);
				log('admin', 'logs updated');
			}
		}, 5000); // refresh every 5 seconds

		onDestroy(() => {
			clearInterval(intervalId);
		});
	} else {
		clearInterval(intervalId);
	}

	/**
	 * get the logs from the server and initialize the related variables
	 */
	async function init() {
		log('admin', 'GridLogs init');
		log('admin', 'current_user_role: ' + current_user_role);
		log('admin', 'token: ' + token);

		if (current_user_role === 'admin') {
			const fetchedLogs = await getLogs(token);
			if (fetchedLogs) {
				logs = fetchedLogs;
			} else {
				logs = new LogContainer([], [], []);
			}
		} else {
			logs = new LogContainer([], [], []);
		}
	}

	/**
	 * converts the log level to an integer for comparison
	 * @param {string} level
	 */
	function logLevelToInt(level) {
		switch (level) {
			case 'DEBUG':
				return 0;
			case 'INFO':
				return 1;
			case 'WARNING':
				return 2;
			case 'ERROR':
				return 3;
			case 'CRITICAL':
				return 4;
			default:
				return 0;
		}
	}

	/**
	 * fetches the logs from the server
	 * todo: move call to API.js
	 * @param {string} token
	 */
	async function getLogs(token) {
		try {
			const response = await fetch(apiUrl + '/api/logs', {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!response.ok) {
				console.error('Error fetching logs');
				return;
			}

			let data = await response.json();
			log('admin', 'retrieved logs');

			data.logs.server.reverse();
			data.logs.trainer.reverse();
			data.logs.predictor.reverse();

			return new LogContainer(
				data.logs.server.map(
					(/** @type {{ timestamp: string; level: string; message: string; }} */ log) =>
						new LogEntry(log.timestamp, log.level, log.message)
				),
				data.logs.trainer.map(
					(/** @type {{ timestamp: string; level: string; message: string; }} */ log) =>
						new LogEntry(log.timestamp, log.level, log.message)
				),
				data.logs.predictor.map(
					(/** @type {{ timestamp: string; level: string; message: string; }} */ log) =>
						new LogEntry(log.timestamp, log.level, log.message)
				)
			);
		} catch (error) {
			showErrorMessage('Fehler beim Abrufen der Logs');
			console.error('Error fetching logs', error);
		}
	}

	/**
	 * refreshes the logs (request to server)
	 */
	async function refreshLogs() {
		let fetchedLogs = await getLogs(token);

		if (!fetchedLogs) {
			showErrorMessage('Logs konnten nicht aktualisiert werden');
			return;
		} else {
			logs = fetchedLogs;
		}
	}

	/**
	 * downloads the logs as a JSON file to the user's device
	 */
	async function downloadLogs() {
		const element = document.createElement('a');
		const file = new Blob([JSON.stringify(logs)], { type: 'text/plain' });
		element.href = URL.createObjectURL(file);
		element.download = 'logs.json';
		document.body.appendChild(element); // Required for this to work in FireFox
		element.click();
	}

	/**
	 * shows an error message for a short time
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
		<!-- Information -->
		<h3>Information</h3>
		<span class="infotext">
			Wählen Sie die Logquelle aus, um die entsprechenden Logeinträge anzuzeigen. Logs können nach
			Log-Level gefiltert werden. Zeitangaben sind in UTC, also 2 Stunden hinter der deutschen
			Zeitzone. Wenn Auto-Refresh aktiviert ist, werden die Logs alle 5 Sekunden automatisch
			aktualisiert. Es werden unabhängig vom gewählten Log-Level nur die letzten 500 Events vom
			Server abgerufen und danach basierend auf dem gewählten Log-Level gefiltert.
		</span>
	</div>

	<!--     Controlbox -->
	<div class="d-flex m-2 justify-content-between">
		<div class="d-flex w-100 align-items-end">
			<div class="d-flex align-items-center w-100">
				<button class="m-1 p-2 button d-flex border-0" on:click={() => refreshLogs()}>
					<!-- svelte-ignore a11y-missing-attribute -->
					<img src={refreshIcon} class="custom-icon" />
				</button>

				<button class="m-1 p-2 button d-flex border-0" on:click={() => downloadLogs()}>
					<!-- svelte-ignore a11y-missing-attribute -->
					<img src={downloadIcon} class="custom-icon" />
				</button>

				<div class="custom-switch small border-0 form-check form-switch m-1 p-1">
					<input
						class="m-1 form-check-input hover"
						type="checkbox"
						bind:checked={autoRefresh}
						id="autoRefreshCheckbox"
					/>
					<label class="mx-1 small form-check-label text-black" for="autoRefreshCheckbox"
						>Auto Refresh</label
					>
				</div>
			</div>

			<div class="m-1">
				<h3>Source</h3>
				<select
					class="form-select d-flex source-selector-dropdown"
					id="logSource"
					bind:value={logSource}
				>
					<option value="server">Server</option>
					<option value="predictor">Predictor</option>
					<option value="trainer">Trainer</option>
				</select>
			</div>

			<div class="m-1">
				<h3>Level</h3>
				<select
					class="form-select d-flex level-filter-dropdown"
					id="logLevel"
					bind:value={logLevel}
				>
					<option value="DEBUG">Debug</option>
					<option value="INFO">Info</option>
					<option value="WARNING">Warning</option>
					<option value="ERROR">Error</option>
					<option value="CRITICAL">Critical</option>
				</select>
			</div>
		</div>
	</div>

	<!-- Logbox -->
	<div id="logbox" class="logentrybox d-flex border rounded">
		{#each logs.getBySource(logSource) as log}
			{#if logLevelToInt(log.level) >= logLevelToInt(logLevel)}
				<div class="logentry m-1 p-1 text-start rounded">
					<span class={log.level}>
						{log.timestamp} - {log.level} - {log.message}
					</span>
				</div>
			{/if}
		{/each}
	</div>

	{#if showErrorAlert}
		<div transition:fade={{ duration: 400 }} class="alert p-2 m-2" role="alert">
			{errorMessage}
		</div>
	{/if}
</div>

<style>
	@import '../../global.css';

	.source-selector-dropdown {
		width: 200px;
		display: inline-block;
	}

	.level-filter-dropdown {
		width: 200px;
		display: inline-block;
	}

	.button {
		cursor: pointer;
		position: relative;
		display: inline-flex;
		transition: background-color 0.3s ease, color 0.3s ease;
		border-radius: 20px;
	}

	.alert {
		font-weight: 800;
		color: red;
		background-color: none;
	}

	.custom-icon {
		height: 1em;
		padding: 0;
	}

	.custom-switch {
		border-radius: 20px;
		background-color: rgba(233, 233, 237, 255);
	}

	.hover:hover {
		cursor: pointer;
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

	.logentrybox {
		max-height: 30vh;
		min-height: 30vh;
		overflow-y: auto;
		scroll-behavior: smooth;
		background-color: white;
		flex-direction: column-reverse; /* reverse the order of the elements displayed (reverse log list beforehand) */
	}

	.logentry {
		background-color: #f0f0f0;
		font-family: monospace;
		font-size: smaller;
	}

	.INFO {
		color: blue;
	}
	.WARNING {
		color: orange;
	}
	.ERROR {
		color: red;
	}

	.DEBUG {
		color: rgba(128, 128, 128, 0.596);
	}

	.CRITICAL {
		color: red;
		font-weight: bold;
	}
</style>
