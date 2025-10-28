<script>
	let { position = null, onSave, onCancel } = $props();

	// Initialize form data
	let formData = $state({
		open_date: position?.open_date || '',
		stock: position?.stock || '',
		set_number: position?.set_number || 1,
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
				premium_paid_to_close: formData.premium_paid_to_close || null,
			};
			onSave(data);
		}
	}
</script>

<form onsubmit={handleSubmit} class="space-y-6">
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
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				class:border-red-500={errors.open_date}
			/>
			{#if errors.open_date}
				<p class="text-red-500 text-xs mt-1">{errors.open_date}</p>
			{/if}
		</div>

		<!-- Stock -->
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

		<!-- Set Number -->
		<div>
			<label for="set-number" class="block text-sm font-medium text-gray-700 mb-1">
				Set Number
			</label>
			<input
				id="set-number"
				type="number"
				bind:value={formData.set_number}
				min="1"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			/>
		</div>

		<!-- Expiration -->
		<div>
			<label for="expiration" class="block text-sm font-medium text-gray-700 mb-1">
				Expiration <span class="text-red-500">*</span>
			</label>
			<input
				id="expiration"
				type="date"
				bind:value={formData.expiration}
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
				step="0.01"
				min="0.01"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
				step="0.01"
				min="0"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
				step="0.01"
				min="0"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
				step="0.01"
				min="0"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
				step="0.01"
				min="0"
				placeholder="0.00"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
			class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
		></textarea>
	</div>

	<!-- Form Actions -->
	<div class="flex justify-end gap-3">
		<button
			type="button"
			onclick={onCancel}
			class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
		>
			Cancel
		</button>
		<button
			type="submit"
			class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
		>
			{position ? 'Update' : 'Create'} Position
		</button>
	</div>
</form>
