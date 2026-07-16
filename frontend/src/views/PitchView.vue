<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const launchDemo = () => {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-800 font-sans selection:bg-blue-200">
    <!-- Hero Section (Terminal Style, 2-Column) -->
    <section class="min-h-[85vh] flex flex-col justify-center px-6 lg:px-16 py-12 bg-slate-900 text-gray-300">
      <div class="w-full max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
        
        <!-- Left Column: Title & CTA -->
        <div class="w-full lg:w-5/12 flex flex-col items-center lg:items-start text-center lg:text-left space-y-8">
          <div class="space-y-4">
            <!-- 中文標題 -->
            <h1 class="text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
              <span class="text-blue-400">Agentic AI</span> x Logistics
            </h1>
            <p class="text-lg text-gray-400 leading-relaxed max-w-xl">
              概念驗證 (POC)：消除紙本提單瓶頸，打破跨部門資料孤島的解決方案。
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row w-full sm:w-auto items-center space-y-4 sm:space-y-0 sm:space-x-4">
            <button 
              @click="launchDemo"
              class="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg shadow-lg hover:shadow-blue-500/30 transition-all duration-300 text-lg tracking-wider"
            >
              啟動 Demo 🚀
            </button>
            <a 
              href="https://github.com/angus0214/2026_07_logistics-ai-control-demo" 
              target="_blank"
              class="w-full sm:w-auto px-8 py-4 bg-transparent hover:bg-gray-800 text-white font-semibold rounded-lg transition-all duration-300 text-lg text-center border border-gray-600 hover:border-gray-400 tracking-wider"
            >
              檢視 GitHub
            </a>
          </div>
        </div>

        <!-- Right Column: Terminal Window -->
        <div class="w-full lg:w-7/12">
          <div class="rounded-xl shadow-2xl bg-[#1e1e1e] overflow-hidden border border-gray-700">
            <!-- Terminal Header -->
            <div class="flex items-center px-4 py-3 bg-[#2d2d2d] border-b border-gray-700">
              <div class="flex space-x-2">
                <div class="w-3 h-3 rounded-full bg-red-500"></div>
                <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div class="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <div class="mx-auto text-xs text-gray-400 font-mono tracking-wider">
                bash - angus41c.dev
              </div>
            </div>
            <!-- Terminal Body -->
            <div class="p-6 sm:p-8 font-mono text-sm sm:text-base leading-relaxed overflow-x-auto">
              <div class="text-green-400 mb-2">$ cat project_spec.json</div>
              <pre class="text-gray-300"><code>{
  <span class="text-blue-400">"project"</span>: <span class="text-orange-300">"Logistics AI Control Tower"</span>,
  <span class="text-blue-400">"role"</span>: <span class="text-orange-300">"Forward Deployed Engineer (POC)"</span>,
  <span class="text-blue-400">"status"</span>: <span class="text-orange-300">"Live Demo Available"</span>,
  <span class="text-blue-400">"tech_stack"</span>: [
    <span class="text-orange-300">"FastAPI"</span>, <span class="text-orange-300">"Vue 3"</span>,
    <span class="text-orange-300">"LangChain"</span>, <span class="text-orange-300">"ChromaDB"</span>,
    <span class="text-orange-300">"SQLite"</span>
  ]
}</code></pre>
              <div class="text-green-400 mt-6 mb-2 animate-pulse">$ _</div>
            </div>
          </div>
        </div>
        
      </div>
    </section>
    
    <!-- Placeholder for upcoming sections (Issue 7-10) -->
    <div class="py-20 text-center text-gray-500">
      More content coming soon... (Scroll down)
    </div>
  </div>
</template>

<style scoped>
/* Any specific pitch styling */
</style>
