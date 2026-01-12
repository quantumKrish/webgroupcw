<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm">
    <div class="container-fluid px-4">
      <RouterLink class="navbar-brand fw-bold text-primary" :to="{ name: 'Main Page' }">
        <i class="bi bi-hammer"></i> Auction App
      </RouterLink>
      
      <div class="navbar-nav gap-2 flex-row align-items-center ms-auto">
        <RouterLink 
          class="nav-link px-3" 
          :class="{ 'active fw-semibold': $route.name === 'Main Page' }"
          :to="{ name: 'Main Page' }"
        >
          <i class="bi bi-house-door"></i> Home
        </RouterLink>
        <RouterLink 
          class="nav-link px-3" 
          :class="{ 'active fw-semibold': $route.name === 'Other Page' }"
          :to="{ name: 'Other Page' }"
        >
          <i class="bi bi-grid"></i> Browse
        </RouterLink>
        <RouterLink 
          class="nav-link px-3" 
          :class="{ 'active fw-semibold': $route.name === 'Items' }"
          :to="{ name: 'Items' }"
        >
          <i class="bi bi-collection"></i> Items
        </RouterLink>
        <RouterLink 
          class="nav-link px-3" 
          :class="{ 'active fw-semibold': $route.name === 'Create Item' }"
          :to="{ name: 'Create Item' }"
        >
          <i class="bi bi-plus-circle"></i> Post Item
        </RouterLink>

        <div class="vr mx-2" v-if="auth.isAuthenticated"></div>

        <template v-if="auth.isAuthenticated">
          <RouterLink 
            class="nav-link px-3 d-flex align-items-center" 
            :class="{ 'active fw-semibold': $route.name === 'Profile' }"
            :to="{ name: 'Profile' }"
          >
            <span class="avatar me-2" v-if="auth.user?.profile_image_url">
              <img :src="auth.user.profile_image_url" :alt="auth.user.username" />
            </span>
            <i v-else class="bi bi-person-circle me-1"></i> 
            <span>{{ auth.user?.username }}</span>
          </RouterLink>
          <button 
            @click="auth.logout()" 
            class="btn btn-outline-danger btn-sm ms-2"
          >
            <i class="bi bi-box-arrow-right"></i> Logout
          </button>
        </template>
        <template v-else>
          <a href="/login/" class="btn btn-outline-primary btn-sm">
            <i class="bi bi-box-arrow-in-right"></i> Login
          </a>
          <a href="/signup/" class="btn btn-primary btn-sm ms-2">
            <i class="bi bi-person-plus"></i> Sign Up
          </a>
        </template>
      </div>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { RouterLink, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { onMounted } from 'vue';

const auth = useAuthStore();
const $route = useRoute();

onMounted(() => {
  auth.checkAuth();
});
</script>

<style scoped>
.nav-link {
  transition: all 0.2s ease;
  border-radius: 0.25rem;
}

.nav-link:hover {
  background-color: rgba(13, 110, 253, 0.1);
}

.nav-link.active {
  color: #0d6efd !important;
  background-color: rgba(13, 110, 253, 0.1);
}

.navbar-brand {
  font-size: 1.25rem;
  transition: transform 0.2s ease;
}

.navbar-brand:hover {
  transform: scale(1.05);
}

.vr {
  height: 24px;
  opacity: 0.25;
}

.avatar {
  display: inline-flex;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  background: #f8fafc;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>