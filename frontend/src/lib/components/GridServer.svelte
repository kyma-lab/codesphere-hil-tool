<script>
	import { Tooltip } from '@svelte-plugins/tooltips';
	import LoadingButton from './LoadingButton.svelte';
	import { fade } from 'svelte/transition';
	import HealthIndicator from './HealthIndicator.svelte';
	import { SystemStatus } from '$lib/SystemStatus';
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';

	/**
	 * token received from parent component
	 * @type {string}
	 */
	export let token;


	const apiUrl = import.meta.env.VITE_SERVER_HOST_LOCATION;

	// global variables for showing error messages
	let showErrorAlert = false;
	let errorMessage = '';

	// send clear request to the server
	// TODO: this should be moved into the API.js file
	async function clearRabbitMQ() {
		try {
			const response = await fetch(apiUrl + '/api/reset_rabbitmq', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				}
			});

			if (!response.ok) {
				// Throw an error to trigger the catch block and reject the promise
				showErrorMessage('Fehler beim Zurücksetzen von RabbitMQ');
				throw new Error('Failed to reset RabbitMQ');
			} else {
				// Resolve the promise successfully
				return;
			}
		} catch (error) {
			// Log the error or handle it accordingly
			showErrorMessage('Fehler beim Zurücksetzen von RabbitMQ');
			console.error('Error clearing RabbitMQ:', error);
			// Reject the promise with an error
			throw error;
		}
	}

	/**
	 * Show an error message for a short period of time
	 * @param {string} msg
	 */
	function showErrorMessage(msg) {
		showErrorAlert = true;
		errorMessage = msg;
		setTimeout(() => {
			showErrorAlert = false;
		}, 3000);
	}

	// local store for system status
	// required to pass down changes within SystemStatus class to child components reactively
	const systemStatus = writable(new SystemStatus());

	// update system status on mount
	onMount(async () => {
		const status = new SystemStatus();
		await status.update();
		systemStatus.set(status);
	});
</script>

<div>

	<div class="d-flex flex-column align-items-start m-2">
		<h3>System Status</h3>
		<p class="infotext text-start m-0">
			Predictor und Trainer werden als Offline angezeigt, wenn zum Zeitpunkt der Abfrage alle Worker 
			mit einem Task beschaeftigt sind.
		</p>
		<div class="d-flex flex-row">
			<HealthIndicator serviceName="Predictor" heartbeat={$systemStatus.predictor} />
			<HealthIndicator serviceName="Trainer" heartbeat={$systemStatus.trainer} />
			<HealthIndicator serviceName="BiLSTM-CRF" heartbeat={$systemStatus.bilstm_crf} />
			<HealthIndicator serviceName="XLM-R" heartbeat={$systemStatus.xlm_r} />
		</div>
	</div>

	<div class="d-flex flex-column align-items-start m-2">
		<h3>Information</h3>
		<p class="infotext text-start">
			Verwenden Sie die nachstehenden Schaltflächen zur Fehlerbehebung. Um die Datenbank für einen
			bestimmten Benutzer zurückzusetzen, löschen Sie einfach den Benutzer und erstellen Sie ihn
			neu. Diese Funktionen sollten nicht waehrend der Nutzung der Anwendung verwendet werden. Nach
			Nutzung der Funktionen muessen ggf. alle Backend-Services neu gestartet werden.
		</p>
	</div>

	<div class="d-flex flex-column align-items-start m-2">
		<h3>Reset</h3>
		<Tooltip
			content="Dies löscht alle Tasks in der Warteschlange des RabbitMQ-Dienstes und setzt ihn auf den
    Ausgangszustand zurückgesetzt."
			position="left"
		>
			<LoadingButton
				style="min-width: 210px;"
				buttonText="RabbitMQ zurücksetzen"
				onClick={() => clearRabbitMQ()}
			/>
		</Tooltip>
	</div>

	{#if showErrorAlert}
		<div transition:fade={{ duration: 400 }} class="alert p-2" role="alert">
			{errorMessage}
		</div>
	{/if}
</div>

<style>
	@import "../../global.css";
	.alert {
		font-weight: 800;
		color: red;
		background-color: none;
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
