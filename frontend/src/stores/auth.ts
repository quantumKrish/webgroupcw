import { defineStore } from 'pinia';

interface User {
  id: number;
  username: string;
  email: string;
}

const apiUrl = import.meta.env.VITE_API_URL || '';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    isAuthenticated: false,
  }),
  
  actions: {
    async checkAuth() {
      try {
        const response = await fetch(`${apiUrl}/api/user/`, {
          credentials: 'include',
        });
        if (response.ok) {
          this.user = await response.json();
          this.isAuthenticated = true;
        }
      } catch (error) {
        this.isAuthenticated = false;
      }
    },
    
    logout() {
      this.user = null;
      this.isAuthenticated = false;
      window.location.href = `${apiUrl}/logout/`;
    },
  },
});