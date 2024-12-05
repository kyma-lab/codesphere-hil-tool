<!-- AnnotationLabel.svelte -->
<script>
	export let handleAnnotationClick;
	export let annotationsForWords;
	export let index;
</script>

<!-- svelte-ignore a11y-no-static-element-interactions -->
<!-- svelte-ignore a11y-click-events-have-key-events -->
<span
	id="annotation-click"
	on:click|stopPropagation={handleAnnotationClick}
	class="annotation-label"
	data-start-index={annotationsForWords[index]?.start_word_index}
	data-end-index={annotationsForWords[index]?.end_word_index}
	data-label={annotationsForWords[index]?.label}
>
	{annotationsForWords[index].label}
</span>

<style>
	.annotation-label {
		cursor: pointer;
		position: relative;
		bottom: 3px;
		font-size: 60%;
		background-color: white;
		color: black;
		border-radius: 13px;
		padding-right: 5px;
		padding-left: 5px;
		padding-top: 2px;
		padding-bottom: 2px;
	}
</style>
