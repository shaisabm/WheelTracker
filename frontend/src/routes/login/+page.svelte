<script>
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import Logo from '$lib/components/Logo.svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';

	console.log('PUBLIC_API_BASE_URL:', PUBLIC_API_BASE_URL);

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleLogin(e) {
		e.preventDefault();
		error = '';
		loading = true;

		try {
			const response = await fetch(`${PUBLIC_API_BASE_URL}/auth/login/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					username,
					password,
				}),
			});

			if (!response.ok) {
				const data = await response.json();
				throw new Error(data.detail || 'Invalid credentials');
			}

			const data = await response.json();

			// Store tokens in localStorage
			if (browser) {
				localStorage.setItem('access_token', data.access);
				localStorage.setItem('refresh_token', data.refresh);
			}

			// Redirect to dashboard
			goto('/');
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Login - WheelTracker</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center px-4">
	<div class="max-w-md w-full">
		<!-- Logo and Brand -->
		<div class="text-center mb-8">
			<div class="flex justify-center mb-4">
				<div class="bg-white rounded-lg p-3 shadow-lg">
					<Logo size={60} />
				</div>
			</div>
			<h1 class="text-3xl font-bold text-gray-900">WheelTracker</h1>
			<p class="text-gray-600 mt-2">Options Wheel Strategy Platform</p>
		</div>


		<!-- Login Card -->
		<div class="bg-white rounded-lg shadow-xl p-8">
			<h2 class="text-2xl font-bold text-gray-900 mb-6">Sign In</h2>

			{#if error}
				<div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
					{error}
				</div>
			{/if}

			<form onsubmit={handleLogin}>
				<div class="space-y-4">
					<!-- Username -->
					<div>
						<label for="username" class="block text-sm font-medium text-gray-700 mb-1">
							Username
						</label>
						<input
							id="username"
							type="text"
							bind:value={username}
							required
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							placeholder="Enter your username"
						/>
					</div>

					<!-- Password -->
					<div>
						<label for="password" class="block text-sm font-medium text-gray-700 mb-1">
							Password
						</label>
						<input
							id="password"
							type="password"
							bind:value={password}
							required
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							placeholder="Enter your password"
						/>
					</div>

					<!-- Submit Button -->
					<button
						type="submit"
						disabled={loading}
						class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
					>
						{#if loading}
							<span class="flex items-center justify-center gap-2">
								<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
								Signing in...
							</span>
						{:else}
							Sign In
						{/if}
					</button>
				</div>
			</form>

			<!-- Demo Credentials -->
			<div class="mt-6 pt-6 border-t border-gray-200">
				<p class="text-sm text-gray-600 text-center">
					Demo: <span class="font-medium">admin</span> / <span class="font-medium">admin123</span>
				</p>
			</div>

			<!-- Registration Link -->
			<div class="mt-4 text-center">
				<p class="text-sm text-gray-600">
					Don't have an account?
					<a href="/register" class="text-blue-600 hover:text-blue-700 font-semibold">
						Create one
					</a>
				</p>
			</div>
		</div>

		<!-- Footer -->
		<p class="text-center text-gray-600 text-sm mt-6">
			Track your wheel strategy trades with confidence
		</p>
	</div>
</div>
