<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const isOpen = ref(false)

onMounted(() => {
  // 檢查 localStorage，若無紀錄則顯示 Modal
  const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding')
  if (!hasSeenOnboarding) {
    isOpen.value = true
  }
})

const handleClose = () => {
  isOpen.value = false
  localStorage.setItem('hasSeenOnboarding', 'true')
}
</script>

<template>
  <Dialog :open="isOpen" @update:open="handleClose">
    <DialogContent class="sm:max-w-md bg-zinc-950 border-zinc-800 text-zinc-100 p-0 overflow-hidden">
      <!-- 頂部視覺區塊 -->
      <div class="h-32 bg-gradient-to-br from-emerald-900/40 via-zinc-900 to-zinc-950 flex items-center justify-center border-b border-zinc-800/50 relative overflow-hidden">
        <div class="absolute inset-0 bg-[linear-gradient(to_right,#0596691a_1px,transparent_1px),linear-gradient(to_bottom,#0596691a_1px,transparent_1px)] bg-[size:14px_24px]"></div>
        <div class="relative z-10 flex flex-col items-center gap-2">
          <div class="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-400"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
          </div>
          <h2 class="text-lg font-bold text-zinc-100 tracking-tight">AI Control Tower</h2>
        </div>
      </div>

      <div class="p-6">
        <DialogHeader class="mb-4">
          <DialogTitle class="text-xl text-center">歡迎體驗 Logistics AI Control Tower</DialogTitle>
          <DialogDescription class="text-center text-zinc-400 mt-2">
            本系統展示了如何利用 AI 打通物流業資訊孤島，請透過左側選單依序體驗三大核心場景：
          </DialogDescription>
        </DialogHeader>

        <div class="space-y-4 my-6">
          <div class="bg-zinc-900/50 rounded-lg p-3.5 border border-zinc-800/80">
            <h3 class="text-sm font-semibold text-emerald-400 flex items-center gap-2 mb-1">
              <span class="text-lg">1️⃣</span> 文件解析 (OP Copilot)
            </h3>
            <p class="text-xs text-zinc-300 leading-relaxed pl-7">
              點擊右側「Demo 測試」按鈕，體驗 Vision AI 如何自動萃取單據資料，取代人工登打。
            </p>
          </div>

          <div class="bg-zinc-900/50 rounded-lg p-3.5 border border-zinc-800/80">
            <h3 class="text-sm font-semibold text-emerald-400 flex items-center gap-2 mb-1">
              <span class="text-lg">2️⃣</span> 數據入庫 (DB 表格)
            </h3>
            <p class="text-xs text-zinc-300 leading-relaxed pl-7">
              預覽解析後的結構化資料，了解資料庫目前掌握了哪些物流維度。
            </p>
          </div>

          <div class="bg-zinc-900/50 rounded-lg p-3.5 border border-zinc-800/80">
            <h3 class="text-sm font-semibold text-emerald-400 flex items-center gap-2 mb-1">
              <span class="text-lg">3️⃣</span> 營運對話 (Boss 戰情室)
            </h3>
            <p class="text-xs text-zinc-300 leading-relaxed pl-7">
              在左側對話框輸入：<span class="text-emerald-300 font-mono">「幫我統計今年運往洛杉磯 (USLAX) 的總重量是多少？」</span>，體驗 Agent 如何直接將自然語言轉為資料庫查詢。
            </p>
          </div>
        </div>

        <DialogFooter class="sm:justify-center mt-4">
          <button 
            type="button" 
            @click="handleClose" 
            class="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm px-10 py-2.5 rounded-md transition-all shadow-lg shadow-emerald-900/20 active:scale-95"
          >
            開始體驗 (Get Started)
          </button>
        </DialogFooter>
      </div>
    </DialogContent>
  </Dialog>
</template>
