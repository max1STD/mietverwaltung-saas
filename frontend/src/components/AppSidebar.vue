<template>
  <!-- Mobile Header -->
  <div class="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white/90 backdrop-blur-md border-b border-gray-200 z-40 px-4 flex items-center justify-between">
    <div class="flex items-center gap-2">
      <div class="w-8 h-8 rounded-lg bg-[#0D3B70] flex items-center justify-center text-white font-bold text-sm">
        MV
      </div>
      <span class="font-semibold text-[#0D3B70]">MietVerwaltung</span>
    </div>
    <button
      type="button"
      class="p-2 rounded-lg text-gray-600 hover:bg-gray-100"
      aria-label="Menü öffnen"
      @click="mobileOpen = true"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
  </div>

  <!-- Desktop Sidebar -->
  <aside
    class="hidden lg:flex flex-col w-64 h-screen sticky top-0 bg-white border-r border-gray-200 z-30"
  >
    <SidebarContent @navigate="mobileOpen = false" />
  </aside>

  <!-- Mobile Drawer -->
  <Transition name="drawer">
    <div
      v-if="mobileOpen"
      class="lg:hidden fixed inset-0 z-50 flex"
    >
      <div class="absolute inset-0 bg-black/40" @click="mobileOpen = false" />
      <aside class="relative flex flex-col w-72 h-full bg-white shadow-xl">
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-[#0D3B70] flex items-center justify-center text-white font-bold text-sm">MV</div>
            <span class="font-semibold text-[#0D3B70]">MietVerwaltung</span>
          </div>
          <button
            type="button"
            class="p-2 rounded-lg text-gray-500 hover:bg-gray-100"
            aria-label="Menü schließen"
            @click="mobileOpen = false"
          >
            ✕
          </button>
        </div>
        <SidebarContent @navigate="mobileOpen = false" />
      </aside>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SidebarContent from './AppSidebarContent.vue'

const mobileOpen = ref(false)
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
</style>
