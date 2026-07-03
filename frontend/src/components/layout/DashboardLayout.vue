<script setup lang="ts">
import { LucideFileText, LucideLayoutDashboard, LucideShip } from '@lucide/vue'
</script>

<template>
  <div class="h-screen w-full flex overflow-hidden bg-zinc-950 text-zinc-50 font-sans selection:bg-emerald-500/30">
    <!-- Left Sidebar Menu -->
    <aside class="w-64 flex-shrink-0 border-r border-zinc-800/60 bg-zinc-950 flex flex-col z-10 shadow-[4px_0_24px_-12px_rgba(0,0,0,0.5)]">
      <div class="p-6 border-b border-zinc-800/60 h-16 flex items-center">
        <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-zinc-950 shadow-lg shadow-emerald-500/20">
            <LucideShip class="w-5 h-5" />
          </div>
          Logistics AI
        </h1>
      </div>
      <nav class="flex-1 p-4 space-y-1">
        <div class="px-3 py-2.5 rounded-lg bg-zinc-800/50 text-emerald-400 font-medium cursor-pointer flex items-center gap-3 transition-all border border-zinc-700/50 shadow-sm">
           <LucideFileText class="w-4 h-4" />
           OP 進件作業
        </div>
        <div class="px-3 py-2.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/30 cursor-pointer flex items-center gap-3 transition-colors">
           <LucideLayoutDashboard class="w-4 h-4" />
           主管戰情室
        </div>
      </nav>
      <div class="p-4 border-t border-zinc-800/60 text-xs text-zinc-500 flex items-center justify-between">
        <span>Angus Workspace</span>
        <span class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
      </div>
    </aside>

    <!-- Center Data Processing Area -->
    <main class="flex-1 flex flex-col min-w-0 bg-zinc-900/40 relative">
      <header class="h-16 border-b border-zinc-800/60 flex items-center px-8 bg-zinc-950/50 backdrop-blur-md sticky top-0 z-10">
        <h2 class="text-base font-semibold tracking-wide text-zinc-200">文件進件與 OCR 覆核</h2>
      </header>
      <div class="flex-1 overflow-y-auto p-8">
        <div class="max-w-2xl mx-auto space-y-6">
          <slot name="center"></slot>
        </div>
      </div>
    </main>

    <!-- Right Image Preview Area -->
    <aside class="w-[500px] flex-shrink-0 border-l border-zinc-800/60 bg-zinc-950 flex flex-col z-10 shadow-[-4px_0_24px_-12px_rgba(0,0,0,0.5)]">
      <header class="h-16 border-b border-zinc-800/60 flex items-center px-6 justify-between bg-zinc-950">
        <h2 class="text-xs font-semibold text-zinc-400 uppercase tracking-widest flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
          Original Document
        </h2>
      </header>
      <div class="flex-1 overflow-hidden p-6 flex flex-col">
        <div class="flex-1 rounded-xl border border-zinc-800/80 bg-zinc-900/50 flex items-center justify-center overflow-hidden relative group">
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
