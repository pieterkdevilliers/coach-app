<script setup lang="ts">
const route = useRoute()
const { apiFetch } = useAuthFetch()
const callId = route.params.id as string

interface ActionStep {
  id: string
  description: string
  isComplete: boolean
  sortOrder: number
  createdAt: string
}

interface Call {
  id: string
  clientId: string
  callTypeId: string
  title: string
  calledAt: string
  durationSeconds: number | null
  notes: string | null
  status: string
  recording: { id: string; fileName: string; s3Key: string | null } | null
  transcript: { id: string; content: string; wordCount: number | null; updatedAt: string } | null
  summary: { id: string; content: string; updatedAt: string } | null
  actionSteps: ActionStep[]
}

const call = ref<Call | null>(null)
const loading = ref(true)
const error = ref('')

const transcriptDraft = ref('')
const editingTranscript = ref(false)
const savingTranscript = ref(false)

const summaryDraft = ref('')
const editingSummary = ref(false)
const savingSummary = ref(false)

const newStep = ref('')
const addingStep = ref(false)

const showDeleteCall = ref(false)
const deletingCall = ref(false)

// Recording upload
const fileInput = ref<HTMLInputElement | null>(null)
const uploadProgress = ref(0)
const uploadState = ref<'idle' | 'uploading' | 'confirming' | 'done' | 'error'>('idle')
const uploadError = ref('')

