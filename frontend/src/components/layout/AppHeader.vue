<template>
  <nav class="navbar navbar-expand bg-light border-bottom px-3">
    <div class="navbar-nav gap-3">
      <RouterLink class="nav-link" :to="{ name: 'Main Page' }">Main</RouterLink>
      <RouterLink class="nav-link" :to="{ name: 'Other Page' }">Other</RouterLink>

      <div class="ms-auto">
        <template v-if="auth.isAuthenticated">
          <RouterLink class="nav-link" :to="{ name: 'Profile' }">{{ auth.user?.username }}</RouterLink>
          <button @click="auth.logout()" class="btn btn-outline-danger btn-sm">Logout</button>
        </template>
        <template v-else>
          <a href="/login/" class="btn btn-outline-primary btn-sm">Login</a>
          <a href="/signup/" class="btn btn-primary btn-sm ms-2">Sign Up</a>
        </template>
      </div>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { onMounted } from 'vue';

const auth = useAuthStore();

onMounted(() => {
  auth.checkAuth();
});
</script>