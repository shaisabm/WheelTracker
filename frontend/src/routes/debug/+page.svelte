<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	let status = $state('Initializing...');
	let apiUrl = 'http://localhost:8000/api/positions/';
	let response = $state(null);
	let error = $state(null);

	async function testAPI() {
		status = 'Testing API connection...';
		error = null;
		response = null;

		try {
			const res = await fetch(apiUrl);
			const data = await res.json();
			status = `Success! Found ${data.count || data.length || 0} positions`;
			response = JSON.stringify(data, null, 2).substring(0, 1000) + '...';
		} catch (err) {
			status = 'Failed!';
			error = err.message;
		}
	}

	onMount(() => {
		if (browser) {
			testAPI();
		}
	});
</script>

<div class="p-8">
	<h1 class="text-3xl font-bold mb-4">Debug Page</h1>

	<div class="mb-4">
		<p><strong>Environment:</strong> {browser ? 'Browser' : 'Server'}</p>
		<p><strong>API URL:</strong> {apiUrl}</p>
		<p><strong>Status:</strong> {status}</p>
	</div>

	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			<p class="font-bold">Error:</p>
			<p>{error}</p>
		</div>
	{/if}

	{#if response}
		<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
			<p class="font-bold">Response:</p>
			<pre class="text-xs overflow-auto">{response}</pre>
		</div>
	{/if}

	<button
		onclick={testAPI}
		class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
	>
		Test API Again
	</button>

	<div class="mt-4">
		<a href="/" class="text-blue-600 hover:underline">← Back to Dashboard</a>
	</div>
</div>
