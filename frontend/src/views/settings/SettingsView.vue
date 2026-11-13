<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70] mb-6">Einstellungen</h1>

      <AppCard padding="md" shadow="md"
      >
        <AppEmptyState
          icon="⚙️"
          title="Einstellungen"
          description="Hier werden bald Kontoeinstellungen, Benachrichtigungen und Abo-Details verwaltet."
        />
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppCard from '@/components/ui/AppCard.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
</script>
