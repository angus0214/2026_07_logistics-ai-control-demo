<script setup lang="ts">
// 查詢依據 (Query Evidence)：Agent 最後一句 SQL 的原始結果。
// 數字直接來自資料庫、不經 LLM；以文字插值渲染、不用 v-html（ADR-0008）。
import { ref } from 'vue'
import { LucideChevronDown, LucideChevronRight } from '@lucide/vue'

const props = defineProps<{
  columns: string[]
  rows: unknown[][]
  truncated: boolean
}>()

const isExpanded = ref(true)

const formatCell = (value: unknown): string => {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'number') {
    return Number.isInteger(value)
      ? value.toLocaleString('en-US')
      : value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }
  return String(value)
}
</script>

<template>
  <div class="query-evidence mt-2 max-w-full sm:max-w-[85%] rounded-xl border border-zinc-700 bg-zinc-900/60 text-xs sm:text-sm">
    <button
      type="button"
      class="flex w-full items-center gap-2 px-4 py-2 text-left text-zinc-400 hover:text-zinc-200 transition-colors"
      @click="isExpanded = !isExpanded"
    >
      <LucideChevronDown v-if="isExpanded" class="w-4 h-4" />
      <LucideChevronRight v-else class="w-4 h-4" />
      <span>查詢依據 · {{ props.rows.length }} 筆</span>
    </button>
    <div v-if="isExpanded" class="overflow-x-auto border-t border-zinc-800">
      <table class="min-w-full text-left">
        <thead class="text-zinc-400">
          <tr>
            <th v-for="column in props.columns" :key="column" class="px-4 py-2 font-medium whitespace-nowrap">{{ column }}</th>
          </tr>
        </thead>
        <tbody class="text-zinc-200">
          <tr v-for="(row, rowIndex) in props.rows" :key="rowIndex" class="border-t border-zinc-800">
            <td
              v-for="(cell, cellIndex) in row"
              :key="cellIndex"
              class="px-4 py-2 whitespace-nowrap"
              :class="{ 'text-right tabular-nums': typeof cell === 'number' }"
            >{{ formatCell(cell) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="props.truncated" class="px-4 py-2 text-amber-400/80">結果較多，僅顯示前 {{ props.rows.length }} 筆。</p>
    </div>
  </div>
</template>
