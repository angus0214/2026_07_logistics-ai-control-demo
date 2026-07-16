<script setup lang="ts">
import { 
  UserCheck, 
  DatabaseZap, 
  RefreshCw,
  ArrowRight
} from 'lucide-vue-next'
</script>

<template>
  <section class="py-24 px-6 lg:px-16 bg-white text-gray-800 relative overflow-hidden">
    
    <!-- Background Decorator -->
    <div class="absolute top-0 right-0 w-[600px] h-[600px] bg-green-50 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3 pointer-events-none"></div>

    <div class="max-w-7xl mx-auto space-y-16 relative z-10">
      
      <!-- Section Header -->
      <div class="text-center max-w-4xl mx-auto space-y-6">
        <h2 class="text-sm font-bold tracking-widest text-green-600 uppercase">Data Flywheel</h2>
        <h3 class="text-3xl md:text-4xl font-extrabold text-gray-900">Bad Case 收集與迭代機制</h3>
        <p class="text-lg text-gray-600 leading-relaxed font-medium">
          本專案內建資料回饋機制，將第一線人員的日常修正動作，自動轉化為提升 AI 準確率的訓練資料。
        </p>
      </div>

      <!-- Flywheel Steps -->
      <div class="relative max-w-5xl mx-auto pt-8">
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
          
          <!-- Step 1: Human-in-the-Loop -->
          <div class="bg-white rounded-3xl p-8 border border-gray-100 shadow-xl shadow-gray-200/50 flex flex-col items-center text-center relative group hover:-translate-y-2 transition-transform duration-300">
            <div class="w-20 h-20 bg-blue-50 rounded-2xl flex items-center justify-center mb-6 text-blue-600 group-hover:scale-110 group-hover:bg-blue-600 group-hover:text-white transition-all shadow-inner">
              <UserCheck class="w-10 h-10" />
            </div>
            <h4 class="text-xl font-bold text-gray-900 mb-3">1. 前端手動修正<br/><span class="text-sm text-gray-500 font-normal">Human-in-the-Loop</span></h4>
            <p class="text-gray-600 leading-relaxed text-sm">
              當 AI 萃取結果（如提單號碼或貨重）有誤時，操作人員直接在前端介面上進行手動修改與確認送出。
            </p>
            
            <!-- Arrow to next step (Desktop) -->
            <div class="hidden md:block absolute -right-6 top-1/2 -translate-y-1/2 z-20 text-gray-300">
              <ArrowRight class="w-8 h-8" />
            </div>
          </div>

          <!-- Step 2: Bad Case Logging -->
          <div class="bg-white rounded-3xl p-8 border border-gray-100 shadow-xl shadow-gray-200/50 flex flex-col items-center text-center relative group hover:-translate-y-2 transition-transform duration-300">
            <div class="w-20 h-20 bg-yellow-50 rounded-2xl flex items-center justify-center mb-6 text-yellow-600 group-hover:scale-110 group-hover:bg-yellow-500 group-hover:text-white transition-all shadow-inner">
              <DatabaseZap class="w-10 h-10" />
            </div>
            <h4 class="text-xl font-bold text-gray-900 mb-3">2. 錯誤紀錄收集<br/><span class="text-sm text-gray-500 font-normal">Data Logging</span></h4>
            <p class="text-gray-600 leading-relaxed text-sm">
              系統自動攔截修改紀錄，將「AI 原始輸出」與「人工正確輸入」對齊打包，寫入 SQLite 的 Bad Case 專屬資料表。
            </p>

            <!-- Arrow to next step (Desktop) -->
            <div class="hidden md:block absolute -right-6 top-1/2 -translate-y-1/2 z-20 text-gray-300">
              <ArrowRight class="w-8 h-8" />
            </div>
          </div>

          <!-- Step 3: Continuous Iteration -->
          <div class="bg-white rounded-3xl p-8 border border-gray-100 shadow-xl shadow-gray-200/50 flex flex-col items-center text-center relative group hover:-translate-y-2 transition-transform duration-300">
            <div class="w-20 h-20 bg-green-50 rounded-2xl flex items-center justify-center mb-6 text-green-600 group-hover:scale-110 group-hover:bg-green-600 group-hover:text-white transition-all shadow-inner">
              <RefreshCw class="w-10 h-10" />
            </div>
            <h4 class="text-xl font-bold text-gray-900 mb-3">3. 系統迭代優化<br/><span class="text-sm text-gray-500 font-normal">Continuous Iteration</span></h4>
            <p class="text-gray-600 leading-relaxed text-sm">
              開發團隊定期匯出 Bad Case 資料庫，藉此微調 Vision API 的 Prompt 參數或更新 RAG 向量庫，提升後續辨識率。
            </p>
          </div>

        </div>

        <!-- Loop back visual (Bottom line connecting 3 back to 1) -->
        <div class="hidden md:block mt-8 relative h-12">
          <!-- Horizontal line -->
          <div class="absolute top-1/2 left-1/6 right-1/6 h-[2px] bg-gradient-to-l from-green-200 via-blue-200 to-transparent"></div>
          <!-- Text Label -->
          <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-4 text-xs font-bold tracking-widest text-gray-400 uppercase">
            Data Flywheel Loop
          </div>
        </div>

      </div>

    </div>
  </section>
</template>
