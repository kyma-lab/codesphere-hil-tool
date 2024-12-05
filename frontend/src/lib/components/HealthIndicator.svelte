<script>
	// name of the service, displayed next to the indicator
	export let serviceName;

	// is the time since the last heartbeat
	export let heartbeat;

	// defines color of the indicator
	let statusColor = 'red';

	// defines text to display as tooltip
	let displayText = 'Error';

	// Reactive statement to update statusColor when heartbeat changes
	$: {
		if (heartbeat == 'Error') {
			statusColor = 'red';
			displayText = 'Offline';
		} else if (heartbeat == 'Unavailable') {
			statusColor = 'yellow';
			displayText = 'Unavailable';
		} else {
			statusColor = 'green';
			displayText = 'Online';
		}
	}
</script>

<div class="d-flex flex-row align-items-center rounded border p-1 m-1">
	<!-- colored dot indicating the status of the service -->
	<div class="indicator m-1" style="--status-color: {statusColor}">
		<!-- tooltip to show text for the satus -->
		<div class="tooltip">{displayText}</div>
	</div>

	<!-- label with the service name -->
	<div class="indicator-label">
		{serviceName}
	</div>
</div>

<style>
	.indicator {
		display: inline-block;
		width: 20px;
		height: 20px;
		border-radius: 50%;
		background-color: var(--status-color);
		position: relative;
	}

	.indicator-label {
		margin-left: 5px;
		margin-right: 3px;
		font-size: smaller;
	}

	.tooltip {
		visibility: hidden;
		background-color: black;
		color: #fff;
		text-align: center;
		border-radius: 5px;
		padding: 5px;
		position: absolute;
		z-index: 1;
		bottom: 125%; /* Position above the indicator */
		left: 50%;
		margin-left: -60px;
		width: 120px;
		opacity: 0;
		transition: opacity 0.3s;
	}

	.indicator:hover .tooltip {
		visibility: visible;
		opacity: 1;
	}
</style>
