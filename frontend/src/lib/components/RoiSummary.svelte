<script>
	import { api } from '$lib/api';

	// Collapsed state - start collapsed
	let isExpanded = $state(false);

	function formatCurrency(value) {
		if (value === null || value === undefined) return '-';
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 2,
		}).format(value);
	}

	function formatPercent(value) {
		if (value === null || value === undefined) return '-';
		const numValue = typeof value === 'string' ? parseFloat(value) : value;
		if (isNaN(numValue)) return '-';
		return `${numValue.toFixed(2)}%`;
	}

	function toggleExpanded() {
		isExpanded = !isExpanded;
	}

	// Date range state
	let startDate = $state('');
	let endDate = $state('');
	let roiData = $state(null);
	let loading = $state(false);
	let error = $state(null);

	// Set default date range to current month
	function setDefaultDates() {
		const today = new Date();
		const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
		const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);

		startDate = firstDay.toISOString().split('T')[0];
		endDate = lastDay.toISOString().split('T')[0];
	}

	// Initialize with default dates
	setDefaultDates();

	// Quick date range presets
	function setThisWeek() {
		const today = new Date();
		const dayOfWeek = today.getDay();
		const monday = new Date(today);
		monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));
		const friday = new Date(monday);
		friday.setDate(monday.getDate() + 4);

		startDate = monday.toISOString().split('T')[0];
		endDate = friday.toISOString().split('T')[0];
		fetchRoiData();
	}

	function setThisMonth() {
		setDefaultDates();
		fetchRoiData();
	}

	function setThisYear() {
		const today = new Date();
		startDate = new Date(today.getFullYear(), 0, 1).toISOString().split('T')[0];
		endDate = new Date(today.getFullYear(), 11, 31).toISOString().split('T')[0];
		fetchRoiData();
	}

	function setLastMonth() {
		const today = new Date();
		const firstDay = new Date(today.getFullYear(), today.getMonth() - 1, 1);
		const lastDay = new Date(today.getFullYear(), today.getMonth(), 0);

		startDate = firstDay.toISOString().split('T')[0];
		endDate = lastDay.toISOString().split('T')[0];
		fetchRoiData();
	}

	function setAllTime() {
		startDate = '';
		endDate = '';
		fetchRoiData();
	}

	// Fetch ROI data for the selected date range
	async function fetchRoiData() {
		loading = true;
		error = null;
		try {
			roiData = await api.getRoiSummary(startDate, endDate);
		} catch (err) {
			error = err.message;
			console.error('Error fetching ROI data:', err);
		} finally {
			loading = false;
		}
	}

	// Fetch data on mount
	$effect(() => {
		fetchRoiData();
	});
</script>

<div class="bg-white rounded-lg shadow-lg mb-6 border border-gray-100">
	<button
		onclick={toggleExpanded}
		class="w-full px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-green-50 to-white hover:from-green-100 hover:to-gray-50 transition-colors cursor-pointer text-left"
	>
		<div class="flex justify-between items-center">
			<div>
				<h2 class="text-xl font-bold text-gray-900">Return on Investment (ROI)</h2>
				<p class="text-sm text-gray-600 mt-1">Closed positions only (realized gains)</p>
			</div>
			<svg
				class="w-6 h-6 text-gray-600 transition-transform duration-200"
				class:rotate-180={isExpanded}
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
			</svg>
		</div>
	</button>

	{#if isExpanded}
	<!-- Date Range Picker -->
	<div class="p-6 border-b border-gray-200 bg-gray-50">
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
			<!-- Date Inputs -->
			<div class="grid grid-cols-2 gap-4">
				<div>
					<label for="start-date" class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
					<input
						id="start-date"
						type="date"
						bind:value={startDate}
						onchange={fetchRoiData}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					/>
				</div>
				<div>
					<label for="end-date" class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
					<input
						id="end-date"
						type="date"
						bind:value={endDate}
						onchange={fetchRoiData}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					/>
				</div>
			</div>

			<!-- Quick Presets -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Quick Select</label>
				<div class="flex flex-wrap gap-2">
					<button
						onclick={setThisWeek}
						class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 cursor-pointer"
					>
						This Week
					</button>
					<button
						onclick={setThisMonth}
						class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 cursor-pointer"
					>
						This Month
					</button>
					<button
						onclick={setLastMonth}
						class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 cursor-pointer"
					>
						Last Month
					</button>
					<button
						onclick={setThisYear}
						class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 cursor-pointer"
					>
						This Year
					</button>
					<button
						onclick={setAllTime}
						class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 cursor-pointer"
					>
						All Time
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- ROI Data -->
	<div class="p-6">
		{#if loading}
			<div class="flex justify-center items-center py-12">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			</div>
		{:else if error}
			<div class="text-center py-8 text-red-600">
				<p>Error loading ROI data: {error}</p>
			</div>
		{:else if !roiData || !roiData.premium}
			<div class="text-center py-8 text-gray-500">
				<p>No closed positions in this date range</p>
			</div>
		{:else}
			<!-- ROI Summary Cards -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-6">
				<div class="bg-purple-50 rounded-lg p-4">
					<div class="text-sm font-medium text-purple-600 mb-1">Closed Positions</div>
					<div class="text-2xl font-bold text-purple-900">{roiData.position_count || 0}</div>
				</div>

				<div class="bg-blue-50 rounded-lg p-4">
					<div class="text-sm font-medium text-blue-600 mb-1">Total P/L</div>
					<div class="text-2xl font-bold text-blue-900">{formatCurrency(roiData.premium)}</div>
				</div>

				<div class="bg-orange-50 rounded-lg p-4">
					<div class="text-sm font-medium text-orange-600 mb-1">Total Collateral</div>
					<div class="text-2xl font-bold text-orange-900">{formatCurrency(roiData.collateral)}</div>
				</div>

				<div class="bg-green-50 rounded-lg p-4">
					<div class="text-sm font-medium text-green-600 mb-1">ROI Percentage</div>
					<div class="text-2xl font-bold text-green-900">{formatPercent(roiData.roi_percentage)}</div>
				</div>
			</div>
		{/if}
	</div>
	{/if}
</div>

<style>
	.rotate-180 {
		transform: rotate(180deg);
	}
</style>
