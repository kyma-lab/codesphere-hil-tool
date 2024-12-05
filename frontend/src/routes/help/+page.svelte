<script>
	import { questions, topics } from './topics';
	import HelpFaqTopic from '$lib/components/HelpFaqTopic.svelte';
	import HelpDocuTopic from '$lib/components/HelpDocuTopic.svelte';
	import HelpToc from '$lib/components/HelpToc.svelte';


</script>

<!-- main content for about / help page  -->
<main class="w-80">
	<div class="row">
		<!-- left hand side table of contents -->
		<div class="col-3">
			<HelpToc {topics} />
		</div>

		<!-- right hand side main content -->
		<div class="col-9">
			<div class="content m-3">
				{#each Object.keys(topics) as topic}
					<section id={topic} class="border rounded p-4 mt-2">
						<h2>{topic}</h2>
						{#each topics[topic] as subtopic}
							<HelpDocuTopic {subtopic} />
						{/each}
					</section>
				{/each}

				<!-- section for frequently asked questions, same principle as above -->
				<section id="FAQ" class="border rounded p-4 mt-2">
					<h2>Häufig gestellte Fragen</h2>
					{#each questions as question}
						<HelpFaqTopic {question} />
					{/each}
				</section>
			</div>
		</div>
	</div>
</main>

<style>
	@import '../../global.css';
	@import '../../../static/bootstrap.min.css';


	.content {
		flex: 1;
		padding: 1em;
	}

	h2 {
		font-size: larger;
		background-color: #9999ff;
		border-radius: 5px;
		padding: 0.4em;
		color: white;
		cursor: default;
	}

</style>
