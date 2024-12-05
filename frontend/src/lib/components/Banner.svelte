<!-- top of page banner with statement regarding website being in closed beta -->

<script>
	export let footerHeight = '25px';
</script>

<div
	class="hint-box w-100 p-0 d-flex align-items-center justify-content-center"
	style:--footer-height={footerHeight}
>
	<div class="container">
		<div class="row">
			<div class="col text-center">
				<ul class="list-inline m-1">
					<li class="list-inline-item p-1">⚠️</li>
					<li class="list-inline-item p-1">
						Dieses Tool befindet sich in einer geschlossenen Testphase. Keine sensitiven Daten
						eingeben.
					</li>
					<li class="list-inline-item p-1">⚠️</li>
				</ul>
			</div>
		</div>
	</div>
</div>

<style>
	.hint-box {
		position: sticky;
		bottom: 100vh;
		left: 0;
		height: var(--footer-height);
		background-color: #e67e22; /* Bootstrap 5 light background color */
		font-size: smaller;
		z-index: 1002;
		color: white;
	}
</style>
