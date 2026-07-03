import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface OcrResult {
  bl_number: string
  shipper: string
  consignee: string
  destination: string
  gross_weight: number
  eta: string
  confidence_score: number
  suspicious_fields: string[]
}

export const useBlStore = defineStore('bl', () => {
  const getEmptyData = (): OcrResult => ({
    bl_number: '', shipper: '', consignee: '', destination: '', gross_weight: 0, eta: '', confidence_score: 100, suspicious_fields: []
  })

  const ocrData = ref<OcrResult>(getEmptyData())
  const previewUrl = ref<string | null>(null)
  const isUploading = ref(false)
  const isAiParsed = ref(false)

  const setOcrData = (data: OcrResult) => {
    ocrData.value = data
    isAiParsed.value = true
  }

  const setPreviewUrl = (url: string) => {
    previewUrl.value = url
  }

  const setUploading = (status: boolean) => {
    isUploading.value = status
  }

  const reset = () => {
    ocrData.value = getEmptyData()
    previewUrl.value = null
    isUploading.value = false
    isAiParsed.value = false
  }

  return {
    ocrData,
    previewUrl,
    isUploading,
    isAiParsed,
    setOcrData,
    setPreviewUrl,
    setUploading,
    reset
  }
})
