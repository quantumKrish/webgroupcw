<template>
  <div class="min-vh-100 d-flex flex-column">
    <AppHeader />
    <main class="container pt-4 flex-grow-1">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script lang="ts" setup>
import AppHeader from './AppHeader.vue';
import AppFooter from './AppFooter.vue';
</script>