<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { LucideZoomIn, LucideZoomOut, LucideRotateCcw } from '@lucide/vue'

const props = defineProps<{
  src: string
}>()

const scale = ref(1)
const translateX = ref(0)
const translateY = ref(0)
const isDragging = ref(false)
const startX = ref(0)
const startY = ref(0)

const containerRef = ref<HTMLElement | null>(null)

const handleWheel = (e: WheelEvent) => {
  e.preventDefault()
  const zoomSensitivity = 0.1
  if (e.deltaY < 0) {
    scale.value = Math.min(scale.value + zoomSensitivity, 5)
  } else {
    scale.value = Math.max(scale.value - zoomSensitivity, 0.5)
  }
}

const startDrag = (e: MouseEvent) => {
  e.preventDefault()
  isDragging.value = true
  startX.value = e.clientX - translateX.value
  startY.value = e.clientY - translateY.value
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  translateX.value = e.clientX - startX.value
  translateY.value = e.clientY - startY.value
}

const stopDrag = () => {
  isDragging.value = false
}

const resetZoom = () => {
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
}

onMounted(() => {
  window.addEventListener('mouseup', stopDrag)
})
onUnmounted(() => {
  window.removeEventListener('mouseup', stopDrag)
})
</script>

<template>
  <div 
    ref="containerRef"
    class="relative w-full h-full overflow-hidden bg-zinc-950/80 rounded-xl border border-zinc-800/80 group select-none cursor-grab active:cursor-grabbing shadow-inner"
    @wheel="handleWheel"
    @mousedown="startDrag"
    @mousemove="onDrag"
    @mouseleave="stopDrag"
  >
    <div class="absolute top-4 right-4 z-10 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
      <button @click="scale = Math.min(scale + 0.5, 5)" class="p-2 rounded-md bg-zinc-800/80 text-zinc-300 hover:bg-zinc-700 hover:text-white backdrop-blur-sm transition-colors shadow-lg border border-zinc-700/50" title="放大">
        <LucideZoomIn class="w-4 h-4" />
      </button>
      <button @click="scale = Math.max(scale - 0.5, 0.5)" class="p-2 rounded-md bg-zinc-800/80 text-zinc-300 hover:bg-zinc-700 hover:text-white backdrop-blur-sm transition-colors shadow-lg border border-zinc-700/50" title="縮小">
        <LucideZoomOut class="w-4 h-4" />
      </button>
      <button @click="resetZoom" class="p-2 rounded-md bg-zinc-800/80 text-zinc-300 hover:bg-zinc-700 hover:text-white backdrop-blur-sm transition-colors shadow-lg border border-zinc-700/50" title="重設畫面">
        <LucideRotateCcw class="w-4 h-4" />
      </button>
    </div>

    <img 
      :src="src" 
      alt="提單預覽" 
      class="w-full h-full object-contain pointer-events-none transition-transform duration-75 ease-out"
      :style="{ transform: `translate(${translateX}px, ${translateY}px) scale(${scale})` }"
    />
    
    <!-- 操作提示 -->
    <div class="absolute bottom-4 left-0 right-0 flex justify-center pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
      <div class="px-3 py-1.5 rounded-full bg-zinc-900/80 text-zinc-400 text-xs backdrop-blur-md border border-zinc-800 shadow-xl">
        滑鼠滾輪縮放 / 拖曳移動畫面
      </div>
    </div>
  </div>
</template>
