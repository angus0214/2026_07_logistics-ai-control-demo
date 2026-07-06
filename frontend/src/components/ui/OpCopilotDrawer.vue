<script setup lang="ts">
import { ref } from 'vue'
import { LucideSparkles, LucideX, LucideSend, LucideBot, LucideUser } from '@lucide/vue'

const isOpen = ref(false)
const inputMessage = ref('')
const messages = ref([
  { role: 'assistant', content: '您好！我是您的物流法規 Copilot。請問遇到什麼報關上的疑問嗎？例如：「鋰電池空運到歐盟需要什麼文件？」' }
])

const toggleDrawer = () => {
  isOpen.value = !isOpen.value
}

const isLoading = ref(false)

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const userMsg = inputMessage.value
  // 記錄使用者訊息
  messages.value.push({ role: 'user', content: userMsg })
  inputMessage.value = ''
  isLoading.value = true
  
  // 模擬思考中
  messages.value.push({ role: 'assistant', content: '思考中...' })
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/chat/op_rag', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMsg })
    })
    
    const data = await response.json()
    messages.value.pop() // 移除思考中
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch (e) {
    messages.value.pop()
    messages.value.push({ role: 'assistant', content: '連線失敗，請確認後端伺服器與 OpenAI API 是否正常運作。' })
  } finally {
    isLoading.value = false
  }
}

defineExpose({ toggleDrawer, isOpen })
</script>

<template>
  <!-- 觸發按鈕 (漂浮於右下角) -->
  <button 
    @click="toggleDrawer"
    class="fixed bottom-8 right-8 z-40 px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full shadow-xl flex items-center gap-2 font-medium transition-all hover:scale-105 group border border-indigo-400/30"
    :class="isOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'"
  >
    <LucideSparkles class="w-5 h-5 text-indigo-200 group-hover:animate-pulse" />
    法規 Copilot
  </button>

  <!-- Drawer 面板 -->
  <div 
    class="fixed top-0 right-0 h-full w-[400px] bg-zinc-950/95 backdrop-blur-xl border-l border-zinc-800 shadow-2xl z-50 transform transition-transform duration-500 cubic-bezier(0.4, 0, 0.2, 1) flex flex-col"
    :class="isOpen ? 'translate-x-0' : 'translate-x-full'"
  >
    <!-- Header -->
    <div class="h-16 flex items-center justify-between px-6 border-b border-zinc-800/80 bg-zinc-900/40">
      <div class="flex items-center gap-2 text-indigo-400 font-bold">
        <LucideSparkles class="w-5 h-5" />
        法規 Copilot (Mock)
      </div>
      <button @click="toggleDrawer" class="p-1 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-md transition-colors">
        <LucideX class="w-5 h-5" />
      </button>
    </div>

    <!-- 訊息區 -->
    <div class="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
      <div 
        v-for="(msg, idx) in messages" 
        :key="idx" 
        class="flex gap-3 animate-in slide-in-from-bottom-2 fade-in duration-300"
        :class="msg.role === 'user' ? 'flex-row-reverse' : ''"
      >
        <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1" :class="msg.role === 'user' ? 'bg-zinc-800 text-zinc-300' : 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'">
          <LucideUser v-if="msg.role === 'user'" class="w-4 h-4" />
          <LucideBot v-else class="w-4 h-4" />
        </div>
        <div 
          class="px-4 py-3 rounded-2xl max-w-[85%] text-sm leading-relaxed shadow-sm"
          :class="msg.role === 'user' ? 'bg-zinc-800 text-zinc-100 rounded-tr-sm' : 'bg-zinc-900/80 border border-zinc-800/80 text-zinc-300 rounded-tl-sm'"
        >
          {{ msg.content }}
        </div>
      </div>
    </div>

    <!-- 輸入區 -->
    <div class="p-4 border-t border-zinc-800/80 bg-zinc-950">
      <div class="relative flex items-center">
        <input 
          v-model="inputMessage" 
          @keyup.enter="sendMessage"
          type="text" 
          placeholder="詢問報關法規或 SOP..."
          class="w-full bg-zinc-900 border border-zinc-800 rounded-full pl-5 pr-12 py-3.5 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all placeholder:text-zinc-600"
        />
        <button 
          @click="sendMessage"
          class="absolute right-2 p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full transition-colors shadow-md"
          :disabled="!inputMessage.trim()"
          :class="!inputMessage.trim() ? 'opacity-50 cursor-not-allowed' : ''"
        >
          <LucideSend class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #3f3f46;
  border-radius: 20px;
}
</style>
