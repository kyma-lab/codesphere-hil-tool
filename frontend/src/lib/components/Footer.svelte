<script>
	export let footerHeight = '30px';
</script>

<footer style:--footer-height={footerHeight}>
	<div class="container">
		<div class="row">
			<div class="col text-center">
				<ul class="list-inline m-1">
					<li class="list-inline-item p-1">
						<a class="brand" href="#">
							<p class="mb-0">
								&copy; 2024 Friedrich-Schiller-Universität Jena. Licensed under the <a href="https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12" target="_blank">EUPL v1.2</a>.
							</p></a
						>
					</li>
					<li class="list-inline-item p-1"><a target="_blank" href="https://www.fmi.uni-jena.de/11110/arbeitsgruppe-offenes-design-digitaler-verwaltungsarchitekturen">openDVA</a></li>
					<li class="list-inline-item p-1"><a href="./datenschutz">Datenschutz</a></li>
					<li class="list-inline-item p-1"><a href="./impressum">Impressum</a></li>
					<li class="list-inline-item p-1"><a href="mailto:robin.erd@uni-jena.de">Kontakt</a></li>
				</ul>
			</div>
		</div>
	</div>
</footer>

<style>

	.brand {
		cursor: default;
	}
	footer {
        position: sticky; 
        top: 100vh;
		left: 0;
		width: 100%;
		height: var(--footer-height);
		background-color: #f8f9fa; /* Bootstrap 5 light background color */
		padding: 1rem; /* Add some padding */
		display: flex;
		justify-content: center;
		align-items: center;
		font-size: smaller;
	}

	footer a {
		color: grey;
		text-decoration: none;
	}

</style>
