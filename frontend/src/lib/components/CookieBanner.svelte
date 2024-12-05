<!-- CookieBanner.svelte -->

<script>
	import { log } from '$lib/CustomLogger';
	import { onMount } from 'svelte';

	/**
	 * @type {boolean}
	 */
	let showBanner;

	function acceptCookies() {
		document.cookie = 'gerps_cookie_ok=true; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/';
		showBanner = false;
	}

	onMount(() => {
		try {
			const cookiesAccepted = document.cookie.includes('gerps_cookie_ok=true');

      // only show the banner if it hasnt been accepted before
			showBanner = !cookiesAccepted;
		} catch (error) {
			log('CookieBanner', 'Error getting cookiesAccepted from sessionStorage: ' + error);
		}
	});
</script>

{#if showBanner}
	<div class="cookie-banner">
		<div class="outer-container">
			<div class="d-flex align-items-center">
				Diese Website nutzt nur technisch notwendige Cookies um sicherzustellen, dass die Website
				ordnungsgemäß funktioniert.
			</div>
			<button class="btn btn-primary mx-2" on:click={acceptCookies}>OK</button>
		</div>
	</div>
{/if}

<style>
	.outer-container {
		width: fit-content;
		display: flex;
		z-index: 1000;
	}
	.cookie-banner {
		position: fixed;
		bottom: 30px;
		left: 0;
		width: 100%;
		background-color: #f8f9fa;
		padding: 10px;
		box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.1);
		z-index: 1000;
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>
