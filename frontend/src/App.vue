<template>
  <AppShell>
    <RouterView />
  </AppShell>
</template>

<script lang="ts" setup>
import { RouterView } from 'vue-router';
import AppShell from './components/layout/AppShell.vue';
</script>