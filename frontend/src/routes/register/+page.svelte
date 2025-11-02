<script>
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import Logo from '$lib/components/Logo.svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';

	let username = $state('');
	let email = $state('');
	let password = $state('');
	let passwordConfirm = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleRegister(e) {
		e.preventDefault();
		error = '';
		loading = true;

		// Client-side validation
		if (password !== passwordConfirm) {
			error = 'Passwords do not match';
			loading = false;
			return;
		}

		if (password.length < 6) {
			error = 'Password must be at least 6 characters long';
			loading = false;
			return;
		}

		try {
			const response = await fetch(`${PUBLIC_API_BASE_URL}/auth/register/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					username,
					email,
					password,
					password_confirm: passwordConfirm,
				}),
			});

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.error || 'Registration failed');
			}

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
	<title>Register - WheelTracker</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center px-4 py-8">
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

		<!-- Maintenance Notice -->
		<div class="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-6 mb-6 shadow-lg">
			<div class="flex items-start gap-3">
				<svg class="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
				</svg>
				<div>
					<h3 class="text-lg font-bold text-yellow-900 mb-2">Maintenance Notice</h3>
					<p class="text-yellow-800 mb-2">
						Our free trial database limit has been exceeded. We're working to restore service.
					</p>
					<p class="text-yellow-800 font-semibold">
						✓ Your data is safe<br>
						✓ Expected back online: Monday, November 3rd
					</p>
				</div>
			</div>
		</div>

		<!-- Registration Card -->
		<div class="bg-white rounded-lg shadow-xl p-8">
			<h2 class="text-2xl font-bold text-gray-900 mb-6">Create Account</h2>

			{#if error}
				<div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
					{error}
				</div>
			{/if}

			<form onsubmit={handleRegister}>
				<div class="space-y-4">
					<!-- Username -->
					<div>
						<label for="username" class="block text-sm font-medium text-gray-700 mb-1">
							Username <span class="text-red-500">*</span>
						</label>
						<input
							id="username"
							type="text"
							bind:value={username}
							required
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							placeholder="Choose a username"
						/>
					</div>

					<!-- Email -->
					<div>
						<label for="email" class="block text-sm font-medium text-gray-700 mb-1">
							Email (Optional)
						</label>
						<input
							id="email"
							type="email"
							bind:value={email}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							placeholder="your@email.com"
						/>
					</div>

					<!-- Password -->
					<div>
						<label for="password" class="block text-sm font-medium text-gray-700 mb-1">
							Password <span class="text-red-500">*</span>
						</label>
						<input
							id="password"
							type="password"
							bind:value={password}
							required
							minlength="6"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							placeholder="At least 6 characters"
						/>
						<p class="text-xs text-gray-500 mt-1">Minimum 6 characters</p>
					</div>

					<!-- Confirm Password -->
					<div>
						<label for="password-confirm" class="block text-sm font-medium text-gray-700 mb-1">
							Confirm Password <span class="text-red-500">*</span>
						</label>
						<input
							id="password-confirm"
							type="password"
							bind:value={passwordConfirm}
							required
							minlength="6"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							placeholder="Re-enter your password"
						/>
					</div>

					<!-- Submit Button -->
					<button
						type="submit"
						disabled={loading}
						class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer mt-6"
					>
						{#if loading}
							<span class="flex items-center justify-center gap-2">
								<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
								Creating account...
							</span>
						{:else}
							Create Account
						{/if}
					</button>
				</div>
			</form>

			<!-- Login Link -->
			<div class="mt-6 pt-6 border-t border-gray-200 text-center">
				<p class="text-sm text-gray-600">
					Already have an account?
					<a href="/login" class="text-blue-600 hover:text-blue-700 font-semibold">
						Sign in
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
