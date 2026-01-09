import { defineStore } from 'pinia';

interface User {
  id: number;
  username: string;
  email: string;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    isAuthenticated: false,
  }),
  
  actions: {
    async checkAuth() {
      try {
        const response = await fetch('/api/user/', { credentials: 'include' });
        const contentType = response.headers.get('content-type') || '';

        if (!response.ok || !contentType.includes('application/json')) {
          this.user = null;
          this.isAuthenticated = false;
          return;
        }

        const data = await response.json();
        if (data && data.authenticated !== false) {
          this.user = data;
          this.isAuthenticated = true;
        } else {
          this.user = null;
          this.isAuthenticated = false;
        }
      } catch {
        this.user = null;
        this.isAuthenticated = false;
      }
    },
    
    logout() {
      this.user = null;
      this.isAuthenticated = false;
      window.location.href = `/logout/`;
    },
  },
});