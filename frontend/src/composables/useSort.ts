import { ref, computed, type Ref } from 'vue'

export function useSort<T>(dataList: Ref<T[]>, initialSortKey: keyof T, initialSortOrder: 'asc' | 'desc' = 'asc') {
  const sortKey = ref<keyof T>(initialSortKey)
  const sortOrder = ref<'asc' | 'desc'>(initialSortOrder)

  const sortBy = (key: keyof T) => {
    if (sortKey.value === key) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey.value = key
      sortOrder.value = 'asc'
    }
  }

  const sortedData = computed(() => {
    return [...dataList.value].sort((a, b) => {
      const valA = a[sortKey.value as keyof T]
      const valB = b[sortKey.value as keyof T]

      if (valA === valB) return 0
      
      // Handle null/undefined
      if (valA == null) return sortOrder.value === 'asc' ? 1 : -1
      if (valB == null) return sortOrder.value === 'asc' ? -1 : 1

      // Handle numbers
      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortOrder.value === 'asc' ? valA - valB : valB - valA
      }

      // Handle strings
      const strA = String(valA).toLowerCase()
      const strB = String(valB).toLowerCase()
      if (strA < strB) return sortOrder.value === 'asc' ? -1 : 1
      if (strA > strB) return sortOrder.value === 'asc' ? 1 : -1
      
      return 0
    })
  })

  return {
    sortKey,
    sortOrder,
    sortBy,
    sortedData
  }
}
