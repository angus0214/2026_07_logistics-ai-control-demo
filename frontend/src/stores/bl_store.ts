import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface OcrResult {
  bl_number: string
  shipper: string
  consignee: string
  destination: string
  gross_weight: number
  volume: number
  eta: string
  confidence_score: number
  suspicious_fields: string[]
}

export const useBlStore = defineStore('bl', () => {
  const getEmptyData = (): OcrResult => ({
    bl_number: '', shipper: '', consignee: '', destination: '', gross_weight: 0, volume: 0, eta: '', confidence_score: 100, suspicious_fields: []
  })

  const ocrData = ref<OcrResult>(getEmptyData())
  const aiRawData = ref<OcrResult | null>(null) // 儲存最原始的 AI 答案
  const previewUrl = ref<string | null>(null)
  const imageBase64 = ref<string | null>(null) // 用於回報 Bad Case
  const isUploading = ref(false)
  const isAiParsed = ref(false)

  const setOcrData = (data: OcrResult) => {
    ocrData.value = { ...data }
    aiRawData.value = JSON.parse(JSON.stringify(data)) // Deep copy
    isAiParsed.value = true
  }

  const setPreviewUrl = (url: string) => {
    previewUrl.value = url
  }

  const setImageBase64 = (base64: string) => {
    imageBase64.value = base64
  }

  const setUploading = (status: boolean) => {
    isUploading.value = status
  }

  const reset = () => {
    ocrData.value = getEmptyData()
    aiRawData.value = null
    previewUrl.value = null
    imageBase64.value = null
    isUploading.value = false
    isAiParsed.value = false
  }

  return {
    ocrData,
    aiRawData,
    previewUrl,
    imageBase64,
    isUploading,
    isAiParsed,
    setOcrData,
    setPreviewUrl,
    setImageBase64,
    setUploading,
    reset
  }
})
