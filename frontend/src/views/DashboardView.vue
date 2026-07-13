<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DashboardLayout from '@/components/layout/DashboardLayout.vue'
import { LucideTable, LucideDatabaseBackup, LucideRefreshCcw } from '@lucide/vue'

const activeTab = ref('bl_list')
const blList = ref<any[]>([])
const badCases = ref<any[]>([])
const isLoading = ref(true)

const fetchData = async () => {
  isLoading.value = true
  try {
    const [blRes, bcRes] = await Promise.all([
      fetch('http://127.0.0.1:8000/api/bl_list'),
      fetch('http://127.0.0.1:8000/api/bad_cases')
    ])
    blList.value = await blRes.json()
    badCases.value = await bcRes.json()
  } catch (error) {
    console.error('Failed to fetch DB data', error)
  } finally {
    isLoading.value = false
  }
}

const parseModifiedFields = (jsonStr: string) => {
  if (!jsonStr) return []
  try {
    return JSON.parse(jsonStr)
  } catch (e) {
    return []
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <DashboardLayout hide-right-sidebar>
    <template #center>
      <div class="w-full max-w-[1600px] mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-12">
        <div class="flex items-center justify-between">
          <div class="flex gap-4">
            <button 
              @click="activeTab = 'bl_list'"
              class="px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2"
              :class="activeTab === 'bl_list' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'text-zinc-400 hover:bg-zinc-800/50'"
            >
              <LucideTable class="w-4 h-4" />
              提單總表庫 (B/L)
            </button>
            <button 
              @click="activeTab = 'bad_cases'"
              class="px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2"
              :class="activeTab === 'bad_cases' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' : 'text-zinc-400 hover:bg-zinc-800/50'"
            >
              <LucideDatabaseBackup class="w-4 h-4" />
              Bad Case 收集庫
            </button>
          </div>
          <button @click="fetchData" class="p-2 text-zinc-400 hover:text-emerald-400 transition-colors" title="重新整理">
            <LucideRefreshCcw class="w-5 h-5" :class="{'animate-spin text-emerald-400': isLoading}" />
          </button>
        </div>

        <!-- 提單總表 -->
        <div v-if="activeTab === 'bl_list'" class="bg-zinc-900/50 border border-zinc-800/80 rounded-xl overflow-x-auto shadow-xl custom-scrollbar">
          <table class="w-full min-w-[1200px] text-left text-sm text-zinc-300">
            <thead class="bg-zinc-950 text-zinc-400 uppercase text-xs">
              <tr>
                <th class="px-6 py-4 font-semibold whitespace-nowrap">ID</th>
                <th class="px-6 py-4 font-semibold whitespace-nowrap">提單號碼</th>
                <th class="px-6 py-4 font-semibold">託運人</th>
                <th class="px-6 py-4 font-semibold">收貨人</th>
                <th class="px-6 py-4 font-semibold">目的地</th>
                <th class="px-6 py-4 font-semibold whitespace-nowrap">體積 (CBM)</th>
                <th class="px-6 py-4 font-semibold whitespace-nowrap">運費</th>
                <th class="px-6 py-4 font-semibold whitespace-nowrap">總重</th>
                <th class="px-6 py-4 font-semibold whitespace-nowrap">裝船日</th>
                <th class="px-6 py-4 font-semibold whitespace-nowrap">AI 信心度</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-zinc-800/50">
              <tr v-for="bl in blList" :key="bl.id" class="hover:bg-zinc-800/20 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">{{ bl.id }}</td>
                <td class="px-6 py-4 text-emerald-400 font-medium whitespace-nowrap">{{ bl.bl_number }}</td>
                <td class="px-6 py-4 max-w-[300px] truncate" :title="bl.shipper">{{ bl.shipper }}</td>
                <td class="px-6 py-4 max-w-[300px] truncate" :title="bl.consignee">{{ bl.consignee }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ bl.destination }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ bl.volume }}</td>
                <td class="px-6 py-4 whitespace-nowrap">${{ bl.freight_cost }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ bl.gross_weight }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ bl.on_board_date }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 rounded-full text-xs font-bold" :class="bl.confidence_score >= 80 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'">
                    {{ bl.confidence_score }}%
                  </span>
                </td>
              </tr>
              <tr v-if="blList.length === 0">
                <td colspan="7" class="px-6 py-8 text-center text-zinc-500">尚無任何提單資料</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Bad Cases -->
        <div v-if="activeTab === 'bad_cases'" class="bg-zinc-900/50 border border-zinc-800/80 rounded-xl overflow-x-auto shadow-xl custom-scrollbar">
          <table class="w-full min-w-[1400px] text-left text-sm text-zinc-300">
            <thead class="bg-zinc-950 text-zinc-400 uppercase text-xs">
              <tr>
                <th class="px-6 py-4 font-semibold w-16 whitespace-nowrap">ID</th>
                <th class="px-6 py-4 font-semibold w-24 whitespace-nowrap">提單 ID</th>
                <th class="px-6 py-4 font-semibold w-48 whitespace-nowrap">修改欄位</th>
                <th class="px-6 py-4 font-semibold w-32 whitespace-nowrap">原始圖片</th>
                <th class="px-6 py-4 font-semibold w-[400px]">AI 原始輸出 (Raw)</th>
                <th class="px-6 py-4 font-semibold w-[400px]">OP 修正輸出 (Corrected)</th>
                <th class="px-6 py-4 font-semibold w-32 whitespace-nowrap">建立時間</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-zinc-800/50">
              <tr v-for="bc in badCases" :key="bc.id" class="hover:bg-zinc-800/20 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">{{ bc.id }}</td>
                <td class="px-6 py-4 text-amber-400 font-medium whitespace-nowrap">#{{ bc.bl_id }}</td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap gap-1">
                    <template v-if="parseModifiedFields(bc.modified_fields).length > 0">
                      <span v-for="field in parseModifiedFields(bc.modified_fields)" :key="field" class="px-2 py-0.5 rounded text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        {{ field }}
                      </span>
                    </template>
                    <span v-else class="text-zinc-500 text-[10px]">無紀錄</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="w-20 h-20 rounded border border-zinc-700 bg-zinc-950 overflow-hidden relative group">
                    <img v-if="bc.image_base64" :src="'data:image/jpeg;base64,' + bc.image_base64" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110" title="原始提單圖片" />
                    <div v-else class="w-full h-full flex items-center justify-center text-zinc-600 text-[10px]">無圖檔</div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <pre class="text-[11px] text-zinc-500 bg-zinc-950 p-3 rounded-lg max-h-40 max-w-[350px] lg:max-w-[450px] overflow-y-auto overflow-x-auto border border-zinc-800 whitespace-pre custom-scrollbar">{{ bc.ai_raw_output }}</pre>
                </td>
                <td class="px-6 py-4">
                  <pre class="text-[11px] text-amber-500/80 bg-zinc-950 p-3 rounded-lg max-h-40 max-w-[350px] lg:max-w-[450px] overflow-y-auto overflow-x-auto border border-amber-900/30 whitespace-pre custom-scrollbar">{{ bc.human_corrected_output }}</pre>
                </td>
                <td class="px-6 py-4 text-[10px] text-zinc-500 whitespace-nowrap">{{ new Date(bc.created_at).toLocaleString() }}</td>
              </tr>
              <tr v-if="badCases.length === 0">
                <td colspan="6" class="px-6 py-8 text-center text-zinc-500">尚無任何 Bad Case 資料</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </DashboardLayout>
</template>
