<template>
  <div class="space-y-4">
    <div class="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-[#0D3B70] transition-colors cursor-pointer" @click="fileInput?.click()">
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="application/pdf,image/*,.doc,.docx,.txt"
        class="hidden"
        @change="onFilesSelected"
      />
      <p class="text-gray-500">Klicke hier, um Dokumente hochzuladen</p>
      <p class="text-xs text-gray-400 mt-1">PDF, Bilder, Word, Text — maximal 10 MB pro Datei</p>
    </div>

    <div v-if="store.error?.message" class="rounded-lg bg-red-50 border border-red-100 px-4 py-3 text-sm text-red-700">
      {{ store.error.message }}
    </div>

    <ul v-if="store.dokumente.length" class="divide-y divide-gray-200 border border-gray-200 rounded-xl bg-white">
      <li
        v-for="dokument in store.dokumente"
        :key="dokument.id"
        class="flex items-center justify-between px-4 py-3 text-sm"
      >
        <div class="flex items-center gap-3 min-w-0">
          <span class="text-gray-400">📄</span>
          <div class="min-w-0">
            <p class="font-medium text-gray-900 truncate">{{ dokument.titel || dokument.file_name }}</p>
            <p class="text-xs text-gray-500">{{ formatBytes(dokument.file_size) }} • {{ formatDate(dokument.created_at) }}</p>
            <p v-if="dokument.upload_error" class="text-xs text-red-600">{{ dokument.upload_error }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button
            v-if="supportsOcr(dokument)"
            type="button"
            class="text-[#0D3B70] hover:text-[#0D3B70]/80 font-medium"
            :disabled="ocrLoading[dokument.id]"
            @click="toggleOcr(dokument.id)"
          >
            {{ expandedOcr[dokument.id] ? 'OCR schließen' : 'OCR' }}
          </button>
          <a
            :href="store.downloadUrl(dokument.id)"
            target="_blank"
            class="text-[#0D3B70] hover:text-[#0D3B70]/80 font-medium"
          >Download</a>
          <button
            type="button"
            class="text-red-500 hover:text-red-700"
            :disabled="store.saving"
            @click="deleteDokument(dokument.id)"
          >
            Löschen
          </button>
        </div>
      </li>

      <!-- OCR-Text Panel -->
      <li
        v-for="dokument in ocrDocuments"
        :key="`ocr-${dokument.id}`"
        class="px-4 py-3 bg-gray-50 border-b border-gray-200"
      >
        <p class="text-xs font-medium text-gray-500 mb-1">
          OCR {{ dokument.ocr_status === 'done' ? '✓' : dokument.ocr_status || 'pending' }}
          <span v-if="dokument.ocr_confidence">· Confidence {{ Math.round(dokument.ocr_confidence) }}%</span>
        </p>
        <pre class="text-sm text-gray-700 whitespace-pre-wrap font-mono bg-white p-3 rounded border border-gray-200">{{ ocrResults[dokument.id]?.ocr_text || 'Kein Text erkannt.' }}</pre>
      </li>
    </ul>

    <p v-else class="text-sm text-gray-500">Noch keine Dokumente vorhanden.</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { useDokumenteStore, type DokumentTyp, type DokumentOcrResult } from '@/stores/dokumente'
import { useToast } from '@/composables/useToast'

const props = defineProps<{
  entityType: string
  entityId: number
  typ?: DokumentTyp
}>()

const store = useDokumenteStore()
const { showToast } = useToast()
const fileInput = ref<HTMLInputElement | null>(null)

const expandedOcr = reactive<Record<number, boolean>>({})
const ocrLoading = reactive<Record<number, boolean>>({})
const ocrResults = reactive<Record<number, DokumentOcrResult>>({})

const ocrDocuments = computed(() =>
  store.dokumente.filter((d) => expandedOcr[d.id] && supportsOcr(d)),
)

function supportsOcr(dokument: { content_type: string }): boolean {
  return dokument.content_type === 'application/pdf' || dokument.content_type.startsWith('image/')
}

async function toggleOcr(id: number): Promise<void> {
  if (expandedOcr[id]) {
    expandedOcr[id] = false
    return
  }
  expandedOcr[id] = true
  if (ocrResults[id]) return

  ocrLoading[id] = true
  const result = await store.fetchOcrText(id)
  ocrLoading[id] = false
  if (result) {
    ocrResults[id] = result
  } else {
    showToast('OCR konnte nicht geladen werden.', 'error')
  }
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('de-DE')
}

async function onFilesSelected(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement
  if (!target.files) return

  const files = Array.from(target.files)
  for (const file of files) {
    const created = await store.uploadDokument(
      props.entityType,
      props.entityId,
      file,
      file.name,
      props.typ,
    )
    if (created) {
      showToast(`"${file.name}" hochgeladen.`, 'success')
    } else {
      showToast(store.error?.message || `Fehler beim Hochladen von ${file.name}.`, 'error')
    }
  }
  target.value = ''
}

async function deleteDokument(id: number): Promise<void> {
  if (!confirm('Dokument wirklich löschen?')) return
  const ok = await store.deleteDokument(id)
  if (ok) {
    showToast('Dokument gelöscht.', 'success')
  } else {
    showToast(store.error?.message || 'Fehler beim Löschen.', 'error')
  }
}

onMounted(() => {
  store.fetchDokumente(props.entityType, props.entityId)
})
</script>
