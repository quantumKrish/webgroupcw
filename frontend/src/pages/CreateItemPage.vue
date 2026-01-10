<template>
  <div class="create-item-page">
    <h1>Post New Auction Item</h1>

    <form @submit.prevent="submitItem" class="item-form">
      <!-- Title -->
      <div class="form-group">
        <label for="title">Title *</label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          required
          placeholder="Enter item title"
        />
      </div>

      <!-- Description -->
      <div class="form-group">
        <label for="description">Description *</label>
        <textarea
          id="description"
          v-model="form.description"
          required
          rows="4"
          placeholder="Describe your item"
        ></textarea>
      </div>

      <!-- Starting Price -->
      <div class="form-group">
        <label for="starting_price">Starting Price ($) *</label>
        <input
          id="starting_price"
          v-model="form.starting_price"
          type="number"
          step="0.01"
          min="0"
          required
          placeholder="0.00"
        />
      </div>

      <!-- Image URL -->
      <div class="form-group">
        <label for="image_url">Image URL</label>
        <input
          id="image_url"
          v-model="form.image_url"
          type="url"
          placeholder="https://example.com/image.jpg"
        />
      </div>

      <!-- End Date/Time -->
      <div class="form-group">
        <label for="ends_at">Auction End Date/Time *</label>
        <input
          id="ends_at"
          v-model="form.ends_at"
          type="datetime-local"
          required
        />
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <!-- Success Message -->
      <div v-if="success" class="success-message">
        Item posted successfully!
      </div>

      <!-- Submit Button -->
      <div class="form-actions">
        <button type="submit" :disabled="submitting" class="submit-btn">
          {{ submitting ? 'Posting...' : 'Post Item' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'CreateItemPage',
  
  data() {
    return {
      form: {
        title: '',
        description: '',
        starting_price: '',
        image_url: '',
        ends_at: '',
      },
      submitting: false,
      error: '',
      success: false,
    };
  },

  methods: {
    async submitItem() {
      this.submitting = true;
      this.error = '';
      this.success = false;

      try {
        const response = await fetch('/api/items/create/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: this.form.title,
            description: this.form.description,
            starting_price: this.form.starting_price,
            image_url: this.form.image_url,
            ends_at: this.form.ends_at,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to create item');
        }

        const data = await response.json();
        console.log('Item created:', data);
        
        this.success = true;
        
        // Reset form
        this.form = {
          title: '',
          description: '',
          starting_price: '',
          image_url: '',
          ends_at: '',
        };

        // Optional: redirect after a delay
        setTimeout(() => {
          // TODO: Use Vue Router to navigate to item list page
          // this.$router.push('/items');
        }, 2000);

      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to post item';
        console.error('Error creating item:', err);
      } finally {
        this.submitting = false;
      }
    },
  },
});
</script>

<style scoped>
.create-item-page {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  margin-bottom: 1.5rem;
  color: #333;
}

.item-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4CAF50;
}

.error-message {
  padding: 1rem;
  margin-bottom: 1rem;
  background: #ffebee;
  color: #c62828;
  border-radius: 4px;
  border-left: 4px solid #c62828;
}

.success-message {
  padding: 1rem;
  margin-bottom: 1rem;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  border-left: 4px solid #2e7d32;
}

.form-actions {
  margin-top: 2rem;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #45a049;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
