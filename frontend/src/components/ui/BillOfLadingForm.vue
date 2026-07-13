<script setup lang="ts">
import { useBlStore } from '@/stores/bl_store'
import { storeToRefs } from 'pinia'
import { computed, ref } from 'vue'
import { LucideCheckCircle2, LucideAlertTriangle, LucideLoader2 } from '@lucide/vue'

const blStore = useBlStore()
const { ocrData, isUploading, isAiParsed, aiRawData, imageBase64 } = storeToRefs(blStore)

const isConfident = computed(() => {
  return ocrData.value.confidence_score >= 80 && ocrData.value.suspicious_fields.length === 0
})

const isSuspicious = (field: keyof typeof ocrData.value) => {
  if (!isAiParsed.value) return false
  return ocrData.value.suspicious_fields.includes(field) ||
    ocrData.value[field] === 'Unknown' ||
    ocrData.value[field] === 0 ||
    ocrData.value[field] === ''
}

const showConfirmModal = ref(false)

const attemptSubmit = () => {
  showConfirmModal.value = true
}

const checkIsBadCase = () => {
  if (!isAiParsed.value || !aiRawData.value) return { isBadCase: false, modifiedFields: [] }
  
  // 比對兩者是否完全一致 (不包含 suspicious_fields)
  const current = { ...ocrData.value }
  const original = { ...aiRawData.value }
  delete (current as any).suspicious_fields
  delete (original as any).suspicious_fields
  
  const modifiedFields: string[] = []
  for (const key in current) {
    if (current[key as keyof typeof current] !== original[key as keyof typeof original]) {
      modifiedFields.push(key)
    }
  }
  
  return {
    isBadCase: modifiedFields.length > 0,
    modifiedFields
  }
}

const confirmSubmit = async () => {
  showConfirmModal.value = false
  
  try {
    // 移除 suspicious_fields 避免後端 DB Model 不認識這個欄位
    const { suspicious_fields, ...submitData } = ocrData.value
    
    // 自動判定是否為 Bad Case (有任何手動修改)
    const { isBadCase, modifiedFields } = checkIsBadCase()

    const payload = {
      data: submitData,
      is_bad_case: isBadCase,
      ai_raw_output: isBadCase ? aiRawData.value : null,
      image_base64: isBadCase ? imageBase64.value : null,
      modified_fields: isBadCase ? modifiedFields : null
    }

    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
    const response = await fetch(`${API_BASE}/api/save_bl`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error('API 回應錯誤')
    }

    alert(`資料已成功寫入資料庫！ (已從 SQLite 紀錄)\n${isBadCase ? '✅ 已自動抓取 Bad Case 回傳供未來訓練' : '未發生人工修改，完美命中！'}`)
    blStore.reset()
  } catch (error) {
    console.error('寫入失敗:', error)
    alert('寫入失敗，請確認後端是否正常運作中')
  }
}
</script>

