<template>
  <!-- Root: Router-Outlet + globale Toast-Komponente -->
  <router-view />
  <AppToast />
</template>

<script setup lang="ts">
/**
 * App.vue — Root-Komponente
 * Enthält das Router-Outlet und die globale Toast-Komponente.
 */
import AppToast from '@/components/ui/AppToast.vue'
</script>