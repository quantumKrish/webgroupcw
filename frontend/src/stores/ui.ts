import { defineStore } from 'pinia';

export const useUiStore = defineStore('ui', {
  state: () => ({
    sidebarOpen: false,
    theme: 'light',
  }),
  actions: {
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },
    setTheme(next: 'light' | 'dark') {
      this.theme = next;
    },
  },
});