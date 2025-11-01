<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import PositionForm from '$lib/components/PositionForm.svelte';
	import PositionTable from '$lib/components/PositionTable.svelte';
	import Summary from '$lib/components/Summary.svelte';
	import RoiSummary from '$lib/components/RoiSummary.svelte';
	import Logo from '$lib/components/Logo.svelte';

	let positions = $state([]);
	let summary = $state(null);
	let loading = $state(true);
	let error = $state(null);
	let showForm = $state(false);
	let editingPosition = $state(null);
	let filterStock = $state('');
	let filterType = $state('');
	let filterStatus = $state('all'); // all, open, closed

	onMount(() => {
		loadData();
	});

	async function loadData() {
		if (!browser) return;

		loading = true;
		error = null;
		try {
			const [positionsData, summaryData] = await Promise.all([
				api.getPositions(),
				api.getSummary()
			]);
			positions = positionsData.results || positionsData;
			summary = summaryData;
		} catch (err) {
			error = err.message;
			console.error('Error loading data:', err);
		} finally {
			loading = false;
		}
	}

	async function handleSave(position) {
		try {
			if (position.isRoll) {
				// Handle roll operation: update existing position and create new one
				await api.updatePosition(editingPosition.id, position.closePosition);
				await api.createPosition(position.newPosition);
			} else if (editingPosition) {
				await api.updatePosition(editingPosition.id, position);
			} else {
				await api.createPosition(position);
			}
			showForm = false;
			editingPosition = null;
			await loadData();
		} catch (err) {
			error = err.message;
		}
	}

	async function handleEdit(position) {
		editingPosition = position;
		showForm = true;
	}

	async function handleDelete(id) {
		if (!confirm('Are you sure you want to delete this position?')) return;

		try {
			await api.deletePosition(id);
			await loadData();
		} catch (err) {
			error = err.message;
		}
	}


	function handleCancel() {
		showForm = false;
		editingPosition = null;
	}

	function openNewPositionForm() {
		editingPosition = null;
		showForm = true;
		// Scroll to form after it's rendered
		setTimeout(() => {
			document.getElementById('position-form')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
		}, 100);
	}

	function handleLogout() {
		if (browser) {
			localStorage.removeItem('access_token');
			localStorage.removeItem('refresh_token');
			goto('/login');
		}
	}

	$effect(() => {
		// Filter positions based on current filters
		filteredPositions;
	});

	let filteredPositions = $derived(() => {
		let filtered = positions;

		if (filterStock) {
			filtered = filtered.filter(p =>
				p.stock.toLowerCase().includes(filterStock.toLowerCase())
			);
		}

		if (filterType) {
			filtered = filtered.filter(p => p.type === filterType);
		}

		if (filterStatus === 'open') {
			filtered = filtered.filter(p => p.is_open);
		} else if (filterStatus === 'closed') {
			filtered = filtered.filter(p => !p.is_open);
		}

		return filtered;
	});
</script>

<svelte:head>
	<title>WheelTracker - Options Wheel Strategy Platform</title>
	<meta name="description" content="Professional options trading tracker for the wheel strategy. Track positions, calculate ROI, and manage your covered calls and cash-secured puts." />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
	<!-- Clean and Simple Header -->
	<header class="bg-white border-b border-gray-200 shadow-sm">
		<div class="mx-auto px-4 py-3 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center">
				<!-- Logo and Brand -->
				<div class="flex items-center gap-2">
					<Logo size={32} />
					<h1 class="text-xl font-bold text-gray-900">WheelTracker</h1>
				</div>

				<!-- Navigation Actions -->
				<div class="flex items-center gap-2">
					<button
						onclick={openNewPositionForm}
						class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 cursor-pointer"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
						</svg>
						New Position
					</button>
					<button
						onclick={handleLogout}
						class="text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer"
						title="Logout"
					>
						Logout
					</button>
				</div>
			</div>
		</div>
	</header>

	<main class="mx-auto px-4 py-8 sm:px-6 lg:px-8">
		{#if error}
			<div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
				<p class="font-bold">Error loading data:</p>
				<p>{error}</p>
				<p class="text-sm mt-2">Make sure Django server is running: <code class="bg-red-100 px-1 py-0.5 rounded">python manage.py runserver</code></p>
				<p class="text-sm mt-1">Then refresh this page.</p>
			</div>
		{/if}

		{#if loading && !positions.length}
			<div class="flex justify-center items-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			</div>
		{:else}
			{#if summary}
				<Summary {summary} />
			{/if}

			<RoiSummary />

			<div class="bg-white rounded-lg shadow p-6 mb-6">
				<h2 class="text-xl font-bold text-gray-900 mb-4">Filters</h2>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div>
						<label for="filter-stock" class="block text-sm font-medium text-gray-700 mb-1">Stock Symbol</label>
						<input
							id="filter-stock"
							type="text"
							bind:value={filterStock}
							placeholder="Filter by stock..."
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div>
						<label for="filter-type" class="block text-sm font-medium text-gray-700 mb-1">Type</label>
						<select
							id="filter-type"
							bind:value={filterType}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
						>
							<option value="">All</option>
							<option value="P">Put</option>
							<option value="C">Call</option>
						</select>
					</div>
					<div>
						<label for="filter-status" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
						<select
							id="filter-status"
							bind:value={filterStatus}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
						>
							<option value="all">All</option>
							<option value="open">Open</option>
							<option value="closed">Closed</option>
						</select>
					</div>
				</div>
			</div>

			{#if showForm}
				<div id="position-form" class="bg-white rounded-lg shadow p-6 mb-6">
					<h2 class="text-xl font-bold text-gray-900 mb-4">
						{editingPosition ? 'Edit Position' : 'New Position'}
					</h2>
					<PositionForm
						position={editingPosition}
						availablePositions={positions}
						onSave={handleSave}
						onCancel={handleCancel}
					/>
				</div>
			{/if}

			<PositionTable
				positions={filteredPositions()}
				onEdit={handleEdit}
				onDelete={handleDelete}
			/>
		{/if}
	</main>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
	}
</style>
