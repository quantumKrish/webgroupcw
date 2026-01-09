<template>
  <div class="d-flex justify-content-center align-items-center" :style="{ minHeight: height }">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <span v-if="message" class="ms-3 text-muted">{{ message }}</span>
  </div>
</template>

<script lang="ts" setup>
defineProps<{
  height?: string;
  message?: string;
}>();
</script>