<template>
  <div class="h1">
    {{ title }}
  </div>
  <div class="input-group input-group-sm mb-3">
    <span class="input-group-text" id="inputGroup-sizing-sm">Search</span>
    <input type="text" class="form-control" aria-label="Auction search" aria-describedby="inputGroup-sizing-sm" placeholder="Search for items">
</div>
</template>

<script lang="ts">
    import { defineComponent } from "vue";
    import { useUiStore } from '../stores/ui';
    const ui = useUiStore();
    ui.toggleSidebar();

    export default defineComponent({
        data() {
            return {
                title: "Auction Website",
                input: "",
            }
        }
    })
</script>

<style scoped>
</style>
