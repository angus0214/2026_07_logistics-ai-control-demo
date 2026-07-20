<script setup lang="ts">
import { ref } from 'vue'
import { LucideUploadCloud, LucideFileImage } from '@lucide/vue'

const emit = defineEmits<{
  (e: 'file-selected', file: File): void
}>()

const isDragging = ref(false)

const onDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = true
}

const onDragLeave = () => {
  isDragging.value = false
}

const onDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    emit('file-selected', files[0])
  }
}

const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    emit('file-selected', target.files[0])
  }
}

const isDemoLoading = ref(false)
const loadDemoFile = async (type: 'invoice' | 'packing-list') => {
  try {
    isDemoLoading.value = true
    const fileName = type === 'invoice' ? 'invoice.jpg' : 'packing-list.jpg'
    const response = await fetch(`/demo/${fileName}`)
    if (!response.ok) throw new Error('Failed to fetch demo image')
    const blob = await response.blob()
    const file = new File([blob], fileName, { type: 'image/jpeg' })
    emit('file-selected', file)
  } catch (error) {
    console.error('Failed to load demo file:', error)
    alert('載入 Demo 檔案失敗，請確定檔案存在 /public/demo 中')
  } finally {
    isDemoLoading.value = false
  }
}
</script>

<template>
  <div 
    class="relative w-full border-2 border-dashed rounded-xl py-6 px-8 transition-all duration-200 flex flex-col items-center justify-center cursor-pointer group"
    :class="[
      isDragging 
        ? 'border-emerald-500 bg-emerald-500/10' 
        : 'border-zinc-700 hover:border-emerald-500/50 hover:bg-zinc-800/50 bg-zinc-900/30'
    ]"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
    @click="$refs.fileInput.click()"
  >
    <input 
      type="file" 
      ref="fileInput" 
      class="hidden" 
      accept="image/jpeg, image/png, application/pdf"
      @change="onFileChange"
    />
    
    <div class="w-16 h-16 mb-4 rounded-full bg-zinc-800 flex items-center justify-center group-hover:bg-zinc-700 transition-colors shadow-inner">
      <LucideUploadCloud 
        class="w-8 h-8 transition-colors" 
        :class="isDragging ? 'text-emerald-400' : 'text-zinc-400 group-hover:text-emerald-400'" 
      />
    </div>
    
    <h3 class="text-base font-semibold text-zinc-200 mb-1">拖曳提單圖片至此</h3>
    <p class="text-sm text-zinc-500 text-center max-w-sm">
      支援 JPEG, PNG 等影像格式。<br/>
      AI 引擎將自動啟動 OCR 與實體擷取。
    </p>
    
    <div class="mt-6 flex flex-col items-center gap-4 w-full">
      <button class="px-4 py-2 rounded-md bg-zinc-100 text-zinc-900 text-sm font-medium hover:bg-zinc-200 transition-colors shadow-sm">
        選擇檔案
      </button>

      <div class="w-full max-w-sm border-t border-zinc-800 pt-4 flex flex-col items-center gap-3">
        <p class="text-xs font-medium text-emerald-400 animate-pulse flex items-center gap-1">
          💡 沒有單據？一鍵帶入 Demo 測試
        </p>
        <div class="flex gap-3">
          <button 
            @click.stop="loadDemoFile('invoice')" 
            :disabled="isDemoLoading"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-800/80 text-zinc-300 text-xs hover:bg-emerald-500 hover:text-zinc-900 transition-colors border border-zinc-700 hover:border-emerald-500 disabled:opacity-50"
          >
            <LucideFileImage class="w-3.5 h-3.5" />
            Invoice 
          </button>
          <button 
            @click.stop="loadDemoFile('packing-list')" 
            :disabled="isDemoLoading"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-800/80 text-zinc-300 text-xs hover:bg-emerald-500 hover:text-zinc-900 transition-colors border border-zinc-700 hover:border-emerald-500 disabled:opacity-50"
          >
            <LucideFileImage class="w-3.5 h-3.5" />
            Packing List
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
