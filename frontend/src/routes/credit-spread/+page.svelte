<script>
    import {onMount} from 'svelte';
    import {browser} from '$app/environment';
    import {goto} from '$app/navigation';
    import {api} from '$lib/api';
    import CreditSpreadForm from '$lib/components/CreditSpreadForm.svelte';
    import CreditSpreadTable from '$lib/components/CreditSpreadTable.svelte';
    import CreditSpreadSummary from '$lib/components/CreditSpreadSummary.svelte';
    import Logo from '$lib/components/Logo.svelte';
    import FeedbackModal from '$lib/components/FeedbackModal.svelte';

    let spreads = $state([]);
    let summary = $state(null);
    let loading = $state(true);
    let error = $state(null);
    let showForm = $state(false);
    let editingSpread = $state(null);
    let filterStock = $state('');
    let filterType = $state('');
    let filterStatus = $state('all'); // all, open, closed
    let showFeedbackModal = $state(false);
    let feedbackSuccess = $state(false);
    let currentUser = $state(null);
    let mobileMenuOpen = $state(false);

    onMount(async () => {
        await checkAuth();
        loadData();
    });

    async function checkAuth() {
        try {
            currentUser = await api.getCurrentUser();
        } catch (err) {
            console.error('Failed to get user info:', err);
        }
    }

    async function loadData() {
        if (!browser) return;

        loading = true;
        error = null;
        try {
            const [spreadsData, summaryData] = await Promise.all([
                api.getCreditSpreads(),
                api.getCreditSpreadSummary()
            ]);
            spreads = spreadsData.results || spreadsData;
            summary = summaryData;
        } catch (err) {
            error = err.message;
            console.error('Error loading data:', err);
        } finally {
            loading = false;
        }
    }

    async function handleSave(spreadData) {
        try {
            if (editingSpread) {
                await api.updateCreditSpread(editingSpread.id, spreadData);
            } else {
                await api.createCreditSpread(spreadData);
            }
            showForm = false;
            editingSpread = null;
            await loadData();
        } catch (err) {
            error = err.message;
        }
    }

    async function handleEdit(spread) {
        editingSpread = spread;
        showForm = true;
    }

    async function handleDelete(id) {
        if (!confirm('Are you sure you want to delete this credit spread?')) return;

        try {
            await api.deleteCreditSpread(id);
            await loadData();
        } catch (err) {
            error = err.message;
        }
    }

    function handleCancel() {
        showForm = false;
        editingSpread = null;
    }

    function openNewSpreadForm() {
        editingSpread = null;
        showForm = true;
        setTimeout(() => {
            document.getElementById('spread-form')?.scrollIntoView({behavior: 'smooth', block: 'start'});
        }, 100);
    }

    function handleLogout() {
        if (browser) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            goto('/login');
        }
    }

    function handleFeedbackSuccess() {
        feedbackSuccess = true;
        setTimeout(() => {
            feedbackSuccess = false;
        }, 3000);
    }

    let filteredSpreads = $derived(() => {
        let filtered = spreads;

        if (filterStock) {
            filtered = filtered.filter(s =>
                s.stock.toLowerCase().includes(filterStock.toLowerCase())
            );
        }

        if (filterType) {
            filtered = filtered.filter(s => s.type === filterType);
        }

        if (filterStatus === 'open') {
            filtered = filtered.filter(s => s.is_open);
        } else if (filterStatus === 'closed') {
            filtered = filtered.filter(s => !s.is_open);
        }

        return filtered;
    });

    const handleMobileNewSpread = () => {
        openNewSpreadForm();
        mobileMenuOpen = false;
    }
    const handleMobileFeedback = () => {
        showFeedbackModal = true;
        mobileMenuOpen = false;
    }
    const handleMobileLogout = () => {
        handleLogout();
        mobileMenuOpen = false;
    }
</script>

