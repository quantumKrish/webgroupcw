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
            <label for="profile_image" class="form-label">Profile Image</label>
            <input 
              type="file" 
              class="form-control" 
              id="profile_image" 
              @change="handleImageUpload"
              accept="image/*"
            >
            <div v-if="form.profile_image_preview" class="mt-2">
              <img :src="form.profile_image_preview" alt="Profile preview" style="max-width: 200px;">
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

interface ProfileForm {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  profile_image?: File | null;
  profile_image_preview?: string;
}

const loading = ref(true);
const saving = ref(false);
const error = ref('');
const successMessage = ref('');

const form = ref<ProfileForm>({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  date_of_birth: '',
  profile_image: null,
  profile_image_preview: undefined,
});

onMounted(async () => {
  await loadProfile();
});

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

// Add this helper function at the top of the script
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

// Then update the updateProfile function to include CSRF token:
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
      method: 'PUT',
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