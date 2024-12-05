<script>
	export let topics;

	// scrolls to the section with the given id

	/**
	 * @param {string} id
	 */
	function scrollToSection(id) {
		const element = document.getElementById(id);
		if (element) {
			element.scrollIntoView({ behavior: 'smooth' });
		}
	}
</script>

<nav class="toc p-4 h-50">
	<ul class="toc-list">
		{#each Object.keys(topics) as topic}
			<li>
				<button
					class="d-block m-1 p-1 border-0 position-relative"
					on:click={() => scrollToSection(topic)}
				>
					<b> {topic}</b></button
				>

				<!-- subtopics make the toc too long for the page, need collapsible subtopics first -->

				<!-- 							<ul class="toc-list">
                    {#each topics[topic] as subtopic}
                        {#if subtopic.get_title() != ''}
                            <li class="p-0 m-0">
                                <button class="m-1 p-0" on:click={() => scrollToSection(topic)}>{subtopic.get_title()}</button>
                            </li>
                        {/if}
                    {/each}
                </ul> -->
			</li>
		{/each}
	</ul>
</nav>

<style>
	@import '../../global.css';

	.toc {
		background-color: #f0f0f0;
		color: #333;
		position: sticky;
		max-height: 85vh;
		top: 5vh;
	}

	/* removes the default list style */
	.toc-list {
		list-style-type: none;
	}

	.toc button {
		background: none;
		text-align: left;
		width: 100%;
		cursor: pointer;
		color: #333;
		font-weight: 200;
	}

	/* for the underline effect on hover */
	.toc button::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		width: 0;
		height: 100%;
		transition: width 0.3s ease;
	}

	/* for the underline effect on hover */
	.toc button::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		width: 0;
		height: 100%;
		border-bottom: 2px solid #333;
		transition: width 0.3s ease;
	}

	/* for the underline effect on hover */
	.toc button:hover::before {
		width: 100%;
	}

	/* for the underline effect on hover */
	.toc button:hover::after {
		width: 100%;
	}
</style>