async function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return

  uploadError.value = ''
  uploadState.value = 'uploading'
  uploadProgress.value = 0

  try {
    // Step 1 — get pre-signed PUT URL from backend
    const { uploadUrl, s3Key } = await apiFetch<{ uploadUrl: string; s3Key: string }>(
      `/api/calls/${callId}/recording/presign`,
      { method: 'POST', body: { file_name: file.name, content_type: file.type || 'application/octet-stream' } }
    )

    // Step 2 — PUT directly to S3 (XHR for progress tracking)
    await new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('PUT', uploadUrl)
      xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream')
      xhr.upload.onprogress = (ev) => {
        if (ev.lengthComputable) uploadProgress.value = Math.round((ev.loaded / ev.total) * 100)
      }
      xhr.onload = () => (xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`S3 upload failed: ${xhr.status}`)))
      xhr.onerror = () => reject(new Error('Network error during S3 upload'))
      xhr.send(file)
    })

    uploadState.value = 'confirming'

    // Step 3 — confirm with backend, get presigned read URL
    const confirmed = await apiFetch<{ fileName: string; s3Key: string; presignedReadUrl: string }>(
      `/api/calls/${callId}/recording/confirm`,
      { method: 'POST', body: { s3_key: s3Key, file_name: file.name } }
    )

    call.value!.recording = { id: '', fileName: confirmed.fileName, s3Key: confirmed.s3Key }
    uploadState.value = 'done'
  } catch (err: unknown) {
    uploadError.value = (err as { data?: { detail?: string }; message?: string })?.data?.detail
      ?? (err as Error)?.message
      ?? 'Upload failed'
    uploadState.value = 'error'
  } finally {
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function removeRecording() {
  await apiFetch(`/api/calls/${callId}/recording`, { method: 'DELETE' })
  call.value!.recording = null
  uploadState.value = 'idle'
  uploadProgress.value = 0
}

onMounted(async () => {
  try {
    call.value = await apiFetch<Call>(`/api/calls/${callId}`)
  } catch {
    error.value = 'Call not found'
  } finally {
    loading.value = false
  }
})

// Transcript
function startEditTranscript() {
  transcriptDraft.value = call.value?.transcript?.content ?? ''
  editingTranscript.value = true
}

async function saveTranscript() {
  savingTranscript.value = true
  try {
    const updated = await apiFetch<{ content: string; wordCount: number | null; updatedAt: string; id: string }>(
      `/api/calls/${callId}/transcript`,
      { method: 'PUT', body: { content: transcriptDraft.value } }
    )
    call.value!.transcript = updated
    editingTranscript.value = false
  } finally {
    savingTranscript.value = false
  }
}

async function deleteTranscript() {
  await apiFetch(`/api/calls/${callId}/transcript`, { method: 'DELETE' })
  call.value!.transcript = null
}

// Summary
function startEditSummary() {
  summaryDraft.value = call.value?.summary?.content ?? ''
  editingSummary.value = true
}

async function saveSummary() {
  savingSummary.value = true
  try {
    const updated = await apiFetch<{ content: string; updatedAt: string; id: string }>(
      `/api/calls/${callId}/summary`,
      { method: 'PUT', body: { content: summaryDraft.value } }
    )
    call.value!.summary = updated
    editingSummary.value = false
  } finally {
    savingSummary.value = false
  }
}

async function deleteSummary() {
  await apiFetch(`/api/calls/${callId}/summary`, { method: 'DELETE' })
  call.value!.summary = null
}

// Action steps
async function addStep() {
  if (!newStep.value.trim()) return
  addingStep.value = true
  try {
    const step = await apiFetch<ActionStep>(`/api/calls/${callId}/action-steps`, {
      method: 'POST',
      body: { description: newStep.value.trim() },
    })
    call.value!.actionSteps.push(step)
    newStep.value = ''
  } finally {
    addingStep.value = false
  }
}

async function toggleStep(step: ActionStep) {
  const updated = await apiFetch<ActionStep>(
    `/api/calls/${callId}/action-steps/${step.id}`,
    { method: 'PUT', body: { is_complete: !step.isComplete } }
  )
  const idx = call.value!.actionSteps.findIndex((s) => s.id === step.id)
  if (idx !== -1) call.value!.actionSteps[idx] = updated
}

async function deleteStep(stepId: string) {
  await apiFetch(`/api/calls/${callId}/action-steps/${stepId}`, { method: 'DELETE' })
  call.value!.actionSteps = call.value!.actionSteps.filter((s) => s.id !== stepId)
}

// Delete call
async function confirmDeleteCall() {
  deletingCall.value = true
  try {
    await apiFetch(`/api/calls/${callId}`, { method: 'DELETE' })
    await navigateTo(`/clients/${call.value?.clientId}`)
  } catch {
    deletingCall.value = false
    showDeleteCall.value = false
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    weekday: 'short', day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

const completedSteps = computed(() =>
  call.value?.actionSteps.filter((s) => s.isComplete).length ?? 0
)
</script>

<template>
  <div class="p-6">
    <p v-if="loading" class="text-sm text-gray-400">Loading…</p>
    <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>

    <template v-else-if="call">
      <!-- Header -->
      <div class="mb-6 flex items-start justify-between">
        <div>
          <NuxtLink
            :to="`/clients/${call.clientId}`"
            class="mb-1 inline-block text-sm text-blue-600 hover:underline"
          >
            ← Back to client
          </NuxtLink>
          <h1 class="text-2xl font-bold">{{ call.title }}</h1>
          <p class="mt-0.5 text-sm text-gray-500">{{ formatDate(call.calledAt) }}</p>
        </div>
        <div class="flex gap-2">
          <NuxtLink
            :to="`/calls/${callId}/edit`"
            class="rounded border px-3 py-1.5 text-sm hover:bg-gray-50"
          >
            Edit
          </NuxtLink>
          <button
            class="rounded border border-red-200 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
            @click="showDeleteCall = true"
          >
            Delete
          </button>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="call.notes" class="mb-6 rounded-lg border p-4 text-sm">
        <p class="mb-1 font-medium text-gray-500">Notes</p>
        <p class="whitespace-pre-wrap">{{ call.notes }}</p>
      </div>

      <!-- Recording -->
      <section class="mb-6">
        <h2 class="mb-3 text-lg font-semibold">Recording</h2>

        <!-- Already uploaded -->
        <div v-if="call.recording" class="flex items-center justify-between rounded-lg border p-4 text-sm">
          <span class="font-medium">{{ call.recording.fileName }}</span>
          <button class="text-xs text-red-500 hover:underline" @click="removeRecording">
            Remove
          </button>
        </div>

        <!-- Upload UI -->
        <div v-else class="rounded-lg border p-5">
          <!-- Idle / pick file -->
          <div v-if="uploadState === 'idle' || uploadState === 'error'" class="text-center">
            <p class="mb-3 text-sm text-gray-500">Audio or video file — uploaded directly to S3, bypassing Cloudflare.</p>
            <label class="inline-block cursor-pointer rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
              Choose file
              <input
                ref="fileInput"
                type="file"
                accept="audio/*,video/*"
                class="hidden"
                @change="handleFileChange"
              />
            </label>
            <p v-if="uploadError" class="mt-2 text-xs text-red-600">{{ uploadError }}</p>
          </div>

          <!-- Uploading to S3 -->
          <div v-else-if="uploadState === 'uploading'" class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Uploading to S3…</span>
              <span class="font-medium">{{ uploadProgress }}%</span>
            </div>
            <div class="h-2 w-full overflow-hidden rounded-full bg-gray-100">
              <div
                class="h-full rounded-full bg-blue-600 transition-all"
                :style="{ width: `${uploadProgress}%` }"
              />
            </div>
          </div>

          <!-- Confirming with backend -->
          <p v-else-if="uploadState === 'confirming'" class="text-center text-sm text-gray-500">
            Saving recording…
          </p>
        </div>
      </section>

      <!-- Transcript -->
      <section class="mb-6">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold">Transcript</h2>
          <div class="flex gap-2">
            <button
              v-if="!editingTranscript"
              class="rounded border px-3 py-1 text-xs hover:bg-gray-50"
              @click="startEditTranscript"
            >
              {{ call.transcript ? 'Edit' : 'Add' }}
            </button>
            <button
              v-if="call.transcript && !editingTranscript"
              class="rounded border border-red-200 px-3 py-1 text-xs text-red-600 hover:bg-red-50"
              @click="deleteTranscript"
            >
              Delete
            </button>
          </div>
        </div>

        <div v-if="editingTranscript" class="space-y-2">
          <textarea
            v-model="transcriptDraft"
            rows="10"
            class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div class="flex gap-2">
            <button
              :disabled="savingTranscript"
              class="rounded bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              @click="saveTranscript"
            >
              {{ savingTranscript ? 'Saving…' : 'Save' }}
            </button>
            <button
              class="rounded border px-4 py-1.5 text-sm hover:bg-gray-50"
              @click="editingTranscript = false"
            >
              Cancel
            </button>
          </div>
        </div>
        <div v-else-if="call.transcript" class="rounded-lg border p-4">
          <p class="mb-2 whitespace-pre-wrap text-sm">{{ call.transcript.content }}</p>
          <p v-if="call.transcript.wordCount" class="text-xs text-gray-400">
            {{ call.transcript.wordCount.toLocaleString() }} words
          </p>
        </div>
        <p v-else class="text-sm text-gray-400">No transcript yet.</p>
      </section>

      <!-- Summary -->
      <section class="mb-6">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold">Summary</h2>
          <div class="flex gap-2">
            <button
              v-if="!editingSummary"
              class="rounded border px-3 py-1 text-xs hover:bg-gray-50"
              @click="startEditSummary"
            >
              {{ call.summary ? 'Edit' : 'Add' }}
            </button>
            <button
              v-if="call.summary && !editingSummary"
              class="rounded border border-red-200 px-3 py-1 text-xs text-red-600 hover:bg-red-50"
              @click="deleteSummary"
            >
              Delete
            </button>
          </div>
        </div>

        <div v-if="editingSummary" class="space-y-2">
          <textarea
            v-model="summaryDraft"
            rows="6"
            class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div class="flex gap-2">
            <button
              :disabled="savingSummary"
              class="rounded bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              @click="saveSummary"
            >
              {{ savingSummary ? 'Saving…' : 'Save' }}
            </button>
            <button
              class="rounded border px-4 py-1.5 text-sm hover:bg-gray-50"
              @click="editingSummary = false"
            >
              Cancel
            </button>
          </div>
        </div>
        <p v-else-if="call.summary" class="whitespace-pre-wrap rounded-lg border p-4 text-sm">
          {{ call.summary.content }}
        </p>
        <p v-else class="text-sm text-gray-400">No summary yet.</p>
      </section>

      <!-- Action Steps -->
      <section class="mb-6">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold">Next Action Steps</h2>
          <span v-if="call.actionSteps.length" class="text-xs text-gray-400">
            {{ completedSteps }} / {{ call.actionSteps.length }} complete
          </span>
        </div>

        <ul class="mb-3 space-y-2">
          <li
            v-for="step in call.actionSteps"
            :key="step.id"
            class="flex items-start gap-3 rounded-lg border px-4 py-3 text-sm"
          >
            <input
              type="checkbox"
              :checked="step.isComplete"
              class="mt-0.5 h-4 w-4 cursor-pointer rounded"
              @change="toggleStep(step)"
            />
            <span
              class="flex-1"
              :class="step.isComplete ? 'text-gray-400 line-through' : ''"
            >
              {{ step.description }}
            </span>
            <button
              class="shrink-0 text-xs text-red-400 hover:text-red-600"
              @click="deleteStep(step.id)"
            >
              Delete
            </button>
          </li>
        </ul>

        <form class="flex gap-2" @submit.prevent="addStep">
          <input
            v-model="newStep"
            type="text"
            placeholder="Add an action step…"
            class="flex-1 rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            :disabled="addingStep || !newStep.trim()"
            class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Add
          </button>
        </form>
      </section>

      <ConfirmDialog
        v-model="showDeleteCall"
        title="Delete call"
        :message="`Are you sure you want to delete '${call.title}'? This will also remove the transcript, summary and action steps.`"
        confirm-label="Delete"
        :loading="deletingCall"
        @confirm="confirmDeleteCall"
      />
    </template>
  </div>
</template>
