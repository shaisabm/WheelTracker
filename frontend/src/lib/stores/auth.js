import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';

function createAuthStore() {
	const { subscribe, set, update } = writable({
		isAuthenticated: false,
		accessToken: null,
		refreshToken: null,
	});

	return {
		subscribe,

		init: () => {
			if (browser) {
				const accessToken = localStorage.getItem('access_token');
				const refreshToken = localStorage.getItem('refresh_token');

				if (accessToken && refreshToken) {
					set({
						isAuthenticated: true,
						accessToken,
						refreshToken,
					});
				}
			}
		},

		login: (accessToken, refreshToken) => {
			if (browser) {
				localStorage.setItem('access_token', accessToken);
				localStorage.setItem('refresh_token', refreshToken);
			}
			set({
				isAuthenticated: true,
				accessToken,
				refreshToken,
			});
		},

		logout: () => {
			if (browser) {
				localStorage.removeItem('access_token');
				localStorage.removeItem('refresh_token');
			}
			set({
				isAuthenticated: false,
				accessToken: null,
				refreshToken: null,
			});
			goto('/login');
		},

		refreshAccessToken: async () => {
			if (!browser) return false;

			const refreshToken = localStorage.getItem('refresh_token');
			if (!refreshToken) return false;

			try {
				const response = await fetch('http://localhost:8000/api/auth/refresh/', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({ refresh: refreshToken }),
				});

				if (!response.ok) {
					throw new Error('Token refresh failed');
				}

				const data = await response.json();

				if (browser) {
					localStorage.setItem('access_token', data.access);
				}

				update(state => ({
					...state,
					accessToken: data.access,
				}));

				return true;
			} catch (error) {
				console.error('Failed to refresh token:', error);
				// Logout on refresh failure
				if (browser) {
					localStorage.removeItem('access_token');
					localStorage.removeItem('refresh_token');
				}
				set({
					isAuthenticated: false,
					accessToken: null,
					refreshToken: null,
				});
				goto('/login');
				return false;
			}
		},
	};
}

export const auth = createAuthStore();
