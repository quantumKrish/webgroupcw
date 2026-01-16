<template>
  <div class="create-item-page">
    <h1 v-if="isEditMode">Edit Auction Item</h1>
    <h1 v-else>Post New Auction Item</h1>

    <div v-if="!isLoggedIn" class="placeholder">
      <p class="muted"><a href="/login/">Log in</a> to post an auction item</p>
    </div>

    <form v-else @submit.prevent="submitItem" class="item-form">
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
        <label for="starting_price">
          <span v-if="isEditMode">Starting Price (Fixed)</span>
          <span v-else>Starting Price ($) *</span>
        </label>
        <input
          id="starting_price"
          v-model="form.starting_price"
          type="number"
          step="0.01"
          min="0"
          :readonly="isEditMode"
          :required="!isEditMode"
          placeholder="0.00"
        />
        <p v-if="isEditMode" class="field-info">Current highest bid: ${{ currentPrice }}</p>
      </div>

      <!-- Image Upload Drag & Drop -->
      <div class="form-group">
        <label>
          <span v-if="isEditMode">Item Image (Leave blank to keep current)</span>
          <span v-else>Item Image *</span>
        </label>
        <div
          class="dropzone"
          :class="{ 'dragover': isDragging, 'has-image': imagePreview }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            @change="handleFileSelect"
            style="display: none"
          />
          <div v-if="imagePreview" class="preview">
            <img :src="imagePreview" alt="Preview" />
            <button type="button" class="remove-btn" @click.stop="removeImage">
              ✕ Remove
            </button>
          </div>
          <div v-else class="dropzone-content">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16" >
              <path d="M6.002 5.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
              <path d="M2.002 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2h-12zm12 1a1 1 0 0 1 1 1v6.5l-3.777-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062L1.002 12V3a1 1 0 0 1 1-1h12z"/>
            </svg>
            <p><strong>Drag & drop</strong> an image here</p>
            <p class="muted">or click to browse</p>
          </div>
        </div>
      </div>

      <!-- Additional Images -->
      <div class="form-group">
        <label>Additional Images</label>
        <input
          type="file"
          accept="image/*"
          multiple
          @change="handleExtraSelect"
        />
        <div v-if="extraPreviews.length" class="extra-grid">
          <div v-for="(preview, idx) in extraPreviews" :key="preview" class="extra-thumb">
            <img :src="preview" alt="Additional preview" />
            <button type="button" class="remove-btn" @click="removeExtra(idx)">✕</button>
          </div>
        </div>
      </div>

      <!-- End Date/Time -->
      <div class="form-group">
        <label for="ends_at">Auction End Date/Time *</label>
        <input
          id="ends_at"
          v-model="form.ends_at"
          type="datetime-local"
          :readonly="isEditMode"
          :required="!isEditMode"
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
        <button type="submit" :disabled="submitting || (!isEditMode && !form.image)" class="submit-btn">
          {{ submitting ? (isEditMode ? 'Updating...' : 'Posting...') : (isEditMode ? 'Update Item' : 'Post Item') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';
import { useRoute } from 'vue-router';

export default defineComponent({
  name: 'CreateItemPage',
  
  setup() {
    const auth = useAuthStore();
    const route = useRoute();
    const isLoggedIn = computed(() => auth.isAuthenticated);
    return { isLoggedIn, route };
  },

  data() {
    return {
      form: {
        title: '',
        description: '',
        starting_price: '',
        image: null as File | null,
        extra_images: [] as File[],
        ends_at: '',
      },
      imagePreview: '',
      extraPreviews: [] as string[],
      isDragging: false,
      submitting: false,
      error: '',
      success: false,
      loading: false,
      currentPrice: '0.00',
      existingImageUrl: '',
      isEditMode: false,
    };
  },

  watch: {
    'route.params.id': {
      handler(newId) {
        this.isEditMode = !!newId;
      },
      immediate: true,
    },
  },

  async mounted() {
    if (this.isEditMode) {
      await this.loadItemData();
    }
  },

  methods: {
    // Fetches existing item data for editing
    // After making API request, populates form fields
    // Handles errors and loading state
    async loadItemData() {
      this.loading = true;
      this.error = '';
      try {
        const response = await fetch(`/api/items/${this.route.params.id}/`);
        if (!response.ok) throw new Error('Failed to load item');
        const data = await response.json();
        
        this.form.title = data.title;
        this.form.description = data.description;
        this.form.starting_price = data.starting_price;
        this.form.ends_at = data.ends_at.slice(0, 16); // Convert to datetime-local format
        this.currentPrice = data.current_price;
        this.existingImageUrl = data.image_url;
        this.imagePreview = data.image_url;
        
        // Load extra images if available
        if (data.images && data.images.length > 1) {
          this.extraPreviews = data.images.slice(1);
        }
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to load item';
      } finally {
        this.loading = false;
      }
    },

    // Triggers the hidden file input for image selection
    triggerFileInput() {
      (this.$refs.fileInput as HTMLInputElement).click();
    },

    // Handles file selection from the file input
    handleFileSelect(event: Event) {
      const target = event.target as HTMLInputElement;
      const file = target.files?.[0];
      if (file) {
        this.setImage(file);
      }
    },

    // Handles file drop in the drag-and-drop area
    // Sets the dropped image as the main image
    handleDrop(event: DragEvent) {
      this.isDragging = false;
      const file = event.dataTransfer?.files[0];
      if (file && file.type.startsWith('image/')) {
        this.setImage(file);
      } else {
        this.error = 'Please drop an image file';
      }
    },

    // Sets the main image and generates a preview
    setImage(file: File) {
      this.form.image = file;
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imagePreview = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    },

    // Removes the selected main image
    removeImage() {
      this.form.image = null;
      this.imagePreview = '';
      (this.$refs.fileInput as HTMLInputElement).value = '';
    },

    // Handles selection of additional images
    handleExtraSelect(event: Event) {
      const target = event.target as HTMLInputElement;
      const files = Array.from(target.files || []);
      files.forEach((file) => {
        if (file.type.startsWith('image/')) {
          this.form.extra_images.push(file);
          const reader = new FileReader();
          reader.onload = (e) => this.extraPreviews.push(e.target?.result as string);
          reader.readAsDataURL(file);
        }
      });
      (this.$refs.fileInput as HTMLInputElement).value = '';
    },

    // Removes an additional image by index
    removeExtra(idx: number) {
      this.form.extra_images.splice(idx, 1);
      this.extraPreviews.splice(idx, 1);
    },

    // Submits the form data to create or update an item
    // Handles success and error states
    async submitItem() {
      if (!this.isEditMode && !this.form.image) {
        this.error = 'Please select an image';
        return;
      }

      this.submitting = true;
      this.error = '';
      this.success = false;

      try {
        const formData = new FormData();
        formData.append('title', this.form.title);
        formData.append('description', this.form.description);
        formData.append('starting_price', this.form.starting_price);
        formData.append('ends_at', this.form.ends_at);
        if (this.form.image) {
          formData.append('image', this.form.image);
        }
        this.form.extra_images.forEach((img) => formData.append('extra_images', img));

        const endpoint = this.isEditMode 
          ? `/api/items/${this.route.params.id}/update/`
          : '/api/items/create/';

        const response = await fetch(endpoint, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `Failed to ${this.isEditMode ? 'update' : 'create'} item`);
        }

        const data = await response.json();
        console.log('Item saved:', data);
        
        this.success = true;
        
        // Reset form if creating new
        if (!this.isEditMode) {
          this.form = {
            title: '',
            description: '',
            starting_price: '',
            image: null,
            extra_images: [],
            ends_at: '',
          };
          this.imagePreview = '';
          this.extraPreviews = [];
        }

        // Redirect after a delay
        setTimeout(() => {
          this.$router.push(`/items/${data.id}/`);
        }, 1500);

      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to ${this.isEditMode ? 'update' : 'post'} item`;
        console.error('Error saving item:', err);
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

.placeholder {
  padding: 2rem;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  text-align: center;
}

.placeholder p {
  color: #6b7280;
  font-size: 0.95rem;
  margin: 0;
}

.placeholder a {
  color: #0d6efd;
  text-decoration: none;
  font-weight: 600;
}

.placeholder a:hover {
  text-decoration: underline;
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

.form-group input:disabled,
.form-group textarea:disabled,
.form-group input:read-only,
.form-group textarea:read-only {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.field-info {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
  margin-bottom: 0;
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

.dropzone {
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #f9fafb;
}

.dropzone:hover {
  border-color: #4CAF50;
  background: #f0fdf4;
}

.dropzone.dragover {
  border-color: #4CAF50;
  background: #dcfce7;
}

.dropzone.has-image {
  padding: 0;
  border: 2px solid #e5e7eb;
}

.dropzone-content {
  color: #6b7280;
}

.dropzone-content svg {
  color: #9ca3af;
  margin: 0 auto 1rem;
}

.dropzone-content p {
  margin: 0.5rem 0;
}

.dropzone-content .muted {
  font-size: 0.875rem;
  color: #9ca3af;
}

.preview {
  position: relative;
}

.preview img {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 6px;
}

.remove-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(220, 38, 38, 0.9);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.remove-btn:hover {
  background: #dc2626;
}

.extra-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.extra-thumb {
  position: relative;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.extra-thumb img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}

.extra-thumb .remove-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  margin-top: 0;
  padding: 0.25rem 0.45rem;
  font-size: 0.85rem;
}
</style>
