<script>
	let { position = null, onSave, onCancel, availablePositions = [] } = $props();

	// Track if we're in roll mode
	let isRolling = $state(false);

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
		entry_price: position?.entry_price || '',
		premium: position?.premium || '',
		open_fees: position?.open_fees || '0.00',
		close_date: position?.close_date || '',
		assigned: position?.assigned || 'No',
		premium_paid_to_close: position?.premium_paid_to_close || '',
		close_fees: position?.close_fees || '0.00',
		notes: position?.notes || '',
	});

	// Roll form data for the new position
	let rollData = $state({
		open_date: '',
		expiration: '',
		strike: '',
		entry_price: '',
		num_contracts: position?.num_contracts || 1,
		premium: '',
		open_fees: '0.00',
	});

	// Track if this is a continuation of an existing wheel
	let isNewWheel = $derived(!formData.related_to);

	// When a related position is selected, auto-fill stock and wheel cycle name
	$effect(() => {
		if (formData.related_to) {
			const relatedPos = availablePositions.find(p => p.id === formData.related_to);
			if (relatedPos) {
				formData.stock = relatedPos.stock;
				// Set wheel cycle name using the PREVIOUS position's expiration date
				// Only set if there's an existing wheel_cycle_name OR if it's empty
				if (relatedPos.wheel_cycle_name) {
					formData.wheel_cycle_name = relatedPos.wheel_cycle_name;
				} else if (!formData.wheel_cycle_name || formData.wheel_cycle_name === '') {
					formData.wheel_cycle_name = `${relatedPos.stock} ${relatedPos.expiration} continues`;
				}
			}
		}
	});

	let errors = $state({});

	function enableRoll() {
		isRolling = true;
		// Set today as default close date for rolling
		const today = new Date().toISOString().split('T')[0];
		formData.close_date = today;
		rollData.open_date = today;
	}

	function cancelRoll() {
		isRolling = false;
		// Clear roll-related fields
		formData.close_date = position?.close_date || '';
		formData.premium_paid_to_close = position?.premium_paid_to_close || '';
		formData.close_fees = position?.close_fees || '0.00';
		rollData = {
			open_date: '',
			expiration: '',
			strike: '',
			entry_price: '',
			num_contracts: position?.num_contracts || 1,
			premium: '',
			open_fees: '0.00',
		};
	}

	function validate() {
		errors = {};

		if (isRolling) {
			// Validate closing fields when rolling
			if (!formData.close_date) errors.close_date = 'Required when rolling';
			if (!formData.premium_paid_to_close && formData.premium_paid_to_close !== 0) {
				errors.premium_paid_to_close = 'Required when rolling';
			}
			if (!formData.close_fees && formData.close_fees !== 0) {
				errors.close_fees = 'Required when rolling';
			}

			// Validate new roll position fields
			if (!rollData.open_date) errors.roll_open_date = 'Required';
			if (!rollData.expiration) errors.roll_expiration = 'Required';
			if (!rollData.strike || rollData.strike <= 0) errors.roll_strike = 'Must be greater than 0';
			if (!rollData.num_contracts || rollData.num_contracts < 1) errors.roll_num_contracts = 'Must be at least 1';
			if (!rollData.premium && rollData.premium !== 0) errors.roll_premium = 'Required';
		} else {
			// Normal validation
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
		}

		return Object.keys(errors).length === 0;
	}

	function handleSubmit(e) {
		e.preventDefault();
		if (validate()) {
			if (isRolling) {
				// Submit roll data
				const rollSubmission = {
					isRoll: true,
					closePosition: {
						...formData,
						stock: formData.stock.toUpperCase(),
						close_date: formData.close_date,
						premium_paid_to_close: formData.premium_paid_to_close,
						close_fees: formData.close_fees,
					},
					newPosition: {
						open_date: rollData.open_date,
						stock: formData.stock.toUpperCase(),
						related_to: position.id,
						wheel_cycle_name: `Rolled from ${formData.expiration}`,
						expiration: rollData.expiration,
						type: formData.type,
						num_contracts: rollData.num_contracts,
						strike: rollData.strike,
						entry_price: rollData.entry_price === '' ? null : rollData.entry_price,
						premium: rollData.premium,
						open_fees: rollData.open_fees,
						close_date: null,
						assigned: 'No',
						premium_paid_to_close: null,
						close_fees: '0.00',
						notes: '',
					}
				};
				onSave(rollSubmission);
			} else {
				// Normal save
				const data = {
					...formData,
					stock: formData.stock.toUpperCase(),
					// Convert empty strings to null for optional fields
					close_date: formData.close_date || null,
					entry_price: formData.entry_price === '' ? null : formData.entry_price,
					premium_paid_to_close: formData.premium_paid_to_close === '' ? null : formData.premium_paid_to_close,
				};
				onSave(data);
			}
		}
	}
