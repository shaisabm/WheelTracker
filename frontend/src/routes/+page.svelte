<script>
    import {onMount} from 'svelte';
    import {browser} from '$app/environment';
    import {goto} from '$app/navigation';
    import {api} from '$lib/api';
    import PositionForm from '$lib/components/PositionForm.svelte';
    import PositionTable from '$lib/components/PositionTable.svelte';
    import Summary from '$lib/components/Summary.svelte';
    import RoiSummary from '$lib/components/RoiSummary.svelte';
    import Logo from '$lib/components/Logo.svelte';
    import FeedbackModal from '$lib/components/FeedbackModal.svelte';
    import NotificationButton from '$lib/components/NotificationButton.svelte';
    import NotificationPanel from '$lib/components/NotificationPanel.svelte';

    let positions = $state([]);
    let summary = $state(null);
    let loading = $state(true);
    let error = $state(null);
    let showForm = $state(false);
    let editingPosition = $state(null);
    let filterStock = $state('');
    let filterType = $state('');
    let filterStatus = $state('all'); // all, open, closed
    let showFeedbackModal = $state(false);
    let feedbackSuccess = $state(false);
    let currentUser = $state(null);
    let mobileMenuOpen = $state(false);
    let showNotificationPanel = $state(false);

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
            document.getElementById('position-form')?.scrollIntoView({behavior: 'smooth', block: 'start'});
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

    const handleMobileNewPosition = () => {
        openNewPositionForm();
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
    const handleMobileNotifications = () => {
        showNotificationPanel = true;
        mobileMenuOpen = false;
    }

</script>

<svelte:head>
    <title>WheelTracker - Options Wheel Strategy Platform</title>
    <meta name="description"
          content="Professional options trading tracker for the wheel strategy. Track positions, calculate ROI, and manage your covered calls and cash-secured puts."/>
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
                    <button
                            onclick={openNewPositionForm}
                            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 cursor-pointer"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                        </svg>
                        <span>New Position</span>
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
                    <!-- Notifications -->
                    <div class="relative">
                        <NotificationButton bind:showPanel={showNotificationPanel} />
                        <NotificationPanel bind:show={showNotificationPanel} />
                    </div>
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
                    <a
                            href="https://buymeacoffee.com/shaisabm"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="bg-yellow-400 hover:bg-yellow-500 text-gray-900 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5"
                            title="Buy me a coffee"
                    >
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M20.216 6.415l-.132-.666c-.119-.598-.388-1.163-1.001-1.379-.197-.069-.42-.098-.57-.241-.152-.143-.196-.366-.231-.572-.065-.378-.125-.756-.192-1.133-.057-.325-.102-.69-.25-.987-.195-.4-.597-.634-.996-.788a5.723 5.723 0 00-.626-.194c-1-.263-2.05-.36-3.077-.416a25.834 25.834 0 00-3.7.062c-.915.083-1.88.184-2.75.5-.318.116-.646.256-.888.501-.297.302-.393.77-.177 1.146.154.267.415.456.692.58.36.162.737.284 1.123.366 1.075.238 2.189.331 3.287.37 1.218.05 2.437.01 3.65-.118.299-.033.598-.073.896-.119.352-.054.578-.513.474-.834-.124-.383-.457-.531-.834-.473-.466.074-.96.108-1.382.146-1.177.08-2.358.082-3.536.006a22.228 22.228 0 01-1.157-.107c-.086-.01-.18-.025-.258-.036-.243-.036-.484-.08-.724-.13-.111-.027-.111-.185 0-.212h.005c.277-.06.557-.108.838-.147h.002c.131-.009.263-.032.394-.048a25.076 25.076 0 013.426-.12c.674.019 1.347.067 2.017.144l.228.031c.267.04.533.088.798.145.392.085.895.113 1.07.542.055.137.08.288.111.431l.319 1.484a.237.237 0 01-.199.284h-.003c-.037.006-.075.01-.112.015a36.704 36.704 0 01-4.743.295 37.059 37.059 0 01-4.699-.304c-.14-.017-.293-.042-.417-.06-.326-.048-.649-.108-.973-.161-.393-.065-.768-.032-1.123.161-.29.16-.527.404-.675.701-.154.316-.199.66-.267 1-.069.34-.176.707-.135 1.056.087.753.613 1.365 1.37 1.502a39.69 39.69 0 0011.343.376.483.483 0 01.535.53l-.071.697-1.018 9.907c-.041.41-.047.832-.125 1.237-.122.637-.553 1.028-1.182 1.171-.577.131-1.165.2-1.756.205-.656.004-1.31-.025-1.966-.022-.699.004-1.556-.06-2.095-.58-.475-.458-.54-1.174-.605-1.793l-.731-7.013-.322-3.094c-.037-.351-.286-.695-.678-.678-.336.015-.718.3-.678.679l.228 2.185.949 9.112c.147 1.344 1.174 2.068 2.446 2.272.742.12 1.503.144 2.257.156.966.016 1.942.053 2.892-.122 1.408-.258 2.465-1.198 2.616-2.657.34-3.332.683-6.663 1.024-9.995l.215-2.087a.484.484 0 01.39-.426c.402-.078.787-.212 1.074-.518.455-.488.546-1.124.385-1.766zm-1.478.772c-.145.137-.363.201-.578.233-2.416.359-4.866.54-7.308.46-1.748-.06-3.477-.254-5.207-.498-.17-.024-.353-.055-.47-.18-.22-.236-.111-.71-.054-.995.052-.26.152-.609.463-.646.484-.057 1.046.148 1.526.22.577.088 1.156.159 1.737.212 2.48.226 5.002.19 7.472-.14.45-.06.899-.13 1.345-.21.399-.072.84-.206 1.08.206.166.281.188.657.162.974a.544.544 0 01-.169.364zm-6.159 3.9c-.862.37-1.84.788-3.109.788a5.884 5.884 0 01-1.569-.217l.877 9.004c.065.78.717 1.38 1.5 1.38 0 0 1.243.065 1.658.065.447 0 1.786-.065 1.786-.065.783 0 1.434-.6 1.499-1.38l.94-9.95a3.996 3.996 0 00-1.322-.238c-.826 0-1.491.284-2.26.613z"/>
                        </svg>
                        <span>Coffee</span>
                    </a>
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
                    <button
                            onclick={handleMobileNewPosition}
                            class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 cursor-pointer"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                        </svg>
                        <span>New Position</span>
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
                            onclick={handleMobileNotifications}
                            class="w-full text-left text-gray-700 hover:bg-gray-100 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 cursor-pointer"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                        </svg>
                        <span>Notifications</span>
                    </button>
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
                    <a
                            href="https://buymeacoffee.com/shaisabm"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2"
                            onclick={() => mobileMenuOpen = false}
                    >
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M20.216 6.415l-.132-.666c-.119-.598-.388-1.163-1.001-1.379-.197-.069-.42-.098-.57-.241-.152-.143-.196-.366-.231-.572-.065-.378-.125-.756-.192-1.133-.057-.325-.102-.69-.25-.987-.195-.4-.597-.634-.996-.788a5.723 5.723 0 00-.626-.194c-1-.263-2.05-.36-3.077-.416a25.834 25.834 0 00-3.7.062c-.915.083-1.88.184-2.75.5-.318.116-.646.256-.888.501-.297.302-.393.77-.177 1.146.154.267.415.456.692.58.36.162.737.284 1.123.366 1.075.238 2.189.331 3.287.37 1.218.05 2.437.01 3.65-.118.299-.033.598-.073.896-.119.352-.054.578-.513.474-.834-.124-.383-.457-.531-.834-.473-.466.074-.96.108-1.382.146-1.177.08-2.358.082-3.536.006a22.228 22.228 0 01-1.157-.107c-.086-.01-.18-.025-.258-.036-.243-.036-.484-.08-.724-.13-.111-.027-.111-.185 0-.212h.005c.277-.06.557-.108.838-.147h.002c.131-.009.263-.032.394-.048a25.076 25.076 0 013.426-.12c.674.019 1.347.067 2.017.144l.228.031c.267.04.533.088.798.145.392.085.895.113 1.07.542.055.137.08.288.111.431l.319 1.484a.237.237 0 01-.199.284h-.003c-.037.006-.075.01-.112.015a36.704 36.704 0 01-4.743.295 37.059 37.059 0 01-4.699-.304c-.14-.017-.293-.042-.417-.06-.326-.048-.649-.108-.973-.161-.393-.065-.768-.032-1.123.161-.29.16-.527.404-.675.701-.154.316-.199.66-.267 1-.069.34-.176.707-.135 1.056.087.753.613 1.365 1.37 1.502a39.69 39.69 0 0011.343.376.483.483 0 01.535.53l-.071.697-1.018 9.907c-.041.41-.047.832-.125 1.237-.122.637-.553 1.028-1.182 1.171-.577.131-1.165.2-1.756.205-.656.004-1.31-.025-1.966-.022-.699.004-1.556-.06-2.095-.58-.475-.458-.54-1.174-.605-1.793l-.731-7.013-.322-3.094c-.037-.351-.286-.695-.678-.678-.336.015-.718.3-.678.679l.228 2.185.949 9.112c.147 1.344 1.174 2.068 2.446 2.272.742.12 1.503.144 2.257.156.966.016 1.942.053 2.892-.122 1.408-.258 2.465-1.198 2.616-2.657.34-3.332.683-6.663 1.024-9.995l.215-2.087a.484.484 0 01.39-.426c.402-.078.787-.212 1.074-.518.455-.488.546-1.124.385-1.766zm-1.478.772c-.145.137-.363.201-.578.233-2.416.359-4.866.54-7.308.46-1.748-.06-3.477-.254-5.207-.498-.17-.024-.353-.055-.47-.18-.22-.236-.111-.71-.054-.995.052-.26.152-.609.463-.646.484-.057 1.046.148 1.526.22.577.088 1.156.159 1.737.212 2.48.226 5.002.19 7.472-.14.45-.06.899-.13 1.345-.21.399-.072.84-.206 1.08.206.166.281.188.657.162.974a.544.544 0 01-.169.364zm-6.159 3.9c-.862.37-1.84.788-3.109.788a5.884 5.884 0 01-1.569-.217l.877 9.004c.065.78.717 1.38 1.5 1.38 0 0 1.243.065 1.658.065.447 0 1.786-.065 1.786-.065.783 0 1.434-.6 1.499-1.38l.94-9.95a3.996 3.996 0 00-1.322-.238c-.826 0-1.491.284-2.26.613z"/>
                        </svg>
                        <span>Buy Me a Coffee</span>
                    </a>
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

        {#if loading && !positions.length}
            <div class="flex justify-center items-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        {:else}
            {#if summary}
                <Summary {summary}/>
            {/if}

            <RoiSummary/>

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

    <!-- Feedback Modal -->
    <FeedbackModal bind:show={showFeedbackModal} onSuccess={handleFeedbackSuccess}/>
</div>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
    }
</style>
