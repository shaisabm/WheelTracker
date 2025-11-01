// API client for Django backend
import { browser } from '$app/environment';
import { goto } from '$app/navigation';

const API_BASE_URL = 'http://localhost:8000/api';

// Get auth headers
function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (browser) {
        const token = localStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

    return headers;
}

// Create fetch with timeout
async function fetchWithTimeout(url, options = {}, timeout = 5000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    // Add auth headers
    const authHeaders = getAuthHeaders();
    const mergedOptions = {
        ...options,
        headers: {
            ...authHeaders,
            ...options.headers,
        },
        signal: controller.signal
    };

    try {
        const response = await fetch(url, mergedOptions);
        clearTimeout(timeoutId);

        // Handle 401 Unauthorized - redirect to login
        if (response.status === 401) {
            if (browser) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                goto('/login');
            }
        }

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
        console.error('API Error Response:', error);
        // If error is an object with field-specific errors, format them nicely
        if (typeof error === 'object' && !error.error) {
            const errorMessages = Object.entries(error)
                .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
                .join('\n');
            throw new Error(errorMessages || `HTTP error! status: ${response.status}`);
        }
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
        const response = await fetchWithTimeout(`${API_BASE_URL}/positions/`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
        return handleResponse(response);
    },

    async updatePosition(id, data) {
        const response = await fetchWithTimeout(`${API_BASE_URL}/positions/${id}/`, {
            method: 'PUT',
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

    async getRoiSummary(startDate = '', endDate = '') {
        try {
            let url = `${API_BASE_URL}/positions/roi_summary/`;
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const queryString = params.toString();
            if (queryString) {
                url += `?${queryString}`;
            }

            const response = await fetchWithTimeout(url);
            return handleResponse(response);
        } catch (error) {
            console.error('Failed to fetch ROI summary:', error);
            throw error;
        }
    },
};
