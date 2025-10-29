<script>
	let { positions = [], onEdit, onDelete } = $props();

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

	function formatDate(dateString) {
		if (!dateString) return '-';
		// Parse as local date to avoid timezone conversion issues
		// Date string format: "YYYY-MM-DD"
		const [year, month, day] = dateString.split('-');
		const date = new Date(year, month - 1, day);
		return date.toLocaleDateString('en-US');
	}

	function getStatusBadge(position) {
		if (position.is_open) {
			return { text: 'Open', class: 'bg-green-100 text-green-800' };
		}
		return { text: 'Closed', class: 'bg-gray-100 text-gray-800' };
	}

	function getTypeBadge(type) {
		if (type === 'P') {
			return { text: 'Put', class: 'bg-red-100 text-red-800' };
		}
		return { text: 'Call', class: 'bg-blue-100 text-blue-800' };
	}
</script>

<div class="bg-white rounded-lg shadow overflow-hidden">
	<div class="px-6 py-4 border-b border-gray-200">
		<h2 class="text-xl font-bold text-gray-900">Positions ({positions.length})</h2>
	</div>

	{#if positions.length === 0}
		<div class="p-12 text-center text-gray-500">
			<svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
			</svg>
			<p class="text-lg font-medium">No positions found</p>
			<p class="text-sm mt-1">Create your first position to get started</p>
		</div>
	{:else}
		<div class="overflow-x-auto">
			<table class="min-w-full divide-y divide-gray-200">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Wheel Cycle</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strike</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contracts</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Premium</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Open Date</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expiration</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">DTE</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P/L</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">AR%</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each positions as position}
						{@const typeBadge = getTypeBadge(position.type)}
						{@const statusBadge = getStatusBadge(position)}
						<tr class="hover:bg-gray-50">
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm font-medium text-gray-900">{position.stock}</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm text-gray-900">
									{#if position.wheel_cycle_name}
										{position.wheel_cycle_name}
									{:else if position.wheel_cycle_number > 1}
										Step {position.wheel_cycle_number}
									{:else}
										-
									{/if}
								</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full {typeBadge.class}">
									{typeBadge.text}
								</span>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm text-gray-900">${position.strike}</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm text-gray-900">{position.num_contracts}</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm text-gray-900">${position.premium}</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm text-gray-500">{formatDate(position.open_date)}</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm text-gray-500">{formatDate(position.expiration)}</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm text-gray-900">
									{#if position.is_open}
										{position.days_to_expiration}
									{:else}
										-
									{/if}
								</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full {statusBadge.class}">
									{statusBadge.text}
								</span>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm font-medium" class:text-green-600={position.profit_loss > 0} class:text-red-600={position.profit_loss < 0}>
									{formatCurrency(position.profit_loss)}
								</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm text-gray-900">
									{#if position.is_open}
										{formatPercent(position.ar_if_held_to_expiration)}
									{:else}
										{formatPercent(position.ar_of_closed_trade)}
									{/if}
								</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap text-sm font-medium">
								<div class="flex gap-2">
									<button
										onclick={() => onEdit(position)}
										class="text-blue-600 hover:text-blue-900 cursor-pointer"
										title="Edit"
									>
										<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
										</svg>
									</button>
									<button
										onclick={() => onDelete(position.id)}
										class="text-red-600 hover:text-red-900 cursor-pointer"
										title="Delete"
									>
										<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
										</svg>
									</button>
								</div>
							</td>
						</tr>

						<!-- Expandable row for additional details -->
						{#if position.notes || position.assigned === 'Yes'}
							<tr class="bg-gray-50">
								<td colspan="13" class="px-4 py-3">
									<div class="text-sm text-gray-700">
										<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
											{#if position.notes}
												<div>
													<span class="font-medium">Notes:</span> {position.notes}
												</div>
											{/if}
											{#if position.assigned === 'Yes'}
												<div>
													<span class="font-medium">Assigned:</span>
													<span class="text-red-600">Yes</span>
												</div>
											{/if}
											{#if position.percent_premium_earned !== null}
												<div>
													<span class="font-medium">Premium Earned:</span> {formatPercent(position.percent_premium_earned)}
												</div>
											{/if}
											{#if position.ar_on_realized_premium !== null}
												<div>
													<span class="font-medium">AR% on Realized:</span> {formatPercent(position.ar_on_realized_premium)}
												</div>
											{/if}
											{#if position.ar_on_remaining_premium !== null}
												<div>
													<span class="font-medium">AR% on Remaining:</span> {formatPercent(position.ar_on_remaining_premium)}
												</div>
											{/if}
											{#if position.set_break_even_price_puts !== null}
												<div>
													<span class="font-medium">Break Even (Put):</span> {formatCurrency(position.set_break_even_price_puts)}
												</div>
											{/if}
										</div>
									</div>
								</td>
							</tr>
						{/if}
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
