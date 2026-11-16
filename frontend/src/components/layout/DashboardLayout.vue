<script setup lang="ts">
import { ref } from 'vue'
import { LucideFileText, LucideMenu, LucideX } from '@lucide/vue'
import LeftSidebar from './LeftSidebar.vue'

defineProps({
  hideRightSidebar: {
    type: Boolean,
    default: false
  },
  pageTitle: {
    type: String,
    default: '文件進件與 OCR 覆核'
  },
  rightPanelTitle: {
    type: String,
    default: 'Original Document'
  }
})

const isSidebarOpen = ref(false)
const isRightPanelOpen = ref(false)
</script>

<template>
  <div class="h-screen w-full flex overflow-hidden bg-zinc-950 text-zinc-50 font-sans selection:bg-emerald-500/30">
    
    <!-- Mobile Sidebar Overlay Backdrop -->
    <div 
      v-if="isSidebarOpen" 
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden transition-opacity"
      @click="isSidebarOpen = false"
    ></div>

    <!-- Left Sidebar (Drawer on Mobile, Static on Desktop) -->
    <aside 
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 border-r border-zinc-800/60 bg-zinc-950 flex flex-col shadow-[4px_0_24px_-12px_rgba(0,0,0,0.5)] transition-transform duration-300 ease-in-out md:relative md:translate-x-0',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <LeftSidebar @close="isSidebarOpen = false" />
    </aside>

    <!-- Center Data Processing Area -->
    <main class="flex-1 flex flex-col min-w-0 bg-zinc-900/40 relative">
      <header class="h-16 shrink-0 border-b border-zinc-800/60 flex items-center px-4 md:px-8 bg-zinc-950/50 backdrop-blur-md sticky top-0 z-10 justify-between">
        <div class="flex items-center gap-3">
          <button 
            class="md:hidden p-2 -ml-2 text-zinc-400 hover:text-white rounded-md hover:bg-zinc-800"
            @click="isSidebarOpen = true"
          >
            <LucideMenu class="w-5 h-5" />
          </button>
          <h2 class="text-base font-semibold tracking-wide text-zinc-200">{{ pageTitle }}</h2>
        </div>
        
        <!-- Mobile Right Panel Toggle Button -->
        <button 
          v-if="!hideRightSidebar"
          class="xl:hidden flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-zinc-800/50 border border-zinc-700/50 text-emerald-400 rounded-lg hover:bg-zinc-800 transition-colors"
          @click="isRightPanelOpen = true"
        >
          <LucideFileText class="w-4 h-4" />
          <span class="hidden sm:inline">檢視文件</span>
        </button>
      </header>
      
      <div class="flex-1 overflow-y-auto p-4 pb-16 md:p-8">
        <div class="w-full min-h-full">
          <slot name="center"></slot>
        </div>
      </div>
    </main>

    <!-- Right Image Preview Area (Modal on Mobile/Tablet, Static on Desktop) -->
    <aside 
      v-if="!hideRightSidebar" 
      :class="[
        'border-l border-zinc-800/60 bg-zinc-950 flex flex-col z-50 transition-transform duration-300 ease-in-out',
        'xl:relative xl:z-auto xl:w-[500px] xl:translate-x-0 xl:shadow-[-4px_0_24px_-12px_rgba(0,0,0,0.5)]', // Desktop
        isRightPanelOpen ? 'fixed inset-0 translate-x-0 w-full' : 'fixed inset-y-0 right-0 translate-x-full w-full xl:translate-x-0' // Mobile
      ]"
    >
      <header class="h-16 shrink-0 border-b border-zinc-800/60 flex items-center px-6 justify-between bg-zinc-950">
        <h2 class="text-xs font-semibold text-zinc-400 uppercase tracking-widest flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
          {{ rightPanelTitle }}
        </h2>
        <!-- Close button for mobile -->
        <button 
          class="xl:hidden p-2 -mr-2 text-zinc-400 hover:text-white rounded-md hover:bg-zinc-800"
          @click="isRightPanelOpen = false"
        >
          <LucideX class="w-5 h-5" />
        </button>
      </header>
      <div class="flex-1 overflow-y-auto p-4 md:p-6 flex flex-col">
        <div class="flex-1 min-h-0 rounded-xl border border-zinc-800/80 bg-zinc-900/50 flex items-center justify-center overflow-hidden relative group">
          <slot name="right">
            <div class="text-zinc-600 flex flex-col items-center gap-2">
              <LucideFileText class="w-8 h-8 opacity-50" />
              <span class="text-sm">尚未上傳提單</span>
            </div>
          </slot>
        </div>
      </div>
    </aside>
  </div>
</template>
