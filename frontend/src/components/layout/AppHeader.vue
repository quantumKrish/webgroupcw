<template>
  <nav class="navbar navbar-expand bg-light border-bottom px-3">
    <div class="navbar-nav gap-3">
      <RouterLink class="nav-link" :to="{ name: 'Main Page' }">Main</RouterLink>
      <RouterLink class="nav-link" :to="{ name: 'Other Page' }">Other</RouterLink>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { RouterLink } from 'vue-router';
</script>