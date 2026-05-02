import { defineStore } from 'pinia'

export interface CallType {
  id: string
  name: string
  description: string | null
  promptTemplate: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export const useCallTypesStore = defineStore('callTypes', () => {
  const callTypes = ref<CallType[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  async function fetchCallTypes() {
    loading.value = true
    error.value = null
    try {
      const data = await $fetch<CallType[]>(`${apiBase}/api/call-types`)
      callTypes.value = data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load call types'
    } finally {
      loading.value = false
    }
  }

  return { callTypes, loading, error, fetchCallTypes }
})
