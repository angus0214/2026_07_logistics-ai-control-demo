<template>
  <DashboardLayout page-title="主管戰情室" right-panel-title="資料視覺化">
    <template #center>
      <!-- Chat Display Area -->
      <div class="flex flex-col h-full">
        <div class="flex-1 overflow-y-auto flex flex-col gap-6 pb-4">
          <div>
            <h1 class="text-2xl font-bold mb-1 text-emerald-400">Boss Dashboard <span class="text-sm font-normal text-zinc-500">v1.0</span></h1>
            <p class="text-zinc-500 text-sm mb-6">可使用自然語言直接查詢提單資料 (Text-to-SQL)</p>
          </div>
          
          <!-- Chat History -->
          <div class="flex flex-col gap-6">
            <template v-for="(msg, index) in messages" :key="index">
              <!-- User Message -->
              <div v-if="msg.role === 'user'" class="flex justify-end">
                <div class="bg-emerald-600/20 border border-emerald-500/30 text-emerald-100 px-5 py-3 rounded-2xl rounded-tr-sm max-w-[80%]">
                  {{ msg.content }}
                </div>
              </div>
              
              <!-- Assistant Message -->
              <div v-else-if="msg.role === 'assistant'" class="flex justify-start">
                <!-- Loading Placeholder for empty message -->
                <div v-if="msg.content === '' && isLoading" class="message-content px-5 py-4 bg-zinc-800/60 rounded-2xl rounded-tl-sm border border-zinc-700 shadow-lg text-zinc-400 italic flex items-center gap-3">
                  <span class="w-4 h-4 rounded-full border-2 border-emerald-500/30 border-t-emerald-500 animate-spin"></span>
                  <span class="animate-pulse">正在連接資料庫與分析意圖...</span>
                </div>
                <!-- Actual Content -->
                <div v-else class="message-content prose prose-sm prose-invert !max-w-[85%] px-5 py-4 bg-zinc-800/60 rounded-2xl rounded-tl-sm border border-zinc-700 shadow-lg prose-p:my-0 overflow-x-auto break-words" v-html="marked.parse(msg.content)">
                </div>
              </div>
            </template>
          </div>
          
          <!-- Current SSE Thought Process Block -->
          <div 
            v-if="isLoading || thoughts.length > 0" 
            class="thought-process mt-4 p-4 rounded-lg bg-zinc-900 border border-zinc-700 shadow-md transition-all duration-300"
            :class="{ 'animate-pulse': isLoading }"
          >
            <div 
              class="flex items-center justify-between cursor-pointer group"
              @click="isThoughtsExpanded = !isThoughtsExpanded"
            >
              <div class="flex items-center gap-2">
                <span class="text-emerald-500">⚙️</span>
                <span class="text-zinc-300 font-medium group-hover:text-emerald-400 transition-colors">SQL Agent 思考軌跡</span>
              </div>
              <span class="text-zinc-500 group-hover:text-emerald-400 transition-transform duration-300" :class="{ 'rotate-180': isThoughtsExpanded }">
                ▼
              </span>
            </div>
            
            <div v-show="isThoughtsExpanded" class="text-zinc-500 text-sm pl-6 flex flex-col gap-1 mt-3">
              <p v-if="thoughts.length === 0">正在連接資料庫與分析意圖...</p>
              <p v-for="(thought, idx) in thoughts" :key="idx">> {{ thought }}</p>
            </div>
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
              placeholder="例如：幫我統計今年運往 USLAX (Los Angeles) 的總重量是多少？"
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

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

const query = ref('幫我統計今年運往 USLAX (Los Angeles) 的總重量是多少？')
const isLoading = ref(false)
const thoughts = ref<string[]>([])
const messages = ref<ChatMessage[]>([])
const isThoughtsExpanded = ref(true)

const submitQuery = async () => {
  if (!query.value.trim()) return
  
  const userText = query.value.trim()
  query.value = '' // Clear input field immediately
  
  messages.value.push({ role: 'user', content: userText })
  
  isLoading.value = true
  isThoughtsExpanded.value = true // Auto-expand when a new query starts
  thoughts.value = []
  
  // Create an empty assistant message to append to
  messages.value.push({ role: 'assistant', content: '' })
  const assistantMsgIndex = messages.value.length - 1
  
  try {
    const API_BASE = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
    const response = await fetch(`${API_BASE}/api/chat/boss_sql`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userText })
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
                messages.value[assistantMsgIndex].content += parsed.data
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
