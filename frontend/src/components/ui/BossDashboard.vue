<template>
  <DashboardLayout>
    <template #center>
      <!-- Chat Display Area -->
      <div class="flex flex-col h-full">
        <div class="flex-1 overflow-y-auto flex flex-col gap-6 pb-4">
          <div>
            <h1 class="text-2xl font-bold mb-1 text-emerald-400">Boss Dashboard <span class="text-sm font-normal text-zinc-500">v1.0</span></h1>
            <p class="text-zinc-500 text-sm mb-6">可使用自然語言直接查詢提單資料 (Text-to-SQL)</p>
          </div>
          
          <!-- SSE Thought Process Block -->
          <div 
            v-if="isLoading || thoughts.length > 0" 
            class="thought-process mb-2 p-4 rounded-lg bg-zinc-900 border border-zinc-700 shadow-md"
            :class="{ 'animate-pulse': isLoading }"
          >
            <div class="flex items-center gap-2 mb-2">
              <span class="text-emerald-500">⚙️</span>
              <span class="text-zinc-300 font-medium">SQL Agent 思考軌跡</span>
            </div>
            <div class="text-zinc-500 text-sm pl-6 flex flex-col gap-1">
              <p v-if="thoughts.length === 0">正在連接資料庫與分析意圖...</p>
              <p v-for="(thought, idx) in thoughts" :key="idx">> {{ thought }}</p>
            </div>
          </div>

          <!-- Final Message Block -->
          <div v-if="finalMessage" class="message-content prose prose-sm prose-invert max-w-none p-6 bg-zinc-800/60 rounded-lg border border-zinc-700 shadow-lg" v-html="marked.parse(finalMessage)">
          </div>
        </div>

        <!-- Input Area -->
        <div class="pt-4 border-t border-zinc-800/80 mt-auto">
          <div class="flex gap-3">
            <input 
              type="text" 
              v-model="query"
              @keyup.enter="submitQuery"
              class="flex-1 bg-zinc-950/50 border border-zinc-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-zinc-100 placeholder-zinc-600 shadow-inner"
              placeholder="例如：幫我統計上個月不同航空公司的運費總和？"
            />
            <button 
              @click="submitQuery"
              class="submit-btn bg-emerald-600 hover:bg-emerald-500 text-white px-8 py-3 rounded-lg font-medium transition-colors shadow-lg shadow-emerald-900/20"
            >
              發送分析
            </button>
          </div>
        </div>
      </div>
    </template>

    <template #right>
      <div class="w-full h-full p-6 flex flex-col">
        <h2 class="text-sm font-semibold mb-4 text-zinc-400 uppercase tracking-widest">資料視覺化</h2>
        <div class="flex-1 rounded-xl border border-dashed border-zinc-700/80 bg-zinc-900/30 flex items-center justify-center">
          <p class="text-zinc-600 text-sm italic">圖表預留區塊</p>
        </div>
      </div>
    </template>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { marked } from 'marked'
import DashboardLayout from '@/components/layout/DashboardLayout.vue'

const query = ref('')
const isLoading = ref(false)
const thoughts = ref<string[]>([])
const finalMessage = ref('')

const submitQuery = async () => {
  if (!query.value.trim()) return
  
  isLoading.value = true
  thoughts.value = []
  finalMessage.value = ''
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/chat/boss_sql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: query.value })
    })

    if (!response.body) throw new Error('No stream')

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let done = false

    while (!done) {
      const { value, done: readerDone } = await reader.read()
      done = readerDone
      if (value) {
        const chunkText = decoder.decode(value, { stream: true })
        const lines = chunkText.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const dataStr = line.replace('data: ', '').trim()
              if (!dataStr) continue
              const parsed = JSON.parse(dataStr)
              
              if (parsed.event === 'thought') {
                thoughts.value.push(parsed.data)
              } else if (parsed.event === 'message') {
                finalMessage.value += parsed.data
              }
            } catch (e) {
              // ignore
            }
          }
        }
      }
    }
  } catch (error) {
    thoughts.value.push('連線錯誤或後端尚未準備好。')
  } finally {
    isLoading.value = false
  }
}
</script>