<template>
  <div v-if="isUploading" class="flex flex-col items-center justify-center py-12 text-zinc-400">
    <LucideLoader2 class="w-8 h-8 animate-spin text-emerald-500 mb-4" />
    <p>AI 視覺引擎正在解析單據中...</p>
  </div>

  <div v-else class="space-y-6 animate-in fade-in duration-500">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-medium text-white flex items-center gap-2">
        單據資料編輯
      </h3>

      <!-- 如果是 AI 解析，顯示紅綠燈。如果是手動輸入，顯示提示 -->
      <div v-if="isAiParsed" class="px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5"
        :class="isConfident ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'">
        <LucideCheckCircle2 v-if="isConfident" class="w-3.5 h-3.5" />
        <LucideAlertTriangle v-else class="w-3.5 h-3.5" />
        AI 信心度: {{ ocrData.confidence_score }}%
      </div>
      <div v-else
        class="px-3 py-1 rounded-full text-xs font-medium bg-zinc-800 text-zinc-400 border border-zinc-700 flex items-center gap-1.5">
        手動建檔模式
      </div>
    </div>

    <!-- Alert Box for Low Confidence -->
    <div v-if="isAiParsed && !isConfident"
      class="p-3.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-start gap-3">
      <LucideAlertTriangle class="w-5 h-5 flex-shrink-0 mt-0.5" />
      <p>AI 認為此文件部分欄位模糊或無法確信，請務必比對右側原圖，修正紅框處欄位。</p>
    </div>

    <!-- Form Fields -->
    <div class="space-y-4">
      <div class="grid gap-2 relative">
        <label class="text-sm font-medium text-zinc-400">提單號碼 (B/L Number)</label>
        <input v-model="ocrData.bl_number" type="text"
          class="w-full bg-zinc-950 border rounded-md px-3 py-2 text-zinc-100 focus:outline-none focus:ring-2 transition-all"
          :class="isSuspicious('bl_number') ? 'border-red-500 focus:ring-red-500/50 bg-red-500/5' : 'border-zinc-800 focus:ring-emerald-500/50'" />
        <div v-if="isSuspicious('bl_number')"
          class="absolute top-0 right-0 mt-1 text-[10px] text-red-500 font-bold tracking-wider">AI UNCERTAIN</div>
      </div>

      <div class="grid gap-2 relative">
        <label class="text-sm font-medium text-zinc-400">託運人 (Shipper)</label>
        <textarea v-model="ocrData.shipper" rows="2"
          class="w-full bg-zinc-950 border rounded-md px-3 py-2 text-zinc-100 focus:outline-none focus:ring-2 transition-all resize-none"
          :class="isSuspicious('shipper') ? 'border-red-500 focus:ring-red-500/50 bg-red-500/5' : 'border-zinc-800 focus:ring-emerald-500/50'"></textarea>
        <div v-if="isSuspicious('shipper')"
          class="absolute top-0 right-0 mt-1 text-[10px] text-red-500 font-bold tracking-wider">AI UNCERTAIN</div>
      </div>

      <div class="grid gap-2 relative">
        <label class="text-sm font-medium text-zinc-400">收貨人 (Consignee)</label>
        <textarea v-model="ocrData.consignee" rows="2"
          class="w-full bg-zinc-950 border rounded-md px-3 py-2 text-zinc-100 focus:outline-none focus:ring-2 transition-all resize-none"
          :class="isSuspicious('consignee') ? 'border-red-500 focus:ring-red-500/50 bg-red-500/5' : 'border-zinc-800 focus:ring-emerald-500/50'"></textarea>
        <div v-if="isSuspicious('consignee')"
          class="absolute top-0 right-0 mt-1 text-[10px] text-red-500 font-bold tracking-wider">AI UNCERTAIN</div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="grid gap-2 relative">
          <label class="text-sm font-medium text-zinc-400">目的地 (Destination)</label>
          <input v-model="ocrData.destination" type="text"
            class="w-full bg-zinc-950 border rounded-md px-3 py-2 text-zinc-100 focus:outline-none focus:ring-2 transition-all"
            :class="isSuspicious('destination') ? 'border-red-500 focus:ring-red-500/50 bg-red-500/5' : 'border-zinc-800 focus:ring-emerald-500/50'" />
          <div v-if="isSuspicious('destination')"
            class="absolute top-0 right-0 mt-1 text-[10px] text-red-500 font-bold tracking-wider">AI UNCERTAIN</div>
        </div>
        <div class="grid gap-2 relative">
          <label class="text-sm font-medium text-zinc-400">總重 (Gross Weight KGS)</label>
          <input v-model.number="ocrData.gross_weight" type="number"
            class="w-full bg-zinc-950 border rounded-md px-3 py-2 text-zinc-100 focus:outline-none focus:ring-2 transition-all"
            :class="isSuspicious('gross_weight') ? 'border-red-500 focus:ring-red-500/50 bg-red-500/5' : 'border-zinc-800 focus:ring-emerald-500/50'" />
          <div v-if="isSuspicious('gross_weight')"
            class="absolute top-0 right-0 mt-1 text-[10px] text-red-500 font-bold tracking-wider">AI UNCERTAIN</div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="grid gap-2 relative">
          <label class="text-sm font-medium text-zinc-400">體積 (Volume CBM)</label>
          <input v-model.number="ocrData.volume" type="number"
            class="w-full bg-zinc-950 border rounded-md px-3 py-2 text-zinc-100 focus:outline-none focus:ring-2 transition-all"
            :class="isSuspicious('volume') ? 'border-red-500 focus:ring-red-500/50 bg-red-500/5' : 'border-zinc-800 focus:ring-emerald-500/50'" />
          <div v-if="isSuspicious('volume')"
            class="absolute top-0 right-0 mt-1 text-[10px] text-red-500 font-bold tracking-wider">AI UNCERTAIN</div>
        </div>
        <div class="grid gap-2 relative">
          <label class="text-sm font-medium text-zinc-400">裝船日 (On Board Date)</label>
          <input v-model="ocrData.on_board_date" type="date"
            class="w-full bg-zinc-950 border rounded-md px-3 py-2 text-zinc-100 focus:outline-none focus:ring-2 transition-all [color-scheme:dark]"
            :class="isSuspicious('on_board_date') ? 'border-red-500 focus:ring-red-500/50 bg-red-500/5' : 'border-zinc-800 focus:ring-emerald-500/50'" />
          <div v-if="isSuspicious('on_board_date')"
            class="absolute top-0 right-0 mt-1 text-[10px] text-red-500 font-bold tracking-wider">AI UNCERTAIN</div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="pt-4 border-t border-zinc-800/60 flex justify-end gap-3">
      <button @click="blStore.reset()"
        class="px-4 py-2 rounded-md bg-zinc-800 text-zinc-200 text-sm font-medium hover:bg-zinc-700 transition-colors">
        取消重傳
      </button>
      <button @click="attemptSubmit"
        class="px-4 py-2 rounded-md text-zinc-950 text-sm font-bold shadow-lg transition-colors flex items-center gap-2"
        :class="isConfident ? 'bg-emerald-500 hover:bg-emerald-400 shadow-emerald-500/20' : 'bg-red-500 text-white hover:bg-red-400 shadow-red-500/20'">
        <LucideCheckCircle2 class="w-4 h-4" />
        準備寫入資料庫
      </button>
    </div>

    <!-- Confirm Modal -->
    <div v-if="showConfirmModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        class="bg-zinc-900 border border-zinc-800 rounded-xl shadow-2xl max-w-md w-full p-6 animate-in zoom-in-95 duration-200">
        <div class="flex items-start gap-4">
          <div
            class="w-10 h-10 rounded-full bg-amber-500/10 flex items-center justify-center flex-shrink-0 mt-1 text-amber-500">
            <LucideAlertTriangle class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-white mb-2">人工覆核確認</h3>
            <p class="text-sm text-zinc-400 leading-relaxed mb-6">
              AI 解析僅供輔助，請確認您已與右側「原圖」進行交叉比對，特別是 <span class="text-red-400 font-semibold">紅色標記 (AI UNCERTAIN)</span>
              的欄位。確認無誤後，資料將正式寫入資料庫。
            </p>
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <button @click="showConfirmModal = false"
            class="px-4 py-2 rounded-md bg-zinc-800 text-zinc-200 text-sm font-medium hover:bg-zinc-700 transition-colors">
            返回檢查
          </button>
          <button @click="confirmSubmit"
            class="px-4 py-2 rounded-md bg-emerald-500 text-zinc-950 text-sm font-bold hover:bg-emerald-400 transition-colors shadow-lg shadow-emerald-500/20 flex items-center gap-2">
            <LucideCheckCircle2 class="w-4 h-4" />
            我已確認無誤，寫入
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