<svelte:head>
    <title>Credit Spread Tracker - WheelTracker</title>
    <meta name="description"
          content="Track your credit spread options trading. Monitor bull put spreads and bear call spreads with detailed ROI calculations."/>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
    <!-- Responsive Header -->
    <header class="bg-white border-b border-gray-200 shadow-sm">
        <div class="mx-auto px-4 py-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center">
                <!-- Logo and Brand -->
                <div class="flex items-center gap-2">
                    <Logo size={32}/>
                    <h1 class="text-xl font-bold text-gray-900">WheelTracker</h1>
                </div>

                <!-- Desktop Navigation -->
                <nav class="hidden lg:flex items-center gap-2">
                    <a
                            href="/"
                            class="text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer"
                    >
                        Wheel Strategy
                    </a>
                    <button
                            onclick={openNewSpreadForm}
                            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 cursor-pointer"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                        </svg>
                        <span>New Spread</span>
                    </button>
                    {#if currentUser?.is_superuser || currentUser?.is_staff}
                        <a
                                href="/admin/feedback"
                                class="text-blue-600 hover:text-blue-700 hover:bg-blue-50 px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer flex items-center gap-1.5"
                                title="Manage Feedback"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            <span>Admin</span>
                        </a>
                    {/if}
                    <button
                            onclick={() => showFeedbackModal = true}
                            class="text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer flex items-center gap-1.5"
                            title="Send Feedback"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                        </svg>
                        <span>Feedback</span>
                    </button>
                    <button
                            onclick={handleLogout}
                            class="text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer"
                            title="Logout"
                    >
                        Logout
                    </button>
                </nav>

                <!-- Mobile Menu Button -->
                <button
                        onclick={() => mobileMenuOpen = !mobileMenuOpen}
                        class="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 cursor-pointer"
                        aria-label="Toggle menu"
                >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        {#if mobileMenuOpen}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M6 18L18 6M6 6l12 12"></path>
                        {:else}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M4 6h16M4 12h16M4 18h16"></path>
                        {/if}
                    </svg>
                </button>
            </div>

            <!-- Mobile Navigation Menu -->
            {#if mobileMenuOpen}
                <div class="lg:hidden mt-4 pb-3 space-y-2 border-t border-gray-200 pt-4">
                    <a
                            href="/"
                            class="w-full text-left text-gray-700 hover:bg-gray-100 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2"
                            onclick={() => mobileMenuOpen = false}
                    >
                        <span>Wheel Strategy</span>
                    </a>
                    <button
                            onclick={handleMobileNewSpread}
                            class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 cursor-pointer"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                        </svg>
                        <span>New Spread</span>
                    </button>
                    {#if currentUser?.is_superuser || currentUser?.is_staff}
                        <a
                                href="/admin/feedback"
                                class="w-full text-blue-600 hover:bg-blue-50 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2"
                                onclick={() => mobileMenuOpen = false}
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            <span>Admin Dashboard</span>
                        </a>
                    {/if}
                    <button
                            onclick={handleMobileFeedback}
                            class="w-full text-left text-gray-700 hover:bg-gray-100 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 cursor-pointer"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                        </svg>
                        <span>Send Feedback</span>
                    </button>
                    <button
                            onclick={handleMobileLogout}
                            class="w-full text-left text-red-600 hover:bg-red-50 px-4 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer"
                    >
                        Logout
                    </button>
                </div>
            {/if}
        </div>
    </header>

    <main class="mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {#if feedbackSuccess}
            <div class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg mb-6">
                <p class="font-bold">Feedback submitted successfully!</p>
                <p>Thank you for your feedback. We'll review it shortly.</p>
            </div>
        {/if}

        {#if error}
            <div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
                <p class="font-bold">Error loading data:</p>
                <p>{error}</p>
                <p class="text-sm mt-2">Make sure Django server is running: <code
                        class="bg-red-100 px-1 py-0.5 rounded">python manage.py runserver</code></p>
                <p class="text-sm mt-1">Then refresh this page.</p>
            </div>
        {/if}

        {#if loading && !spreads.length}
            <div class="flex justify-center items-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        {:else}
            {#if summary}
                <CreditSpreadSummary {summary}/>
            {/if}

            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h2 class="text-xl font-bold text-gray-900 mb-4">Filters</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label for="filter-stock" class="block text-sm font-medium text-gray-700 mb-1">Stock
                            Symbol</label>
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
                            <option value="BPS">Bull Put Spread</option>
                            <option value="BCS">Bear Call Spread</option>
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
                <div id="spread-form" class="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 class="text-xl font-bold text-gray-900 mb-4">
                        {editingSpread ? 'Edit Credit Spread' : 'New Credit Spread'}
                    </h2>
                    <CreditSpreadForm
                            spread={editingSpread}
                            onSave={handleSave}
                            onCancel={handleCancel}
                    />
                </div>
            {/if}

            <CreditSpreadTable
                    spreads={filteredSpreads()}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
            />
        {/if}
    </main>

    <!-- Feedback Modal -->
    <FeedbackModal bind:show={showFeedbackModal} onSuccess={handleFeedbackSuccess}/>
</div>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
    }
</style>
