<script setup lang="ts">
import { 
  FileUp, 
  Database, 
  MessageSquareText, 
  ShieldCheck,
  Server
} from 'lucide-vue-next'
</script>

<template>
  <section class="py-24 px-6 lg:px-16 bg-slate-900 text-gray-300 relative overflow-hidden">
    <!-- Subtle Background Glow -->
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-900/20 rounded-full blur-[120px] pointer-events-none"></div>

    <div class="max-w-7xl mx-auto space-y-16 relative z-10">
      
      <!-- Section Header -->
      <div class="text-center max-w-4xl mx-auto space-y-6">
        <h2 class="text-sm font-bold tracking-widest text-blue-400 uppercase">Architecture & Data Flow</h2>
        <h3 class="text-3xl md:text-4xl font-extrabold text-white">技術解構：架構與安全隔離</h3>
        <p class="text-lg text-gray-400 leading-relaxed max-w-2xl mx-auto">
          本專案以 <strong class="text-blue-400">Sidecar (外掛模組)</strong> 形式部署，與企業既有的 ERP 系統保持隔離，在不干擾核心運營的前提下進行技術概念驗證。
        </p>
      </div>

      <!-- Architecture Container -->
      <div class="relative max-w-6xl mx-auto pt-8">
        
        <!-- Legacy System (Left/Top conceptually, but we put it as a separate node pointing to the sidecar) -->
        <div class="flex justify-center mb-12">
          <div class="flex items-center space-x-4 bg-gray-800/50 px-6 py-3 rounded-full border border-gray-700">
            <Server class="w-5 h-5 text-gray-400" />
            <span class="text-gray-300 font-medium tracking-wide">既有核心 ERP 系統 (Legacy System)</span>
          </div>
        </div>

        <!-- The Air-Gap / Isolation Barrier -->
        <div class="absolute left-1/2 -translate-x-1/2 top-[100px] flex flex-col items-center">
          <div class="h-12 w-px bg-dashed border-l-2 border-dashed border-yellow-500/50"></div>
          <div class="bg-yellow-900/30 border border-yellow-700 text-yellow-500 text-xs px-3 py-1 rounded-full flex items-center space-x-2 my-2">
            <ShieldCheck class="w-4 h-4" />
            <span>Air-Gapped / 單向唯讀隔離層</span>
          </div>
          <div class="h-12 w-px bg-dashed border-l-2 border-dashed border-yellow-500/50"></div>
        </div>

        <!-- AI Sidecar Container -->
        <div class="mt-32 p-1 border-2 border-dashed border-blue-500/30 rounded-3xl relative bg-slate-900/50 backdrop-blur-sm">
          <!-- Container Label -->
          <div class="absolute -top-4 left-8 bg-slate-900 px-4 text-blue-400 text-sm font-bold tracking-widest uppercase flex items-center">
            AI Sidecar (Dockerized POC Environment)
          </div>

          <!-- Architecture Flow Diagram (CSS Grid) -->
          <div class="relative p-6 lg:p-12">
            
            <!-- Connecting Line (Simple Animated Data Flow) -->
            <div class="hidden lg:block absolute top-1/2 left-0 w-full h-[2px] -translate-y-1/2 z-0">
              <div class="absolute inset-0 bg-gray-800"></div>
              <div class="absolute inset-0 bg-blue-500/30 animate-pulse"></div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 lg:gap-12 relative z-10">
              
              <!-- Engine 1: Op Copilot -->
              <div class="bg-gray-800 rounded-2xl p-8 border border-gray-700 shadow-xl flex flex-col items-center text-center hover:border-blue-500 transition-colors group h-full">
                <div class="w-16 h-16 bg-blue-900/50 rounded-full flex items-center justify-center border border-blue-700 mb-6 group-hover:scale-110 transition-transform shrink-0">
                  <FileUp class="w-8 h-8 text-blue-400" />
                </div>
                <h4 class="text-xl font-bold text-white mb-2">1. Op Copilot<br/><span class="text-sm text-blue-400 font-normal">營運輸入引擎</span></h4>
                <p class="text-sm text-gray-400 mb-6">
                  業務上傳非結構化提單，透過視覺模型進行版面分析與欄位自動萃取。
                </p>
                <!-- Tech Badges -->
                <div class="flex flex-wrap justify-center gap-2 mt-auto">
                  <span class="bg-slate-700 text-gray-200 text-xs px-2 py-1 rounded border border-slate-600">Vue 3</span>
                  <span class="bg-blue-900/50 text-blue-300 text-xs px-2 py-1 rounded border border-blue-800">LangChain Vision</span>
                </div>
              </div>

              <!-- Central Hub: SQLite -->
              <div class="bg-gray-800 rounded-2xl p-8 border border-gray-700 shadow-xl flex flex-col items-center text-center hover:border-indigo-500 transition-colors group h-full">
                <div class="w-16 h-16 bg-indigo-900/50 rounded-full flex items-center justify-center border border-indigo-700 mb-6 group-hover:scale-110 transition-transform shrink-0">
                  <Database class="w-8 h-8 text-indigo-400" />
                </div>
                <h4 class="text-xl font-bold text-white mb-2">2. Database<br/><span class="text-sm text-indigo-400 font-normal">輕量級關聯資料庫</span></h4>
                <p class="text-sm text-gray-400 mb-6">
                  將萃取出的資料扁平化寫入關聯庫，準備好作為決策分析的高品質數據源。
                </p>
                <!-- Tech Badges -->
                <div class="flex flex-wrap justify-center gap-2 mt-auto">
                  <span class="bg-slate-700 text-gray-200 text-xs px-2 py-1 rounded border border-slate-600">FastAPI</span>
                  <span class="bg-indigo-900/50 text-indigo-300 text-xs px-2 py-1 rounded border border-indigo-800">SQLite / ChromaDB</span>
                </div>
              </div>

              <!-- Engine 2: Boss Dashboard -->
              <div class="bg-gray-800 rounded-2xl p-8 border border-gray-700 shadow-xl flex flex-col items-center text-center hover:border-green-500 transition-colors group h-full">
                <div class="w-16 h-16 bg-green-900/50 rounded-full flex items-center justify-center border border-green-700 mb-6 group-hover:scale-110 transition-transform shrink-0">
                  <MessageSquareText class="w-8 h-8 text-green-400" />
                </div>
                <h4 class="text-xl font-bold text-white mb-2">3. Boss Dashboard<br/><span class="text-sm text-green-400 font-normal">決策輸出引擎</span></h4>
                <p class="text-sm text-gray-400 mb-6">
                  高管輸入白話文，系統即時將自然語言轉為精準 SQL 查詢並生成視覺化圖表。
                </p>
                <!-- Tech Badges -->
                <div class="flex flex-wrap justify-center gap-2 mt-auto">
                  <span class="bg-green-900/50 text-green-300 text-xs px-2 py-1 rounded border border-green-800">Text-to-SQL</span>
                  <span class="bg-slate-700 text-gray-200 text-xs px-2 py-1 rounded border border-slate-600">LLM Generation</span>
                </div>
              </div>

            </div>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>
