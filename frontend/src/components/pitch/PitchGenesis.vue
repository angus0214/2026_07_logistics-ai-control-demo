<script setup lang="ts">
import {
  FileSearch,
  Cpu
} from 'lucide-vue-next'
</script>

<template>
  <section class="py-24 px-6 lg:px-16 bg-white text-gray-800">
    <div class="max-w-7xl mx-auto space-y-16">

      <!-- Section Header -->
      <div class="text-center max-w-4xl mx-auto space-y-6">
        <h2 class="text-sm font-bold tracking-widest text-blue-600 uppercase">Genesis & Strategy</h2>
        <h3 class="text-3xl md:text-4xl font-extrabold text-gray-900">專案緣起與軟著陸戰略</h3>
        <p class="text-xl text-gray-600 leading-relaxed font-medium">
          本專案衍生自真實的物流業數位轉型諮詢案。與其規劃龐大的系統重構，我們選擇以「Agentic AI 概念驗證 (POC)」作為第一道策略——<strong
            class="text-blue-600">先解決立即見效的痛點，建立內部信任，再談底層重構。</strong>
        </p>
      </div>

      <!-- Before & After Comparison -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12">

        <!-- Before Card (Pain Points) -->
        <div
          class="bg-red-50/50 rounded-3xl p-8 lg:p-10 border border-red-100 shadow-sm relative overflow-hidden transition-all hover:shadow-md">
          <div class="absolute top-0 right-0 p-8 opacity-10">
            <FileSearch class="w-32 h-32 text-red-600" />
          </div>
          <div class="relative z-10 space-y-8">
            <h4 class="text-2xl font-bold text-red-800 flex items-center border-b border-red-200/50 pb-4">
              <span class="bg-red-100 text-red-600 px-3 py-1 rounded-full text-sm mr-4 shadow-sm">Before</span>
              紙本地獄與資訊孤島
            </h4>
            <ul class="space-y-6 text-gray-700">
              <li class="flex items-start">
                <span class="text-red-500 mr-4 mt-1 font-bold text-lg">✖</span>
                <div>
                  <strong class="block text-gray-900 text-lg mb-1">基層痛點：常態性加班</strong>
                  面對格式各異的提單（含手寫圖片），高度仰賴<strong class="bg-red-100 text-red-800 px-1 rounded">純人工登打</strong>，導致嚴重的<strong class="text-red-600 font-bold">加班費損耗</strong>與<strong class="text-red-600 font-bold">人才流失</strong>。
                </div>
              </li>
              <li class="flex items-start">
                <span class="text-red-500 mr-4 mt-1 font-bold text-lg">✖</span>
                <div>
                  <strong class="block text-gray-900 text-lg mb-1">管理痛點：決策時間差</strong>
                  內部各子系統<strong class="bg-red-100 text-red-800 px-1 rounded">互不連通</strong>，形成難以打破的<strong class="text-red-600 font-bold">資訊孤島</strong>，營運數據與財報永遠存在落後的<strong class="text-red-600 font-bold">時間差</strong>。
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- After Card (Solution) -->
        <div
          class="bg-blue-50/50 rounded-3xl p-8 lg:p-10 border border-blue-100 shadow-sm relative overflow-hidden transition-all hover:shadow-md">
          <div class="absolute top-0 right-0 p-8 opacity-10">
            <Cpu class="w-32 h-32 text-blue-600" />
          </div>
          <div class="relative z-10 space-y-8">
            <h4 class="text-2xl font-bold text-blue-800 flex items-center border-b border-blue-200/50 pb-4">
              <span class="bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-sm mr-4 shadow-sm">After</span>
              AI 賦能的破局戰略
            </h4>
            <ul class="space-y-6 text-gray-700">
              <li class="flex items-start">
                <span class="text-blue-500 mr-4 mt-1 font-bold text-lg">✔</span>
                <div>
                  <strong class="block text-gray-900 text-lg mb-1">營運解方 (Op Copilot)</strong>
                  透過 AI 視覺自動解析非結構化文件，<strong class="text-blue-700 font-bold">消滅無效的機械化登打作業</strong>，直接替公司<strong class="bg-blue-100 text-blue-800 px-1 rounded">省下加班費</strong>。
                </div>
              </li>
              <li class="flex items-start">
                <span class="text-blue-500 mr-4 mt-1 font-bold text-lg">✔</span>
                <div>
                  <strong class="block text-gray-900 text-lg mb-1">管理解方 (Boss Dashboard)</strong>
                  以白話文 (Text-to-SQL) <strong class="text-blue-700 font-bold">跨越系統孤島</strong>，不畫宏大架構的空餅，直接交付老闆<strong class="bg-blue-100 text-blue-800 px-1 rounded">立即可見效的決策工具</strong>。
                </div>
              </li>
            </ul>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>
