<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import Logo from '$lib/components/Logo.svelte';
	import SendNotificationModal from '$lib/components/SendNotificationModal.svelte';

	let feedbackList = $state([]);
	let loading = $state(true);
	let error = $state(null);
	let currentUser = $state(null);
	let filterType = $state('');
	let filterStatus = $state('');
	let showSendNotificationModal = $state(false);

	onMount(async () => {
		await checkAuth();
		await loadFeedback();
	});

	async function checkAuth() {
		try {
			currentUser = await api.getCurrentUser();
			// Redirect if not superuser
			if (!currentUser.is_superuser && !currentUser.is_staff) {
				goto('/');
			}
		} catch (err) {
			console.error('Auth check failed:', err);
			goto('/login');
		}
	}

	async function loadFeedback() {
		loading = true;
		error = null;
		try {
			const data = await api.getAllFeedback();
			feedbackList = data.results || data;
		} catch (err) {
			error = err.message;
			console.error('Error loading feedback:', err);
		} finally {
			loading = false;
		}
	}

	async function updateStatus(id, newStatus) {
		try {
			await api.updateFeedbackStatus(id, newStatus);
			// Update local state
			feedbackList = feedbackList.map(item =>
				item.id === id ? { ...item, status: newStatus } : item
			);
		} catch (err) {
			alert(`Failed to update status: ${err.message}`);
		}
	}

	function handleLogout() {
		if (browser) {
			localStorage.removeItem('access_token');
			localStorage.removeItem('refresh_token');
			goto('/login');
		}
	}

	function getTypeLabel(type) {
		const types = {
			bug: 'Bug Report',
			feature: 'Feature Request',
			other: 'Other'
		};
		return types[type] || type;
	}

	function getTypeBadgeClass(type) {
		const classes = {
			bug: 'bg-red-100 text-red-800',
			feature: 'bg-blue-100 text-blue-800',
			other: 'bg-gray-100 text-gray-800'
		};
		return classes[type] || 'bg-gray-100 text-gray-800';
	}

	function getStatusBadgeClass(status) {
		const classes = {
			new: 'bg-yellow-100 text-yellow-800',
			in_progress: 'bg-blue-100 text-blue-800',
			completed: 'bg-green-100 text-green-800',
			closed: 'bg-gray-100 text-gray-800'
		};
		return classes[status] || 'bg-gray-100 text-gray-800';
	}

	function getStatusLabel(status) {
		const labels = {
			new: 'New',
			in_progress: 'In Progress',
			completed: 'Completed',
			closed: 'Closed'
		};
		return labels[status] || status;
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	let filteredFeedback = $derived(() => {
		let filtered = feedbackList;

		if (filterType) {
			filtered = filtered.filter(f => f.type === filterType);
		}

		if (filterStatus) {
			filtered = filtered.filter(f => f.status === filterStatus);
		}

		return filtered;
	});

	// Group by status
	let groupedByStatus = $derived(() => {
		const filtered = filteredFeedback();
		return {
			new: filtered.filter(f => f.status === 'new'),
			in_progress: filtered.filter(f => f.status === 'in_progress'),
			completed: filtered.filter(f => f.status === 'completed'),
			closed: filtered.filter(f => f.status === 'closed')
		};
	});
</script>

<svelte:head>
	<title>Feedback Management - WheelTracker Admin</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
	<!-- Header -->
	<header class="bg-white border-b border-gray-200 shadow-sm">
		<div class="mx-auto px-4 py-3 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center">
				<div class="flex items-center gap-2">
					<Logo size={32} />
					<div>
						<h1 class="text-lg sm:text-xl font-bold text-gray-900">WheelTracker Admin</h1>
						<p class="text-xs sm:text-sm text-gray-600 hidden sm:block">Feedback Management</p>
					</div>
				</div>

				<div class="flex items-center gap-1 sm:gap-2">
					<button
						onclick={() => showSendNotificationModal = true}
						class="text-purple-600 hover:text-purple-700 hover:bg-purple-50 px-2 sm:px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors cursor-pointer flex items-center gap-1.5"
						title="Send Notification to Users"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
							      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
						</svg>
						<span class="hidden sm:inline">Send Notification</span>
						<span class="sm:hidden">Notify</span>
					</button>
					<a
						href="/"
						class="text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-2 sm:px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors cursor-pointer"
					>
						<span class="hidden sm:inline">Dashboard</span>
						<span class="sm:hidden">Home</span>
					</a>
					<button
						onclick={handleLogout}
						class="text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-2 sm:px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors cursor-pointer"
						title="Logout"
					>
						Logout
					</button>
				</div>
			</div>
		</div>
	</header>

	<main class="mx-auto px-4 py-8 sm:px-6 lg:px-8 max-w-7xl">
		{#if error}
			<div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
				<p class="font-bold">Error loading feedback:</p>
				<p>{error}</p>
			</div>
		{/if}

		{#if loading}
			<div class="flex justify-center items-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			</div>
		{:else}
			<!-- Summary Stats -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
				<div class="bg-white rounded-lg shadow p-6">
					<div class="text-sm text-gray-600 mb-1">Total Feedback</div>
					<div class="text-3xl font-bold text-gray-900">{feedbackList.length}</div>
				</div>
				<div class="bg-yellow-50 rounded-lg shadow p-6">
					<div class="text-sm text-yellow-800 mb-1">New</div>
					<div class="text-3xl font-bold text-yellow-900">{groupedByStatus().new.length}</div>
				</div>
				<div class="bg-blue-50 rounded-lg shadow p-6">
					<div class="text-sm text-blue-800 mb-1">In Progress</div>
					<div class="text-3xl font-bold text-blue-900">{groupedByStatus().in_progress.length}</div>
				</div>
				<div class="bg-green-50 rounded-lg shadow p-6">
					<div class="text-sm text-green-800 mb-1">Completed</div>
					<div class="text-3xl font-bold text-green-900">{groupedByStatus().completed.length}</div>
				</div>
			</div>

			<!-- Filters -->
			<div class="bg-white rounded-lg shadow p-6 mb-6">
				<h2 class="text-xl font-bold text-gray-900 mb-4">Filters</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label for="filter-type" class="block text-sm font-medium text-gray-700 mb-1">Type</label>
						<select
							id="filter-type"
							bind:value={filterType}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
						>
							<option value="">All Types</option>
							<option value="bug">Bug Report</option>
							<option value="feature">Feature Request</option>
							<option value="other">Other</option>
						</select>
					</div>
					<div>
						<label for="filter-status" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
						<select
							id="filter-status"
							bind:value={filterStatus}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
						>
							<option value="">All Statuses</option>
							<option value="new">New</option>
							<option value="in_progress">In Progress</option>
							<option value="completed">Completed</option>
							<option value="closed">Closed</option>
						</select>
					</div>
				</div>
			</div>

			<!-- Feedback List -->
			<div class="bg-white rounded-lg shadow overflow-hidden">
				<div class="px-6 py-4 border-b border-gray-200">
					<h2 class="text-xl font-bold text-gray-900">
						Feedback Items ({filteredFeedback().length})
					</h2>
				</div>

				{#if filteredFeedback().length === 0}
					<div class="px-6 py-12 text-center text-gray-500">
						No feedback items found.
					</div>
				{:else}
					<div class="divide-y divide-gray-200">
						{#each filteredFeedback() as feedback (feedback.id)}
							<div class="px-4 sm:px-6 py-4 hover:bg-gray-50 transition-colors">
								<div class="flex items-start justify-between gap-4">
									<div class="flex-1 min-w-0">
										<!-- Header -->
										<div class="flex flex-wrap items-center gap-2 mb-2">
											<span class="px-2 py-1 text-xs font-semibold rounded {getTypeBadgeClass(feedback.type)}">
												{getTypeLabel(feedback.type)}
											</span>
											<span class="px-2 py-1 text-xs font-semibold rounded {getStatusBadgeClass(feedback.status)}">
												{getStatusLabel(feedback.status)}
											</span>
											<span class="text-xs sm:text-sm text-gray-500">
												by {feedback.username}
											</span>
											<span class="text-xs sm:text-sm text-gray-400 hidden sm:inline">
												• {formatDate(feedback.created_at)}
											</span>
										</div>

										<!-- Date on mobile -->
										<div class="text-xs text-gray-400 mb-2 sm:hidden">
											{formatDate(feedback.created_at)}
										</div>

										<!-- Subject -->
										<h3 class="text-base sm:text-lg font-semibold text-gray-900 mb-2">
											{feedback.subject}
										</h3>

										<!-- Description -->
										<p class="text-sm sm:text-base text-gray-700 whitespace-pre-wrap mb-3">
											{feedback.description}
										</p>

										<!-- Actions -->
										<div class="space-y-2">
											<span class="block text-xs sm:text-sm text-gray-600">Change status:</span>
											<div class="flex flex-wrap gap-2">
												<button
													onclick={() => updateStatus(feedback.id, 'new')}
													class="px-2 sm:px-3 py-1 text-xs font-medium rounded transition-colors {feedback.status === 'new' ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'}"
													disabled={feedback.status === 'new'}
												>
													New
												</button>
												<button
													onclick={() => updateStatus(feedback.id, 'in_progress')}
													class="px-2 sm:px-3 py-1 text-xs font-medium rounded transition-colors {feedback.status === 'in_progress' ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-800 hover:bg-blue-200'}"
													disabled={feedback.status === 'in_progress'}
												>
													In Progress
												</button>
												<button
													onclick={() => updateStatus(feedback.id, 'completed')}
													class="px-2 sm:px-3 py-1 text-xs font-medium rounded transition-colors {feedback.status === 'completed' ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800 hover:bg-green-200'}"
													disabled={feedback.status === 'completed'}
												>
													Completed
												</button>
												<button
													onclick={() => updateStatus(feedback.id, 'closed')}
													class="px-2 sm:px-3 py-1 text-xs font-medium rounded transition-colors {feedback.status === 'closed' ? 'bg-gray-600 text-white' : 'bg-gray-100 text-gray-800 hover:bg-gray-200'}"
													disabled={feedback.status === 'closed'}
												>
													Closed
												</button>
											</div>
										</div>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	</main>

	<!-- Send Notification Modal -->
	<SendNotificationModal bind:show={showSendNotificationModal} />
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
	}
</style>
