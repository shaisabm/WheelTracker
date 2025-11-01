<script>
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let { children } = $props();

	onMount(() => {
		const publicPages = ['/login', '/register'];
		const token = localStorage.getItem('access_token');

		if (browser) {
			// If user is logged in and trying to access login/register, redirect to dashboard
			if (token && publicPages.includes($page.url.pathname)) {
				goto('/');
			}
			// If user is not logged in and trying to access protected pages, redirect to login
			else if (!token && !publicPages.includes($page.url.pathname)) {
				goto('/login');
			}
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children?.()}
