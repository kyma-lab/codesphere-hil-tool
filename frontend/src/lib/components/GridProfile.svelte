<script>
	export let current_user;
	export let current_user_role;
</script>

<div>
	<div class="d-flex flex-column align-items-start w-50 m-2">
		<h3>Benutzername</h3>
		<span class="infotext username-highlight rounded p-1 px-2">{current_user}</span>
	</div>
	<div class="d-flex flex-column align-items-start w-50 m-2">
		<h3>Rolle</h3>
		<span class="infotext role-highlight rounded p-1 px-2">{current_user_role}</span>
	</div>
</div>

<style>
	.username-highlight {
		background-color: #00e5ff;
	}

	.role-highlight {
		background-color: #1de9b6;
	}

	h3 {
		font-size: smaller;
		font-weight: bold;
		margin-bottom: 0.5em;
	}

	.infotext {
		color: #000000;
		padding-left: 10px;
	}
</style>
