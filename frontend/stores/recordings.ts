import { defineStore } from 'pinia'

export type RecordingStatus = 'pending' | 'processing' | 'complete' | 'failed'

export interface Recording {
  id: string
  callTypeId: string
  title: string
  clientName: string | null
  recordedAt: string | null
  fileName: string
  filePath: string
  durationSeconds: number | null
  status: RecordingStatus
  scribeJobId: string | null
  errorMessage: string | null
  createdAt: string
  updatedAt: string
}

export const useRecordingsStore = defineStore('recordings', () => {
  const recordings = ref<Recording[]>([])
  const current = ref<Recording | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  async function fetchRecordings() {
    loading.value = true
    error.value = null
    try {
      const data = await $fetch<Recording[]>(`${apiBase}/api/recordings`)
      recordings.value = data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load recordings'
    } finally {
      loading.value = false
    }
  }

  async function fetchRecording(id: string) {
    loading.value = true
    error.value = null
    try {
      current.value = await $fetch<Recording>(`${apiBase}/api/recordings/${id}`)
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load recording'
    } finally {
      loading.value = false
    }
  }

  return { recordings, current, loading, error, fetchRecordings, fetchRecording }
})
