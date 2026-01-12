<template>
  <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
    <i class="bi bi-exclamation-triangle-fill me-2"></i>
    <strong>Error:</strong> {{ error }}
    <button 
      type="button" 
      class="btn-close" 
      @click="$emit('close')"
      aria-label="Close"
    ></button>
  </div>
</template>

<script lang="ts" setup>
defineProps<{
  error: string;
}>();

defineEmits<{
  close: [];
}>();
</script>