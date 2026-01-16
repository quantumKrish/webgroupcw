<template>
  <div class="container mt-5">
    <div class="row">
      <div class="col-md-8 offset-md-2">
        <h2>Profile</h2>
        
        <div v-if="loading" class="alert alert-info">Loading...</div>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

        <form @submit.prevent="updateProfile" v-if="!loading">
          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input 
              type="text" 
              class="form-control" 
              id="username" 
              v-model="form.username"
              disabled
            >
          </div>

          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input 
              type="email" 
              class="form-control" 
              id="email" 
              v-model="form.email"
              required
            >
          </div>

          <div class="mb-3">
            <label for="first_name" class="form-label">First Name</label>
            <input 
              type="text" 
              class="form-control" 
              id="first_name" 
              v-model="form.first_name"
            >
          </div>

          <div class="mb-3">
            <label for="last_name" class="form-label">Last Name</label>
            <input 
              type="text" 
              class="form-control" 
              id="last_name" 
              v-model="form.last_name"
            >
          </div>

          <div class="mb-3">
            <label for="date_of_birth" class="form-label">Date of Birth</label>
            <input 
              type="date" 
              class="form-control" 
              id="date_of_birth" 
              v-model="form.date_of_birth"
            >
          </div>

          <div class="mb-3">
            <label class="form-label">Profile Image</label>
            <div
              class="dropzone"
              :class="{ 'dragover': isDragging, 'has-image': !!form.profile_image_preview }"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleDrop"
              @click="triggerFileInput"
            >
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                @change="handleImageUpload"
                style="display: none"
              />
              <div v-if="form.profile_image_preview" class="preview">
                <img :src="form.profile_image_preview" alt="Profile preview" />
                <button type="button" class="remove-btn" @click.stop="removeImage">✕ Remove</button>
              </div>
              <div v-else class="dropzone-content">
                <p><strong>Drag & drop</strong> an image here</p>
                <p class="muted">or click to browse</p>
              </div>
            </div>
          </div>

          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import type { ProfileForm } from '@/types';
import { useAuthStore } from '@/stores/auth';

const loading = ref(true);
const saving = ref(false);
const error = ref('');
const successMessage = ref('');
const auth = useAuthStore();

const isDragging = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

const form = ref<ProfileForm>({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  date_of_birth: '',
  profile_image: null,
  profile_image_preview: undefined,
});


// Helper function to get CSRF token from cookies
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

onMounted(async () => {
  await loadProfile();
});

// Load user profile data from API
// Fetches from /api/profile/
// Populates form fields
// Handles loading and error state
async function loadProfile() {
  try {
    loading.value = true;
    error.value = '';
    
    const response = await fetch('/api/profile/', {
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to load profile');
    }

    const data = await response.json();
    form.value = {
      username: data.username || '',
      email: data.email || '',
      first_name: data.first_name || '',
      last_name: data.last_name || '',
      date_of_birth: data.date_of_birth || '',
      profile_image_preview: data.profile_image_url || undefined,
    };
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'An error occurred';
  } finally {
    loading.value = false;
  }
}

// Handle profile image file upload
// Updates form.profile_image and form.profile_image_preview
// Called on file input change event
function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  
  if (files && files.length > 0) {
    const file = files[0];
    form.value.profile_image = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      form.value.profile_image_preview = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

function triggerFileInput() {
  fileInput.value?.click();
}

// Handle drag-and-drop file upload
// Updates form.profile_image and form.profile_image_preview
function handleDrop(event: DragEvent) {
  isDragging.value = false;
  const file = event.dataTransfer?.files?.[0];
  if (file && file.type.startsWith('image/')) {
    form.value.profile_image = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      form.value.profile_image_preview = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

// Remove selected profile image
function removeImage() {
  form.value.profile_image = null;
  form.value.profile_image_preview = undefined;
  if (fileInput.value) fileInput.value.value = '';
}

// Update user profile data via API
// Sends POST request to /api/profile/
// Includes form data and profile image if provided
// Handles saving, error, and success states
async function updateProfile() {
  try {
    saving.value = true;
    error.value = '';
    successMessage.value = '';

    const formData = new FormData();
    formData.append('email', form.value.email);
    formData.append('first_name', form.value.first_name);
    formData.append('last_name', form.value.last_name);
    formData.append('date_of_birth', form.value.date_of_birth);
    
    if (form.value.profile_image) {
      formData.append('profile_image', form.value.profile_image);
    }

    const csrfToken = getCookie('csrftoken');
    
    const response = await fetch('/api/profile/', {
      method: 'POST',
      credentials: 'include',
      headers: csrfToken ? {
        'X-CSRFToken': csrfToken,
      } : {},
      body: formData,
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to update profile');
    }

    const data = await response.json();
    form.value.profile_image_preview = data.profile_image_url || form.value.profile_image_preview;
    if (auth.user) {
      auth.user = {
        ...auth.user,
        profile_image_url: data.profile_image_url || null,
        email: data.email ?? auth.user.email,
        first_name: data.first_name ?? auth.user.first_name,
        last_name: data.last_name ?? auth.user.last_name,
      };
    }
    successMessage.value = 'Profile updated successfully!';
    
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'An error occurred';
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.container {
  max-width: 720px;
}

.dropzone {
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #f9fafb;
}

.dropzone:hover {
  border-color: #0d6efd;
  background: #eef2ff;
}

.dropzone.dragover {
  border-color: #0d6efd;
  background: #e0e7ff;
}

.dropzone.has-image {
  padding: 0.5rem;
  border: 2px solid #e5e7eb;
}

.dropzone-content {
  color: #6b7280;
}

.preview {
  position: relative;
}

.preview img {
  max-width: 100%;
  max-height: 240px;
  border-radius: 8px;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.4rem 0.75rem;
  background: rgba(220, 38, 38, 0.9);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.remove-btn:hover { background: #b91c1c; }
</style>