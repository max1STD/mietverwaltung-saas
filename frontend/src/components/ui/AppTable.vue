<template>
  <div class="overflow-x-auto -mx-6">
    <table class="w-full text-left border-collapse">
      <thead>
        <tr class="border-b border-gray-200">
          <th
            v-for="column in columns"
            :key="String(column.key)"
            class="py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer select-none hover:text-[#0D3B70] transition-colors"
            @click="sortBy(column.key)"
          >
            {{ column.label }}
            <span v-if="sortKey === column.key" class="ml-1">
              {{ sortOrder === 'asc' ? '↑' : '↓' }}
            </span>
          </th>
          <th
            v-if="$slots.actions"
            class="py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right"
          >
            Aktionen
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr
          v-for="item in sortedItems"
          :key="String(item[idKey])"
          class="hover:bg-gray-50/50 transition-colors"
        >
          <slot name="row" :item="item" />
          <td v-if="$slots.actions" class="py-3 px-4 text-right">
            <slot name="actions" :item="item" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts" generic="T extends object">
import { ref, computed } from 'vue'

export interface TableColumn<TItem> {
  key: keyof TItem | string
  label: string
}

const props = withDefaults(
  defineProps<{
    items: T[]
    columns: TableColumn<T>[]
    idKey?: keyof T
    initialSort?: keyof T | string
  }>(),
  {
    idKey: 'id' as keyof T,
  },
)

const sortKey = ref<keyof T | string | null>(props.initialSort ?? null)
const sortOrder = ref<'asc' | 'desc'>('asc')

function sortBy(key: keyof T | string): void {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

function getValue(item: T, key: keyof T | string): unknown {
  return item[key as keyof T]
}

const sortedItems = computed(() => {
  if (!sortKey.value) return props.items

  const key = sortKey.value
  const order = sortOrder.value === 'asc' ? 1 : -1

  return [...props.items].sort((a: T, b: T) => {
    const aValue = getValue(a, key)
    const bValue = getValue(b, key)

    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return aValue.localeCompare(bValue) * order
    }

    if (aValue == null) return 1 * order
    if (bValue == null) return -1 * order

    if (aValue < bValue) return -1 * order
    if (aValue > bValue) return 1 * order
    return 0
  })
})
</script>
