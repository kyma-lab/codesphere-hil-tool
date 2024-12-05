<!-- component used on the settings page to display the content of a subtopic -->
<script>
	import DocumentationTopic from '$lib/DocumentationTopic';

	/** The subtopic to be displayed. Subtopic title 'Video' is special key to show video instead of text.
	 * @type {DocumentationTopic} subtopic - The subtopic for the documentation topic.
	 */
	export let subtopic;
	
</script>

{#if subtopic.get_title() == 'Video'}
	<!-- subtopic title video is special key to show video instead of text -->

	<!-- svelte-ignore a11y-media-has-caption -->
	<a class="m-4" href="https://youtu.be/r5e4_d6t-Cg" target="_blank" rel="noopener noreferrer">
	 <button class="yt-button">
		Hier klicken um Anleitungsvideo auf <strong>YouTube</strong> anzusehen
		
	 </button>
	</a>




{:else}
	<!-- default case is showing the textual content of the subtopic -->
	<div class="mx-3">
		<section id={subtopic.get_title()}>
			<!-- show title for the subtopic, if available -->
			{#if subtopic.get_title() != ''}
				<h3 class="text-white rounded p-1">{subtopic.get_title()}</h3>
			{/if}

			<!-- show main textual content for the subtopic -->
			<p>{subtopic.get_content()}</p>

			<!-- show bullet points if available for this subtopic -->
			{#if subtopic.get_steps().length > 0}
				<ul>
					{#each subtopic.get_steps() as step}
						<li class="rounded m-1 p-1">{step}</li>
					{/each}
				</ul>
			{/if}
		</section>
	</div>
{/if}

<style>
	@import '../../global.css';
	@import '../../../static/bootstrap.min.css';

	.yt-button {
		background-color: #ff0000;
		color: white;
		border: none;
		padding: 0.5em;
		border-radius: 5px;
		cursor: pointer;
		box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.25);
		margin-top: 20px;
		margin-bottom: 20px;
	}

	.yt-button:hover {
		background-color: #ee0000;
	}

	h3 {
		font-size: medium;
		background-color: #9999ff;
		margin-top: 1em;
		width: fit-content;
		cursor: default;
	}

	li {
		width: fit-content;
	}

	li:hover {
		background-color: #f0f0f0;
		width: fit-content;
		animation: shake 0.5s;
	}

	/* animate the shake of the bullet points when hovering over them */
	@keyframes shake {
		0% {
			transform: translateX(0);
		}
		30% {
			transform: translateX(3px);
		}
		70% {
			transform: translateX(-3px);
		}
		100% {
			transform: translateX(0);
		}
	}

	ul {
		list-style-type: '👉  ';
	}

	p {
		text-align: justify;
	}
</style>
