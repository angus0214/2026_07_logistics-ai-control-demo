<script setup lang="ts">
import DashboardLayout from '@/components/layout/DashboardLayout.vue'
import FileUploadZone from '@/components/ui/FileUploadZone.vue'
import BillOfLadingForm from '@/components/ui/BillOfLadingForm.vue'
import ZoomableImage from '@/components/ui/ZoomableImage.vue'
import { useBlStore } from '@/stores/bl_store'
import { storeToRefs } from 'pinia'

const blStore = useBlStore()
const { ocrData, previewUrl, isUploading } = storeToRefs(blStore)

const handleFileSelected = async (file: File) => {
  if (!file.type.startsWith('image/')) {
    alert('請上傳圖片檔')
    return
  }

  // 1. 產生預覽圖 URL 與 Base64 (供 Bad Case 使用)
  const objectUrl = URL.createObjectURL(file)
  blStore.setPreviewUrl(objectUrl)
  
  const reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onload = () => {
    const base64String = (reader.result as string).split(',')[1]
    blStore.setImageBase64(base64String)
  }
  
  // 2. 開始上傳與 OCR
  blStore.setUploading(true)
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    // 實務上這裡要串接後端 API
    const response = await fetch('http://127.0.0.1:8000/api/upload_bl', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) throw new Error('上傳失敗')
    
    const result = await response.json()
    blStore.setOcrData(result.data)
  } catch (error) {
    console.error(error)
    alert('解析失敗，請確認後端是否已啟動')
  } finally {
    blStore.setUploading(false)
  }
}
</script>

<template>
  <DashboardLayout>
    <template #center>
      <!-- 上傳區 (縮小一點放上方) -->
      <div class="mb-6 animate-in fade-in zoom-in-95 duration-300">
        <FileUploadZone @file-selected="handleFileSelected" />
      </div>

      <!-- 複雜表單區 (永遠顯示，讓 OP 可手動輸入) -->
      <div class="bg-zinc-900/80 border border-zinc-800/80 rounded-xl p-6 shadow-xl">
        <BillOfLadingForm />
      </div>
    </template>

    <template #right>
      <div v-if="previewUrl" class="w-full h-full p-4">
        <ZoomableImage :src="previewUrl" />
      </div>
    </template>
  </DashboardLayout>
</template>
