<script>
	/**
	 * @type {() => any}
	 */
	export let onClick; // Function to handle the button's action
	export let buttonText = 'Click Me'; // Text to display on the button
	export let style = ''; // Additional classes to apply to the button
	export let classes = ''; // Additional styles to apply to the button

	let isLoading = false;
	let isSuccess = false;
	let isError = false;

	async function handleClick() {
		isLoading = true;
		isSuccess = false;
		isError = false;

		try {
			// wait for 0.4 seconds
			await new Promise((r) => setTimeout(r, 400));

			await onClick(); // Wait for the passed function to complete
			isSuccess = true;
		} catch (error) {
			isError = true;
		} finally {
			isLoading = false;
			setTimeout(() => {
				isSuccess = false;
				isError = false;
			}, 1000);
		}
	}
</script>

<button
	{style}
	class="button {isLoading ? 'loading' : ''} {isSuccess ? 'success' : ''} {isError
		? 'error'
		: ''} {classes}"
	on:click={handleClick}
	disabled={isLoading}
>
	{#if isLoading}
		.
	{:else if isSuccess}
		✔
	{:else if isError}
		✖
	{:else}
		{buttonText}
	{/if}
</button>

<style>
	.button {
		padding: 5px;
		font-size: smaller;
		border: none;
		border-radius: 5px;
		cursor: pointer;
		position: relative;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		transition: background-color 0.3s ease, color 0.3s ease;
	}

	.loading {
		color: transparent;
		position: relative;
	}

	.loading::after {
		content: '';
		border: 2px solid #f3f3f3;
		border-top: 2px solid #333;
		border-radius: 50%;
		width: 20px;
		height: 20px;
		animation: spin 1s linear infinite;
		position: absolute;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.success {
		background-color: green;
		color: white;
	}

	.error {
		background-color: red;
		color: white;
	}
</style>
