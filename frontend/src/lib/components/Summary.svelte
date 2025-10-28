<script>
	let { summary, onFetchAllPrices } = $props();

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
</script>

<div class="bg-white rounded-lg shadow mb-6">
	<div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
		<h2 class="text-xl font-bold text-gray-900">Portfolio Summary</h2>
		<button
			onclick={onFetchAllPrices}
			class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
		>
			Refresh All Prices
		</button>
	</div>
	<div class="p-6">
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<div class="bg-blue-50 rounded-lg p-4">
				<div class="text-sm font-medium text-blue-600 mb-1">Total Positions</div>
				<div class="text-2xl font-bold text-blue-900">{summary.total_positions}</div>
				<div class="text-xs text-blue-600 mt-1">
					{summary.open_positions} open / {summary.closed_positions} closed
				</div>
			</div>

			<div class="bg-green-50 rounded-lg p-4">
				<div class="text-sm font-medium text-green-600 mb-1">Total P/L</div>
				<div class="text-2xl font-bold" class:text-green-900={summary.total_profit_loss >= 0} class:text-red-900={summary.total_profit_loss < 0}>
					{formatCurrency(summary.total_profit_loss)}
				</div>
				<div class="text-xs text-green-600 mt-1">Closed positions</div>
			</div>

			<div class="bg-purple-50 rounded-lg p-4">
				<div class="text-sm font-medium text-purple-600 mb-1">Premium Collected</div>
				<div class="text-2xl font-bold text-purple-900">{formatCurrency(summary.total_premium_collected)}</div>
				<div class="text-xs text-purple-600 mt-1">All positions</div>
			</div>

			<div class="bg-orange-50 rounded-lg p-4">
				<div class="text-sm font-medium text-orange-600 mb-1">Collateral at Risk</div>
				<div class="text-2xl font-bold text-orange-900">{formatCurrency(summary.total_collateral_at_risk)}</div>
				<div class="text-xs text-orange-600 mt-1">Open positions</div>
			</div>
		</div>

		{#if summary.average_ar_closed_trades !== null}
			<div class="mt-4 p-4 bg-gray-50 rounded-lg">
				<div class="text-sm font-medium text-gray-600">Average AR% (Closed Trades)</div>
				<div class="text-xl font-bold text-gray-900">{formatPercent(summary.average_ar_closed_trades)}</div>
			</div>
		{/if}

		{#if summary.stocks_traded && summary.stocks_traded.length > 0}
			<div class="mt-4">
				<div class="text-sm font-medium text-gray-600 mb-2">Stocks Traded</div>
				<div class="flex flex-wrap gap-2">
					{#each summary.stocks_traded as stock}
						<span class="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium">
							{stock}
						</span>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>
