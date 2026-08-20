<script setup lang="ts">
import { inject, type Ref } from 'vue'
import { LucideFileText, LucideLayoutDashboard, LucideShip, LucideDatabase, LucidePresentation } from '@lucide/vue'

const currentView = inject('currentView') as Ref<string>
const emit = defineEmits(['close'])

const handleNavClick = (view: string) => {
  currentView.value = view
  emit('close')
}
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0 bg-zinc-950 h-full">
      <div class="p-6 border-b border-zinc-800/60 h-16 shrink-0 flex items-center">
        <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-zinc-950 shadow-lg shadow-emerald-500/20">
            <LucideShip class="w-5 h-5" />
          </div>
          Logistics AI
        </h1>
      </div>
      <nav class="flex-1 overflow-y-auto p-4 space-y-1">
        <div 
          @click="handleNavClick('op')"
          class="px-3 py-2.5 rounded-lg font-medium cursor-pointer flex items-center gap-3 transition-all"
          :class="currentView === 'op' ? 'bg-zinc-800/50 text-emerald-400 border border-zinc-700/50 shadow-sm' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/30'"
        >
           <LucideFileText class="w-4 h-4" />
           OP 進件作業
        </div>
        <div 
          @click="handleNavClick('db')"
          class="px-3 py-2.5 rounded-lg font-medium cursor-pointer flex items-center gap-3 transition-all"
          :class="currentView === 'db' ? 'bg-zinc-800/50 text-emerald-400 border border-zinc-700/50 shadow-sm' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/30'"
        >
           <LucideDatabase class="w-4 h-4" />
           DB 資料庫後台
        </div>
        <div 
          @click="handleNavClick('boss')"
          class="px-3 py-2.5 rounded-lg font-medium cursor-pointer flex items-center gap-3 transition-all"
          :class="currentView === 'boss' ? 'bg-zinc-800/50 text-emerald-400 border border-zinc-700/50 shadow-sm' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/30'"
        >
           <LucideLayoutDashboard class="w-4 h-4" />
           主管戰情室
        </div>

        <div class="pt-4 mt-2 border-t border-zinc-800/60">
          <router-link 
            to="/pitch"
            @click="emit('close')"
            class="px-3 py-2.5 rounded-lg font-medium cursor-pointer flex items-center gap-3 transition-all bg-blue-500/10 text-blue-400 border border-blue-500/20 hover:bg-blue-500/20 hover:text-blue-300 shadow-[0_0_15px_rgba(59,130,246,0.15)] group"
          >
             <LucidePresentation class="w-4 h-4" />
             <span>專案介紹</span>
          </router-link>
        </div>
      </nav>
      <div class="p-4 border-t border-zinc-800/60 shrink-0 flex flex-col gap-4">
        <a 
          href="/resume.pdf"
          target="_blank"
          @click="emit('close')"
          class="flex items-center gap-2 text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors group cursor-pointer drop-shadow-[0_0_8px_rgba(16,185,129,0.5)] hover:drop-shadow-[0_0_12px_rgba(16,185,129,0.8)]"
        >
          <LucideFileText class="w-4 h-4" />
          <span>Get my Resume</span>
        </a>
        <div class="text-xs text-zinc-500 flex items-center justify-between">
          <span>Angus Workspace</span>
          <span class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
        </div>
      </div>
  </div>
</template>
