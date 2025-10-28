// API client for Django backend
const API_BASE_URL = 'http://localhost:8000/api';

// Create fetch with timeout
async function fetchWithTimeout(url, options = {}, timeout = 5000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('Request timeout - is Django server running?');
        }
        throw error;
    }
}

async function handleResponse(response) {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
    }
    return response.json();
}

export const api = {
    // Position CRUD operations
    async getPositions() {
        try {
            const response = await fetchWithTimeout(`${API_BASE_URL}/positions/`);
            return handleResponse(response);
        } catch (error) {
            console.error('Failed to fetch positions:', error);
            throw error;
        }
    },

    async getPosition(id) {
        const response = await fetch(`${API_BASE_URL}/positions/${id}/`);
        return handleResponse(response);
    },

    async createPosition(data) {
        const response = await fetch(`${API_BASE_URL}/positions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        return handleResponse(response);
    },

    async updatePosition(id, data) {
        const response = await fetch(`${API_BASE_URL}/positions/${id}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        return handleResponse(response);
    },

    async deletePosition(id) {
        const response = await fetch(`${API_BASE_URL}/positions/${id}/`, {
            method: 'DELETE',
        });
        if (response.status === 204) {
            return { success: true };
        }
        return handleResponse(response);
    },

    // Custom actions
    async getSummary() {
        try {
            const response = await fetchWithTimeout(`${API_BASE_URL}/positions/summary/`);
            return handleResponse(response);
        } catch (error) {
            console.error('Failed to fetch summary:', error);
            throw error;
        }
    },

    async getByStock(stock = null) {
        const url = stock
            ? `${API_BASE_URL}/positions/by_stock/?stock=${stock}`
            : `${API_BASE_URL}/positions/by_stock/`;
        const response = await fetch(url);
        return handleResponse(response);
    },

    async fetchCurrentPrice(id) {
        const response = await fetch(`${API_BASE_URL}/positions/${id}/fetch_current_price/`, {
            method: 'POST',
        });
        return handleResponse(response);
    },

    async fetchAllCurrentPrices() {
        const response = await fetch(`${API_BASE_URL}/positions/fetch_all_current_prices/`, {
            method: 'POST',
        });
        return handleResponse(response);
    },
};
