<script>
	// @ts-nocheck

	import { jwt } from './../stores/store.js';
	import { onMount, setContext, onDestroy, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import { page } from '$app/stores';
	import { getRole, logout } from './login/+page.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import Banner from '$lib/components/Banner.svelte';
	import CookieBanner from '$lib/components/CookieBanner.svelte';
	import logoImg from '$lib/assets/logo.png';
	import { Tooltip } from '@svelte-plugins/tooltips';
	import { log } from '../lib/CustomLogger.js';

	export const prerender = true;

	let token;
	let role = 'user';
	let windowTooSmall = false;
	let isAuthenticated = false;

	jwt.subscribe((value) => {
		token = value;
	});

	// reactive variables useful for conditional rendering
	$: isAuthenticated = token !== undefined && token !== null;

	// check windows size on load
	checkWindowSize();

	onMount(() => {
		token = localStorage.getItem('jwt');

		if (token !== undefined && token !== null) {
			isAuthenticated = true;

			// check if role is jwt additional claim role = admin
			role = getRole(token);
		}

		// check the window size whenever it's resized
		window.addEventListener('resize', checkWindowSize);
		// adjust navbar on window resize
		window.addEventListener('resize', () => setTimeout(updateHoriSelector, 500));

		const tabsNewAnim = document.querySelector('#navbarSupportedContent');

		// Call once to set initial position
		updateHoriSelector();

		// Setup listeners once
		tabsNewAnim.addEventListener('click', (e) => {
			let target = e.target;
			// Ensure we're clicking on an LI element or a child of it
			while (target && target.tagName !== 'LI' && target !== tabsNewAnim) {
				target = target.parentNode;
			}
			if (target && target.tagName === 'LI') {
				tabsNewAnim.querySelectorAll('ul li').forEach((li) => li.classList.remove('active'));
				target.classList.add('active');
				updateHoriSelector(); // Update .hori-selector position
			}
		});

		// Navbar toggler
		const navbarToggler = document.querySelector('.navbar-toggler');
		navbarToggler?.addEventListener('click', () => {
			const collapse = document.querySelector('.navbar-collapse');
			const isCollapsed = collapse.style.display === 'block';
			collapse.style.display = isCollapsed ? 'none' : 'block';
			setTimeout(updateHoriSelector, 300);
		});

		// Active class on page move
		const path = window.location.pathname.split('/').pop();
		const targetPath = path === '' ? 'index.html' : path;
		const target = document.querySelector(`#navbarSupportedContent ul li a[href="${targetPath}"]`);
		if (target) {
			target.parentElement.classList.add('active');
		}
	});

	onDestroy(() => {});

	// Reactive statement for updating navigation state, adjusted for SSR compatibility
	$: if (browser) {
		const pathname = $page.url.pathname;

		// Because this runs reactively, you need to ensure it's deferred until after the DOM updates
		// which is why we use `setTimeout` here.
		setTimeout(() => {
			const navItems = document.querySelectorAll('#navbarSupportedContent ul li a');
			navItems.forEach((item) => {
				item.parentElement.classList.remove('active');
			});
			const activeItem = document.querySelector(
				`#navbarSupportedContent ul li a[href="${pathname}"]`
			);
			if (activeItem) {
				activeItem.parentElement.classList.add('active');
			}
			// Assuming updateHoriSelector is your function to adjust the UI, call it here
			updateHoriSelector();
		}, 0); // `0` delay ensures this runs after Svelte has updated the DOM
	}

	// Function definitions below

	/*
	 * Function to navigate to the admin dashboard, used by the Settings-button
	 */
	function navigateToAdminDashboard() {
		goto('/settings');
		clearActiveStates(); // clears states of navbar
	}

	/*
	 * Navbar helper function to clear active states
	 */
	function clearActiveStates() {
		// Query all nav items and remove 'active' class
		const navItems = document.querySelectorAll('#navbarSupportedContent ul li');
		navItems.forEach((item) => {
			item.classList.remove('active');
		});

		updateHoriSelector(); // Update the horizontal selector if necessary
	}

	/*
	 * used by the Logout-button, invalidates the token and redirects to the login page
	 */
	function logoutButton() {

		// show alert that warns of data loss

		if (!confirm('Achtung: Der Inhalt des Annotationseditors und Prozessmodellierers wird gelöscht! Trotzdem fortfahren?')) {
			return;
		}

		logout(token);
		isAuthenticated = false;
		deleteAnnotatedDataLocalStorage();
	}

	/*
	 * Function to remove the annotated data from the local storage after LOG OUT
	 */
	function deleteAnnotatedDataLocalStorage() {
		const keys = [
			'annotatedData',
			'annotation_view_meta',
			'resultData',
			'process_view_text_checkpoint',
			'jwt',
			'checkpoint'
		];
		keys.forEach((key) => localStorage.removeItem(key));
	}

	/*
	 * Function to check the window size and set the windowTooSmall variable accordingly
	 * For small windows, a warning is displayed (instead of the content)
	 */
	function checkWindowSize() {
		try {
			if (typeof window !== 'undefined') {
				windowTooSmall = window.innerWidth < 1000 || window.innerHeight < 400;
			}
		} catch (error) {
			console.debug('Error checking window size:', error);
		}
	}

	/*
	 * Function to update the navbar (.hori-selector) position and size
	 */
	function updateHoriSelector() {
		const selector = document.querySelector('.hori-selector');
		const tabsNewAnim = document.querySelector('#navbarSupportedContent');
		const activeItemNewAnim = tabsNewAnim.querySelector('.active');

		// If there's no active item, hide the selector
		if (!activeItemNewAnim) {
			if (selector) {
				selector.style.cssText = 'display: none;';
			}
			return;
		}

		// If there is an active item, update the selector's position and size
		const { offsetHeight, offsetWidth, offsetTop, offsetLeft } = activeItemNewAnim;

		if (selector) {
			selector.style.cssText = `
            display: block;
            top: ${offsetTop}px;
            left: ${offsetLeft}px;
            height: ${offsetHeight}px;
            width: ${offsetWidth}px;
        `;
		}
	}
</script>

<svelte:window on:resize={checkWindowSize} />
<CookieBanner />

<div style="min-height: 100vh; ">
	<Banner />

	<!-- navigation bar -->
	<nav class="navbar navbar-expand-custom navbar-mainbg">
		<div class="container-fluid">
			<a class="navbar-brand navbar-logo" href="/">
				<img class="logo-img" src={logoImg} alt="" width="fit-content" />
			</a>

			<button
				class="navbar-toggler"
				type="button"
				aria-controls="navbarSupportedContent"
				aria-expanded="false"
				aria-label="Toggle navigation"
			/>

			<div class="collapse navbar-collapse" id="navbarSupportedContent">
				<ul class="navbar-nav ml-auto">
					<div class="hori-selector">
						<div class="left" />
						<div class="right" />
					</div>

					{#if isAuthenticated}
						<li class="nav-item active">
							<a class="nav-link" href="/">Start</a>
						</li>
						<li class="nav-item">
							<a class="nav-link" href="/search">Normensuche</a>
						</li>

						<li class="nav-item">
							<a class="nav-link" href="/annotation-editor">Annotationen</a>
						</li>
						<li class="nav-item">
							<a class="nav-link" href="/process">Prozessmodellierung</a>
						</li>
						<li class="nav-item">
							<a class="nav-link" href="/help">Hilfe</a>
						</li>
					{/if}
				</ul>
			</div>

			{#if isAuthenticated}
				<!-- only show these buttons when logged in -->
				<button class="settings-button" on:click={navigateToAdminDashboard}>
					<Tooltip content="Einstellungen" position="left">
						<span class="gear-icon"> ⚙️ </span>
					</Tooltip>
				</button>

				<button id="logout" class="logout-button" on:click={logoutButton}>Log out</button>
			{/if}
		</div>
	</nav>

	<!-- main content via slot, or a warning if the window is too small -->
	<main>
		{#if windowTooSmall}
			<div class="alert alert-warning m-3 p-3">
				⚠️ Das Browser-Fenster ist aktuell zu klein um die Anwendung darzustellen.
			</div>
		{:else}
			<slot />
		{/if}
	</main>

	<Footer />
</div>

<!-- include bootstrap globally -->
<link
	href="/bootstrap.min.css"
	rel="stylesheet"
	integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN"
	crossorigin="anonymous"
/>

<style>
	@import '../global.css';

	* {
		margin: 0;
		padding: 0;
	}

	.logout-button {
		padding: 6px 13px;
		background-color: white;
		color: rgb(255, 0, 0);
		border-radius: 2mm;
		border: none;
		height: 40px;
		cursor: pointer;
		position: relative;
		right: 50px;
	}

	.logout-button:hover {
		background-color: whitesmoke; /* Darker shade on hover */
	}

	.settings-button {
		padding: 6px 13px;
		background-color: white;
		color: grey;
		border-radius: 2mm;
		border: none;
		height: 40px;
		cursor: pointer;
		position: relative;
		right: 70px;
	}

	.settings-button:hover {
		background-color: whitesmoke; /* Darker shade on hover */
	}

	.settings-button:hover .gear-icon {
		transform: rotate(360deg);
		transition: transform 0.5s ease-in-out;
	}

	.gear-icon {
		display: inline-block;
	}

	.navbar-logo {
		margin-left: 400px;
		margin-bottom: auto;
		margin-top: auto;
	}

	.logo-img {
		margin: 0;
		padding: 0;
		height: 50px;
	}

	/*----------bootstrap-navbar-css------------*/

	.navbar-mainbg {
		background-color: #9999ff;
		padding: 0px;
	}
	#navbarSupportedContent {
		overflow: hidden;
		position: relative;
	}
	#navbarSupportedContent ul {
		padding: 0px;
		margin: 0px;
	}
	/* 	#navbarSupportedContent ul li a i {
		margin-right: 10px;
	} */
	#navbarSupportedContent li {
		list-style-type: none;
		float: left;
	}
	#navbarSupportedContent ul li a {
		color: white;
		text-decoration: none;
		font-weight: 600;
		font-size: 15px;
		display: block;
		padding: 20px;
		transition-duration: 0.6s;
		transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55);
		position: relative;
	}
	#navbarSupportedContent > ul > li.active > a {
		color: #9999ff;
		background-color: transparent;
		transition: all 0.7s;
	}
	#navbarSupportedContent a:not(:only-child):after {
		content: '\f105';
		position: absolute;
		right: 20px;
		top: 10px;
		font-size: 14px;
		font-family: 'Font Awesome 5 Free';
		display: inline-block;
		padding-right: 3px;
		vertical-align: middle;
		font-weight: 900;
		transition: 0.5s;
	}
	#navbarSupportedContent .active > a:not(:only-child):after {
		transform: rotate(90deg);
	}
	.hori-selector {
		display: inline-block;
		position: absolute;
		height: 100%;
		top: 0px;
		left: 0px;
		transition-duration: 0.6s;
		transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55);
		background-color: #fff;
		border-top-left-radius: 15px;
		border-top-right-radius: 15px;
		margin-top: 10px;
	}
	.hori-selector .right,
	.hori-selector .left {
		position: absolute;
		width: 25px;
		height: 25px;
		background-color: #fff;
		bottom: 10px;
	}
	.hori-selector .right {
		right: -25px;
	}
	.hori-selector .left {
		left: -25px;
	}
	.hori-selector .right:before,
	.hori-selector .left:before {
		content: '';
		position: absolute;
		width: 50px;
		height: 50px;
		border-radius: 50%;
		background-color: #9999ff;
	}
	.hori-selector .right:before {
		bottom: 0;
		right: -25px;
	}
	.hori-selector .left:before {
		bottom: 0;
		left: -25px;
	}

	@media (min-width: 992px) {
		.navbar-expand-custom {
			-ms-flex-flow: row nowrap;
			flex-flow: row nowrap;
			-ms-flex-pack: start;
			justify-content: flex-start;
		}
		.navbar-expand-custom .navbar-nav {
			-ms-flex-direction: row;
			flex-direction: row;
			justify-content: center;
			flex-grow: 1;
		}
		.navbar-expand-custom .navbar-toggler {
			display: none;
		}
		.navbar-expand-custom .navbar-collapse {
			display: -ms-flexbox !important;
			display: flex !important;
			-ms-flex-preferred-size: auto;
			flex-basis: auto;
			justify-content: flex-end;
		}
	}

	@media (max-width: 991px) {
		#navbarSupportedContent ul li a {
			padding: 12px 30px;
		}
		.hori-selector {
			margin-top: 0px;
			margin-left: 10px;
			border-radius: 0;
			border-top-left-radius: 25px;
			border-bottom-left-radius: 25px;
		}
		.hori-selector .left,
		.hori-selector .right {
			right: 10px;
		}
		.hori-selector .left {
			top: -25px;
			left: auto;
		}
		.hori-selector .right {
			bottom: -25px;
		}
		.hori-selector .left:before {
			left: -25px;
			top: -25px;
		}
		.hori-selector .right:before {
			bottom: -25px;
			left: -25px;
		}
	}

	@media (max-width: 2000px) {
		.navbar-brand {
			margin-left: 10px; /* Reduce the left margin */
			flex-grow: 1; /* Ensure the logo takes up more space if needed */
		}

		.navbar-collapse {
			flex-basis: 100%; /* Ensure the navbar items move to the next line */
		}

		.navbar-nav {
			justify-content: flex-end; /* Push nav items to the right */
			flex-wrap: wrap; /* Allow wrapping of items */
		}

		.navbar-nav .nav-item {
			margin: 0 5px; /* Reduce space between items */
		}

		.logo-img {
			max-width: 150px; /* Reduce the logo size */
			height: auto; /* Maintain aspect ratio */
		}
	}
</style>
