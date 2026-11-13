<template>
  <div class="flex flex-col h-full">
    <!-- Logo (nur Desktop, da Mobile im Drawer-Header) -->
    <div class="hidden lg:flex items-center gap-2 px-6 py-5 border-b border-gray-100">
      <div class="w-8 h-8 rounded-lg bg-[#0D3B70] flex items-center justify-center text-white font-bold text-sm">MV</div>
      <span class="font-semibold text-[#0D3B70]">MietVerwaltung</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-1">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
        :class="route.path.startsWith(item.to)
          ? 'bg-[#0D3B70] text-white'
          : 'text-gray-600 hover:bg-gray-100 hover:text-[#0D3B70]'"
        @click="emit('navigate')"
      >
        <span class="text-lg">{{ item.icon }}</span>
        {{ item.label }}
      </RouterLink>
    </nav>

    <!-- Footer: Benutzer + Logout -->
    <div class="border-t border-gray-100 p-4">
      <div class="flex items-center gap-3 mb-3">
        <div class="w-9 h-9 rounded-full bg-[#0D3B70]/10 flex items-center justify-center text-[#0D3B70] font-semibold text-sm">
          {{ initials }}
        </div>
        <div class="min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">{{ authStore.user?.full_name || 'Benutzer' }}</p>
          <p class="text-xs text-gray-500 truncate">{{ authStore.user?.email }}</p>
        </div>
      </div>

      <AppButton
        variant="ghost"
        size="sm"
        full-width
        @click="handleLogout"
      >
        Abmelden
      </AppButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppButton from '@/components/ui/AppButton.vue'

interface NavItem {
  to: string
  label: string
  icon: string
}

const emit = defineEmits<{
  (e: 'navigate'): void
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const navItems: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/objekte', label: 'Objekte', icon: '🏠' },
  { to: '/mieter', label: 'Mieter', icon: '👤' },
  { to: '/mietvertraege', label: 'Mietverträge', icon: '📄' },
  { to: '/tickets', label: 'Tickets', icon: '🎫' },
  { to: '/einstellungen', label: 'Einstellungen', icon: '⚙️' },
]

const initials = computed(() => {
  const name = authStore.user?.full_name || authStore.user?.email || 'U'
  return name
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})

async function handleLogout(): Promise<void> {
  await authStore.logout()
  await router.push({ name: 'login' })
  emit('navigate')
}
</script>
