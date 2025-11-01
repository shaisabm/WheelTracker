<script>
	let { position = null, onSave, onCancel, availablePositions = [] } = $props();

	// Initialize form data
	let formData = $state({
		open_date: position?.open_date || '',
		stock: position?.stock || '',
		related_to: position?.related_to || null,
		wheel_cycle_name: position?.wheel_cycle_name || '',
		expiration: position?.expiration || '',
		type: position?.type || 'P',
		num_contracts: position?.num_contracts || 1,
		strike: position?.strike || '',
		premium: position?.premium || '',
		open_fees: position?.open_fees || '0.00',
		close_date: position?.close_date || '',
		assigned: position?.assigned || 'No',
		premium_paid_to_close: position?.premium_paid_to_close || '',
		close_fees: position?.close_fees || '0.00',
		notes: position?.notes || '',
	});

	// Track if this is a continuation of an existing wheel
	let isNewWheel = $derived(!formData.related_to);

	// When a related position is selected, auto-fill stock and wheel cycle name
	$effect(() => {
		if (formData.related_to) {
			const relatedPos = availablePositions.find(p => p.id === formData.related_to);
			if (relatedPos) {
				formData.stock = relatedPos.stock;
				if (relatedPos.wheel_cycle_name) {
					formData.wheel_cycle_name = relatedPos.wheel_cycle_name;
				}
			}
		}
	});

	let errors = $state({});

	function validate() {
		errors = {};

		if (!formData.open_date) errors.open_date = 'Required';
		if (!formData.stock) errors.stock = 'Required';
		if (!formData.expiration) errors.expiration = 'Required';
		if (!formData.num_contracts || formData.num_contracts < 1) errors.num_contracts = 'Must be at least 1';
		if (!formData.strike || formData.strike <= 0) errors.strike = 'Must be greater than 0';
		if (!formData.premium && formData.premium !== 0) errors.premium = 'Required';

		// Validate dates
		if (formData.open_date && formData.expiration && formData.open_date > formData.expiration) {
			errors.expiration = 'Must be after open date';
		}

		if (formData.close_date && formData.open_date && formData.close_date < formData.open_date) {
			errors.close_date = 'Must be after open date';
		}

		// If close_date is provided, premium_paid_to_close is required
		if (formData.close_date && !formData.premium_paid_to_close && formData.premium_paid_to_close !== 0) {
			errors.premium_paid_to_close = 'Required when closing';
		}

		return Object.keys(errors).length === 0;
	}

	function handleSubmit(e) {
		e.preventDefault();
		if (validate()) {
			// Convert stock to uppercase
			const data = {
				...formData,
				stock: formData.stock.toUpperCase(),
				// Convert empty strings to null for optional fields
				close_date: formData.close_date || null,
				premium_paid_to_close: formData.premium_paid_to_close === '' ? null : formData.premium_paid_to_close,
			};
			onSave(data);
		}
	}
</script>

