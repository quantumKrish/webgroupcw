import { defineStore } from 'pinia';

export interface Item {
  id: number;
  owner: number;
  title: string;
  description: string;
  starting_price: string;
  current_price: string;
  image_url: string;
  ends_at: string;
  created_at: string;
  updated_at: string;
}

export interface Bid {
  id: number;
  item: number;
  bidder: number;
  amount: string;
  created_at: string;
}

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [] as Item[],
    currentItem: null as Item | null,
    bids: [] as Bid[],
    loading: false,
    error: null as string | null,
    searchQuery: '',
  }),
  
  getters: {
    filteredItems: (state) => {
      if (!state.searchQuery) return state.items;
      const query = state.searchQuery.toLowerCase();
      return state.items.filter(item => 
        item.title.toLowerCase().includes(query) || 
        item.description.toLowerCase().includes(query)
      );
    },
    
    getItemById: (state) => (id: number) => {
      return state.items.find(item => item.id === id);
    },
    
    getBidsForItem: (state) => (itemId: number) => {
      return state.bids.filter(bid => bid.item === itemId);
    },
  },
  
  actions: {
    async fetchItems() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await fetch('/api/items/', {
          credentials: 'include',
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch items');
        }
        
        this.items = await response.json();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An error occurred';
        console.error('Error fetching items:', err);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchItem(id: number) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await fetch(`/api/items/${id}/`, {
          credentials: 'include',
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch item');
        }
        
        this.currentItem = await response.json();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An error occurred';
        console.error('Error fetching item:', err);
      } finally {
        this.loading = false;
      }
    },
    
    async searchItems(query: string) {
      this.searchQuery = query;
      this.loading = true;
      this.error = null;
      
      try {
        const response = await fetch(`/api/items/search/?q=${encodeURIComponent(query)}`, {
          credentials: 'include',
        });
        
        if (!response.ok) {
          throw new Error('Failed to search items');
        }
        
        this.items = await response.json();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An error occurred';
        console.error('Error searching items:', err);
      } finally {
        this.loading = false;
      }
    },
    
    async placeBid(itemId: number, amount: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const csrfToken = this.getCookie('csrftoken');
        
        const response = await fetch('/api/bids/', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
          },
          body: JSON.stringify({
            item: itemId,
            amount: amount,
          }),
        });
        
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || 'Failed to place bid');
        }
        
        const newBid = await response.json();
        this.bids.push(newBid);
        
        // Refresh the item to get updated price
        await this.fetchItem(itemId);
        
        return newBid;
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An error occurred';
        console.error('Error placing bid:', err);
        throw err;
      } finally {
        this.loading = false;
      }
    },
    
    async fetchBidsForItem(itemId: number) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await fetch(`/api/items/${itemId}/bids/`, {
          credentials: 'include',
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch bids');
        }
        
        this.bids = await response.json();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An error occurred';
        console.error('Error fetching bids:', err);
      } finally {
        this.loading = false;
      }
    },
    
    getCookie(name: string): string | null {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
      return null;
    },
  },
});