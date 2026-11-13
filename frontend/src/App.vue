<template>
  <div class="min-h-screen bg-[#f5f5f7]">
    <!-- Authentifizierter Layout: Sidebar + Hauptbereich -->
    <div v-if="authStore.isAuthenticated" class="lg:flex"
    >
      <AppSidebar />
      <main class="flex-1 min-w-0 pt-16 lg:pt-0"
      >
        <router-view />
      </main>
    </div>

    <!-- Öffentliches Layout: Nur Router-Outlet -->
    <div v-else class="min-h-screen"
    >
      <router-view />
    </div>

    <!-- Globale Toast-Komponente -->
    <AppToast />
  </div>
</template>

<script setup lang="ts">
/**
 * App.vue — Root-Komponente mit Sidebar-Layout.
 *
 * Für authentifizierte Routen wird die Navigationssidebar angezeigt.
 * Öffentliche Routen (Landing, Login, Register) rendern weiterhin
 * das reine Router-Outlet ohne Sidebar.
 */
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/ui/AppToast.vue'

const authStore = useAuthStore()
</script>