<form onsubmit={handleSubmit} class="space-y-6">
	<!-- Wheel Cycle Section -->
	<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
		<h3 class="text-sm font-semibold text-blue-900 mb-3">Wheel Cycle Tracking</h3>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<!-- Related To - First field -->
			<div>
				<label for="related-to" class="block text-sm font-medium text-gray-700 mb-1">
					Continue Existing Wheel?
				</label>
				<select
					id="related-to"
					bind:value={formData.related_to}
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white cursor-pointer"
				>
					<option value={null}>No - Start new wheel cycle</option>
					{#each availablePositions as pos}
						<option value={pos.id}>
							{pos.stock} - {pos.type === 'P' ? 'Put' : 'Call'} ${pos.strike} (opened {pos.open_date})
						</option>
					{/each}
				</select>
				<p class="text-xs text-gray-600 mt-1">
					{isNewWheel ? 'Starting a new wheel cycle' : 'Continuing an existing wheel cycle'}
				</p>
			</div>

			<!-- Wheel Cycle Name -->
			<div>
				<label for="wheel-cycle-name" class="block text-sm font-medium text-gray-700 mb-1">
					Wheel Cycle Name (Optional)
				</label>
				<input
					id="wheel-cycle-name"
					type="text"
					bind:value={formData.wheel_cycle_name}
					placeholder="e.g., AAPL Jan 2025"
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
					disabled={!isNewWheel && !formData.wheel_cycle_name}
				/>
				<p class="text-xs text-gray-600 mt-1">
					{isNewWheel ? 'Give this wheel cycle a name' : 'Inherited from related position'}
				</p>
			</div>
		</div>
	</div>

	<!-- Position Details Section -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
		<!-- Open Date -->
		<div>
			<label for="open-date" class="block text-sm font-medium text-gray-700 mb-1">
				Open Date <span class="text-red-500">*</span>
			</label>
			<input
				id="open-date"
				type="date"
				bind:value={formData.open_date}
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
				class:border-red-500={errors.open_date}
			/>
			{#if errors.open_date}
				<p class="text-red-500 text-xs mt-1">{errors.open_date}</p>
			{/if}
		</div>

		<!-- Stock - Only show if new wheel -->
		{#if isNewWheel}
			<div>
				<label for="stock" class="block text-sm font-medium text-gray-700 mb-1">
					Stock Ticker <span class="text-red-500">*</span>
				</label>
				<input
					id="stock"
					type="text"
					bind:value={formData.stock}
					placeholder="e.g., AAPL"
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase"
					class:border-red-500={errors.stock}
				/>
				{#if errors.stock}
					<p class="text-red-500 text-xs mt-1">{errors.stock}</p>
				{/if}
			</div>
		{:else}
			<!-- Show stock as read-only when continuing a wheel -->
			<div>
				<label for="stock-display" class="block text-sm font-medium text-gray-700 mb-1">
					Stock Ticker
				</label>
				<input
					id="stock-display"
					type="text"
					value={formData.stock}
					disabled
					class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-700 cursor-not-allowed"
				/>
				<p class="text-xs text-gray-500 mt-1">Inherited from related position</p>
			</div>
		{/if}

		<!-- Expiration -->
		<div>
			<label for="expiration" class="block text-sm font-medium text-gray-700 mb-1">
				Expiration <span class="text-red-500">*</span>
			</label>
			<input
				id="expiration"
				type="date"
				bind:value={formData.expiration}
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
				class:border-red-500={errors.expiration}
			/>
			{#if errors.expiration}
				<p class="text-red-500 text-xs mt-1">{errors.expiration}</p>
			{/if}
		</div>

		<!-- Type -->
		<div>
			<label for="type" class="block text-sm font-medium text-gray-700 mb-1">
				Type <span class="text-red-500">*</span>
			</label>
			<select
				id="type"
				bind:value={formData.type}
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
			>
				<option value="P">Put</option>
				<option value="C">Call</option>
			</select>
		</div>

		<!-- Number of Contracts -->
		<div>
			<label for="num-contracts" class="block text-sm font-medium text-gray-700 mb-1">
				# Contracts <span class="text-red-500">*</span>
			</label>
			<input
				id="num-contracts"
				type="number"
				bind:value={formData.num_contracts}
				min="1"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
				class:border-red-500={errors.num_contracts}
			/>
			{#if errors.num_contracts}
				<p class="text-red-500 text-xs mt-1">{errors.num_contracts}</p>
			{/if}
		</div>

		<!-- Strike -->
		<div>
			<label for="strike" class="block text-sm font-medium text-gray-700 mb-1">
				Strike <span class="text-red-500">*</span>
			</label>
			<input
				id="strike"
				type="number"
				bind:value={formData.strike}
				step="0.001"
				min="0.01"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
				class:border-red-500={errors.strike}
			/>
			{#if errors.strike}
				<p class="text-red-500 text-xs mt-1">{errors.strike}</p>
			{/if}
		</div>

		<!-- Premium -->
		<div>
			<label for="premium" class="block text-sm font-medium text-gray-700 mb-1">
				Premium <span class="text-red-500">*</span>
			</label>
			<input
				id="premium"
				type="number"
				bind:value={formData.premium}
				step="0.001"
				min="0"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
				class:border-red-500={errors.premium}
			/>
			{#if errors.premium}
				<p class="text-red-500 text-xs mt-1">{errors.premium}</p>
			{/if}
		</div>

		<!-- Open Fees -->
		<div>
			<label for="open-fees" class="block text-sm font-medium text-gray-700 mb-1">
				Open Fees
			</label>
			<input
				id="open-fees"
				type="number"
				bind:value={formData.open_fees}
				step="0.001"
				min="0"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
			/>
		</div>

		<!-- Close Date -->
		<div>
			<label for="close-date" class="block text-sm font-medium text-gray-700 mb-1">
				Close Date
			</label>
			<input
				id="close-date"
				type="date"
				bind:value={formData.close_date}
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
				class:border-red-500={errors.close_date}
			/>
			{#if errors.close_date}
				<p class="text-red-500 text-xs mt-1">{errors.close_date}</p>
			{/if}
		</div>

		<!-- Assigned -->
		<div>
			<label for="assigned" class="block text-sm font-medium text-gray-700 mb-1">
				Assigned
			</label>
			<select
				id="assigned"
				bind:value={formData.assigned}
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
			>
				<option value="Yes">Yes</option>
				<option value="No">No</option>
			</select>
		</div>

		<!-- Premium Paid to Close -->
		<div>
			<label for="premium-paid" class="block text-sm font-medium text-gray-700 mb-1">
				Premium Paid to Close
			</label>
			<input
				id="premium-paid"
				type="number"
				bind:value={formData.premium_paid_to_close}
				step="0.001"
				min="0"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
				class:border-red-500={errors.premium_paid_to_close}
			/>
			{#if errors.premium_paid_to_close}
				<p class="text-red-500 text-xs mt-1">{errors.premium_paid_to_close}</p>
			{/if}
		</div>

		<!-- Close Fees -->
		<div>
			<label for="close-fees" class="block text-sm font-medium text-gray-700 mb-1">
				Close Fees
			</label>
			<input
				id="close-fees"
				type="number"
				bind:value={formData.close_fees}
				step="0.001"
				min="0"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
			/>
		</div>

	</div>

	<!-- Notes -->
	<div>
		<label for="notes" class="block text-sm font-medium text-gray-700 mb-1">
			Notes
		</label>
		<textarea
			id="notes"
			bind:value={formData.notes}
			rows="3"
			placeholder="Any notes about this position..."
			class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
		></textarea>
	</div>

	<!-- Form Actions -->
	<div class="flex justify-end gap-3">
		<button
			type="button"
			onclick={onCancel}
			class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium cursor-pointer"
		>
			Cancel
		</button>
		<button
			type="submit"
			class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium cursor-pointer"
		>
			{position ? 'Update' : 'Create'} Position
		</button>
	</div>
</form>