</script>

<form onsubmit={handleSubmit} class="space-y-6">
	<!-- Roll Button (only show when editing and position is open) -->
	{#if position && !position.close_date && !isRolling}
		<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
			<div class="flex justify-between items-center">
				<div>
					<h3 class="text-sm font-semibold text-yellow-900">Roll this position?</h3>
					<p class="text-xs text-yellow-700 mt-1">Close the current position and open a new one with updated terms</p>
				</div>
				<button
					type="button"
					onclick={enableRoll}
					class="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm font-medium cursor-pointer"
				>
					Enable Roll
				</button>
			</div>
		</div>
	{/if}

	<!-- Roll Form (shown when rolling) -->
	{#if isRolling}
		<div class="bg-green-50 border border-green-200 rounded-lg p-4 space-y-4">
			<div class="flex justify-between items-center mb-4">
				<h3 class="text-lg font-semibold text-green-900">Rolling Position</h3>
				<button
					type="button"
					onclick={cancelRoll}
					class="text-sm text-green-700 hover:text-green-900 underline cursor-pointer"
				>
					Cancel Roll
				</button>
			</div>

			<!-- Closing Position Section -->
			<div class="border-b border-green-300 pb-4">
				<h4 class="text-sm font-semibold text-green-900 mb-3">1. Close Current Position</h4>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<!-- Close Date -->
					<div>
						<label for="roll-close-date" class="block text-sm font-medium text-gray-700 mb-1">
							Close Date <span class="text-red-500">*</span>
						</label>
						<input
							id="roll-close-date"
							type="date"
							bind:value={formData.close_date}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
							class:border-red-500={errors.close_date}
						/>
						{#if errors.close_date}
							<p class="text-red-500 text-xs mt-1">{errors.close_date}</p>
						{/if}
					</div>

					<!-- Premium Paid to Close -->
					<div>
						<label for="roll-premium-paid" class="block text-sm font-medium text-gray-700 mb-1">
							Premium Paid to Close <span class="text-red-500">*</span>
						</label>
						<input
							id="roll-premium-paid"
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
						<label for="roll-close-fees" class="block text-sm font-medium text-gray-700 mb-1">
							Close Fees <span class="text-red-500">*</span>
						</label>
						<input
							id="roll-close-fees"
							type="number"
							bind:value={formData.close_fees}
							step="0.001"
							min="0"
							placeholder="0.00"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
							class:border-red-500={errors.close_fees}
						/>
						{#if errors.close_fees}
							<p class="text-red-500 text-xs mt-1">{errors.close_fees}</p>
						{/if}
					</div>
				</div>
			</div>

			<!-- New Position Section -->
			<div>
				<h4 class="text-sm font-semibold text-green-900 mb-3">2. Open New Rolled Position</h4>
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					<!-- Open Date -->
					<div>
						<label for="roll-open-date" class="block text-sm font-medium text-gray-700 mb-1">
							Open Date <span class="text-red-500">*</span>
						</label>
						<input
							id="roll-open-date"
							type="date"
							bind:value={rollData.open_date}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
							class:border-red-500={errors.roll_open_date}
						/>
						{#if errors.roll_open_date}
							<p class="text-red-500 text-xs mt-1">{errors.roll_open_date}</p>
						{/if}
					</div>

					<!-- Expiration -->
					<div>
						<label for="roll-expiration" class="block text-sm font-medium text-gray-700 mb-1">
							New Expiration <span class="text-red-500">*</span>
						</label>
						<input
							id="roll-expiration"
							type="date"
							bind:value={rollData.expiration}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
							class:border-red-500={errors.roll_expiration}
						/>
						{#if errors.roll_expiration}
							<p class="text-red-500 text-xs mt-1">{errors.roll_expiration}</p>
						{/if}
					</div>

					<!-- Strike -->
					<div>
						<label for="roll-strike" class="block text-sm font-medium text-gray-700 mb-1">
							New Strike <span class="text-red-500">*</span>
						</label>
						<input
							id="roll-strike"
							type="number"
							bind:value={rollData.strike}
							step="0.001"
							min="0.01"
							placeholder="0.00"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
							class:border-red-500={errors.roll_strike}
						/>
						{#if errors.roll_strike}
							<p class="text-red-500 text-xs mt-1">{errors.roll_strike}</p>
						{/if}
					</div>

					<!-- Entry Price -->
					<div>
						<label for="roll-entry-price" class="block text-sm font-medium text-gray-700 mb-1">
							Entry Price
						</label>
						<input
							id="roll-entry-price"
							type="number"
							bind:value={rollData.entry_price}
							step="0.001"
							min="0"
							placeholder="Stock price at entry"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
						/>
					</div>

					<!-- Contracts -->
					<div>
						<label for="roll-contracts" class="block text-sm font-medium text-gray-700 mb-1">
							# Contracts <span class="text-red-500">*</span>
						</label>
						<input
							id="roll-contracts"
							type="number"
							bind:value={rollData.num_contracts}
							min="1"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
							class:border-red-500={errors.roll_num_contracts}
						/>
						{#if errors.roll_num_contracts}
							<p class="text-red-500 text-xs mt-1">{errors.roll_num_contracts}</p>
						{/if}
					</div>

					<!-- Premium -->
					<div>
						<label for="roll-premium" class="block text-sm font-medium text-gray-700 mb-1">
							Premium Received <span class="text-red-500">*</span>
						</label>
						<input
							id="roll-premium"
							type="number"
							bind:value={rollData.premium}
							step="0.001"
							min="0"
							placeholder="0.00"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
							class:border-red-500={errors.roll_premium}
						/>
						{#if errors.roll_premium}
							<p class="text-red-500 text-xs mt-1">{errors.roll_premium}</p>
						{/if}
					</div>

					<!-- Open Fees -->
					<div>
						<label for="roll-open-fees" class="block text-sm font-medium text-gray-700 mb-1">
							Open Fees
						</label>
						<input
							id="roll-open-fees"
							type="number"
							bind:value={rollData.open_fees}
							step="0.001"
							min="0"
							placeholder="0.00"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
						/>
					</div>
				</div>
				<p class="text-xs text-gray-600 mt-2">
					Stock: <strong>{formData.stock}</strong> | Type: <strong>{formData.type === 'P' ? 'Put' : 'Call'}</strong> |
					Wheel Cycle: <strong>Rolled from {formData.expiration}</strong>
				</p>
			</div>
		</div>
	{/if}

	<!-- Wheel Cycle Section -->
	{#if !isRolling}
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
				/>
				<p class="text-xs text-gray-600 mt-1">
					{isNewWheel ? 'Give this wheel cycle a name' : 'Auto-generated for wheel continuation (editable)'}
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

		<!-- Entry Price -->
		<div>
			<label for="entry-price" class="block text-sm font-medium text-gray-700 mb-1">
				Entry Price
			</label>
			<input
				id="entry-price"
				type="number"
				bind:value={formData.entry_price}
				step="0.001"
				min="0"
				placeholder="Stock price at entry"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
			/>
			<p class="text-xs text-gray-500 mt-1">Stock price when you entered the position</p>
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
	{/if}

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
			{#if isRolling}
				Roll Position
			{:else}
				{position ? 'Update' : 'Create'} Position
			{/if}
		</button>
	</div>
</form>
