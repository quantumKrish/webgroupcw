<template>
  <div class="item-list-page">
    <h1>Auction Items</h1>
    
    <!-- Search bar -->
    <div class="search-box">
      <input 
        v-model="searchQuery" 
        @input="onSearchInput"
        type="text" 
        placeholder="Search items by title or description..."
        class="search-input"
      />
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">Loading items...</div>

    <!-- Error state -->
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Items grid -->
    <div v-if="!loading && !error" class="items-grid">
      <div 
        v-for="item in items" 
        :key="item.id" 
        class="item-card"
      >
        <div v-if="item.image_url" class="item-image">
          <img :src="item.image_url" :alt="item.title" />
        </div>
        <div class="item-details">
          <h3>{{ item.title }}</h3>
          <p class="item-description">{{ item.description }}</p>
          <div class="item-meta">
            <span class="price">Current: ${{ item.current_price }}</span>
            <span class="ends">Ends: {{ formatDate(item.ends_at) }}</span>
          </div>
        </div>
      </div>
      
      <div v-if="items.length === 0" class="no-items">
        No items found{{ searchQuery ? ' matching your search' : '' }}.
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { Item } from '../types';

export default defineComponent({
  name: 'ItemListPage',
  
  data() {
    return {
      items: [] as Item[],
      searchQuery: '',
      loading: false,
      error: '',
      searchTimeout: null as number | null,
    };
  },

  mounted() {
    this.fetchItems();
  },

  methods: {
    async fetchItems(search = '') {
      this.loading = true;
      this.error = '';
      
      try {
        const url = search 
          ? `/api/items/?search=${encodeURIComponent(search)}`
          : '/api/items/';
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch items: ${response.statusText}`);
        }
        
        const data = await response.json();
        this.items = data.items || [];
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to load items';
        console.error('Error fetching items:', err);
      } finally {
        this.loading = false;
      }
    },

    onSearchInput() {
      // Debounce search to avoid excessive API calls
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      
      this.searchTimeout = window.setTimeout(() => {
        this.fetchItems(this.searchQuery);
      }, 300);
    },

    formatDate(isoString: string): string {
      const date = new Date(isoString);
      return date.toLocaleString();
    },
  },
});
</script>

<style scoped>
.item-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  margin-bottom: 1.5rem;
  color: #333;
}

.search-box {
  margin-bottom: 2rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.loading, .error, .no-items {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
}

.error {
  color: #d32f2f;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.item-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.item-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.item-image {
  width: 100%;
  height: 200px;
  background: #f5f5f5;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  padding: 1rem;
}

.item-details h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  color: #333;
}

.item-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.price {
  font-weight: bold;
  color: #4CAF50;
}

.ends {
  color: #999;
  font-size: 0.85rem;
}
</style>
