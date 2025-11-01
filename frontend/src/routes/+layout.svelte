<script>
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let { children } = $props();

	onMount(() => {
		// Check if user is authenticated (except on login and register pages)
		const publicPages = ['/login', '/register'];
		if (browser && !publicPages.includes($page.url.pathname)) {
			const token = localStorage.getItem('access_token');
			if (!token) {
				goto('/login');
			}
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children?.()}
