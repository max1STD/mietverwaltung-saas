<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
    <AppCard
      v-for="objekt in objekteStore.objekte"
      :key="objekt.id"
      padding="none"
      shadow="md"
      hover
      @click="$router.push(`/objekte/${objekt.public_id || objekt.id}`)"
    >
      <div class="relative h-32 bg-gray-100 rounded-t-xl overflow-hidden">
        <img
          v-if="objekt.foto_url"
          :src="objekt.foto_url"
          alt="Objektfoto"
          class="w-full h-full object-cover"
        />
        <div
          v-else
          class="w-full h-full flex items-center justify-center text-4xl"
        >
          🏠
        </div>
        <button
          type="button"
          class="absolute bottom-2 right-2 bg-white/90 hover:bg-white text-[#0D3B70] rounded-full p-2 shadow-sm transition-colors"
          title="Foto hochladen"
          @click.stop="startUpload(objekt)"
        >
          📷
        </button>
      </div>

      <div class="p-5">
        <h3 class="font-semibold text-[#0D3B70] truncate">{{ objekt.name }}</h3>
        <p class="text-sm text-gray-500 truncate">{{ objekt.address || 'Keine Adresse' }}</p>

        <div class="mt-4">
          <div class="flex justify-between text-sm mb-1">
            <span class="text-gray-600">Vermietungsquote</span>
            <span class="font-medium text-[#0D3B70]">
              {{ summaryFor(objekt.id)?.einheiten_vermietet ?? 0 }} /
              {{ summaryFor(objekt.id)?.einheiten_total ?? 0 }} WE
              <span v-if="summaryFor(objekt.id)" class="ml-1">({{ formatPercent(summaryFor(objekt.id)?.vermietungsquote) }})</span>
            </span>
          </div>
          <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              class="h-full transition-all duration-500"
              :class="progressColor(summaryFor(objekt.id)?.vermietungsquote ?? 0)"
              :style="{ width: `${summaryFor(objekt.id)?.vermietungsquote ?? 0}%` }"
            />
          </div>
        </div>

        <div
          v-if="summaryFor(objekt.id)?.bruttomietrendite != null"
          class="mt-3 flex items-center justify-between text-sm"
        >
          <span class="text-gray-500">Bruttomietrendite</span>
          <span class="font-medium text-gray-900">{{ formatPercent(summaryFor(objekt.id)?.bruttomietrendite) }}</span>
        </div>
      </div>
    </AppCard>

    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      class="hidden"
      @change="onFileSelected"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useObjekteStore } from '@/stores/objekte'
import { useDashboardStore, type DashboardObjectSummary } from '@/stores/dashboard'
import AppCard from '@/components/ui/AppCard.vue'

interface Props {
  summaries?: Record<number, DashboardObjectSummary>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'upload', objektId: string | number, file: File): void
}>()

const objekteStore = useObjekteStore()
const dashboardStore = useDashboardStore()
const fileInput = ref<HTMLInputElement | null>(null)
const selectedObjekt = ref<{ id: string } | null>(null)

function summaryFor(objektId: string | number): DashboardObjectSummary | undefined {
  return props.summaries?.[Number(objektId)] ?? dashboardStore.objectSummaries[Number(objektId)]
}

function formatPercent(value: number | null | undefined): string {
  if (value === undefined || value === null) return '–'
  return `${value.toLocaleString('de-DE', { maximumFractionDigits: 1 })}%`
}

function progressColor(quote: number): string {
  if (quote >= 100) return 'bg-green-500'
  if (quote >= 75) return 'bg-[#0D3B70]'
  if (quote >= 50) return 'bg-yellow-500'
  return 'bg-red-500'
}

function startUpload(objekt: { id: string }): void {
  selectedObjekt.value = objekt
  fileInput.value?.click()
}

function onFileSelected(event: Event): void {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file && selectedObjekt.value) {
    emit('upload', selectedObjekt.value.id, file)
  }
  if (target) {
    target.value = ''
  }
}
</script>
