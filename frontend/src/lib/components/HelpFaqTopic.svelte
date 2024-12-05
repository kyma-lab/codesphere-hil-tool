<!-- component used on the settings page to display a FAQ question and answer -->
<script>
	export let question;
</script>

<div class="mx-3">
	<section id={question}>
		<h3 class="text-white rounded p-1">{question.get_title()}</h3>
		<p>{question.get_content()}</p>
		<ol>
			{#each question.get_steps() as step}
				<li class="rounded m-1 p-1">{step}</li>
			{/each}
		</ol>
	</section>
</div>

<style>
	@import '../../global.css';
	@import '../../../static/bootstrap.min.css';

	h3 {
		font-size: medium;
		background-color: #9999ff;
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

	p {
		text-align: justify;
	}
</style>
