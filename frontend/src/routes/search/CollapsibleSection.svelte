<script>
	// based on suggestions from:
	// source:: https://svelte.dev/repl/a5f4d395b15a44d48a6b2239ef705fc4?version=3.35.0
	// Inclusive Components by Heydon Pickering https://inclusive-components.design/collapsible-sections/
	export let headerText;
	import plusIcon from '$lib/assets/icons/Plus.svg';

	let expanded = false;
</script>

<div class="collapsible">
	<h4>
		<button aria-expanded={expanded} on:click={() => (expanded = !expanded)} id="collapse-button"
			>{headerText}
			<img class="plus-icon m-1" src={plusIcon} alt="Expand" />
		</button>
	</h4>

	<div class="contents" hidden={!expanded}>
		<slot />
	</div>
</div>

<style>
	.collapsible {
		border-bottom: 1px solid var(--gray-light, #eee);
	}

	h4 {
		margin: 0;
	}

	button {
		background-color: var(--background, #fff);
		color: var(--gray-darkest, #282828);
		display: flex;
		justify-content: space-between;
		width: 100%;
		border: none;
		margin: 0;
		padding: 1em 0.5em;
	}

	button[aria-expanded='true'] {
		border-bottom: 1px solid var(--gray-light, #eee);
	}

	.plus-icon {
		cursor: default;
	}
</style>
