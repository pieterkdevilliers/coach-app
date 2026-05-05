<script setup lang="ts">
const { apiFetch } = useAuthFetch()

interface CallType {
  id: string
  name: string
  description: string | null
  promptTemplate: string
  isActive: boolean
}

const callTypes = ref<CallType[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const editingId = ref<string | null>(null)
const showForm = ref(false)

const form = reactive({
  name: '',
  description: '',
  promptTemplate: '',
})

const showDeleteDialog = ref(false)
const deletingId = ref<string | null>(null)
const deleting = ref(false)

onMounted(async () => {
  try {
    callTypes.value = await apiFetch<CallType[]>('/api/call-types')
  } catch {
    error.value = 'Failed to load call types'
  } finally {
    loading.value = false
  }
})

function openCreate() {
  editingId.value = null
  form.name = ''
  form.description = ''
  form.promptTemplate = ''
  showForm.value = true
}

function openEdit(ct: CallType) {
  editingId.value = ct.id
  form.name = ct.name
  form.description = ct.description ?? ''
  form.promptTemplate = ct.promptTemplate
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
  error.value = ''
}

async function save() {
  error.value = ''
  saving.value = true
  try {
    const body = {
      name: form.name,
      description: form.description || null,
      prompt_template: form.promptTemplate,
    }
    if (editingId.value) {
      const updated = await apiFetch<CallType>(`/api/call-types/${editingId.value}`, {
        method: 'PUT',
        body,
      })
      const idx = callTypes.value.findIndex((c) => c.id === editingId.value)
      if (idx !== -1) callTypes.value[idx] = updated
    } else {
      const created = await apiFetch<CallType>('/api/call-types', {
        method: 'POST',
        body,
      })
      callTypes.value.push(created)
      callTypes.value.sort((a, b) => a.name.localeCompare(b.name))
    }
    cancelForm()
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to save'
  } finally {
    saving.value = false
  }
}

function confirmDelete(id: string) {
  deletingId.value = id
  showDeleteDialog.value = true
}

async function doDelete() {
  if (!deletingId.value) return
  deleting.value = true
  try {
    await apiFetch(`/api/call-types/${deletingId.value}`, { method: 'DELETE' })
    callTypes.value = callTypes.value.filter((c) => c.id !== deletingId.value)
    showDeleteDialog.value = false
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to delete'
    showDeleteDialog.value = false
  } finally {
    deleting.value = false
    deletingId.value = null
  }
}

const deletingName = computed(
  () => callTypes.value.find((c) => c.id === deletingId.value)?.name ?? ''
)
</script>

<template>
  <div class="p-6">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Call Types</h1>
      <button
        v-if="!showForm"
        class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        @click="openCreate"
      >
        New Call Type
      </button>
    </div>

    <!-- Create / edit form -->
    <div v-if="showForm" class="mb-6 rounded-lg border p-5">
      <h2 class="mb-4 text-base font-semibold">
        {{ editingId ? 'Edit Call Type' : 'New Call Type' }}
      </h2>
      <form class="space-y-4" @submit.prevent="save">
        <div>
          <label class="mb-1 block text-sm font-medium">Name <span class="text-red-500">*</span></label>
          <input
            v-model="form.name"
            type="text"
            required
            class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Description</label>
          <input
            v-model="form.description"
            type="text"
            class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Prompt Template <span class="text-red-500">*</span></label>
          <textarea
            v-model="form.promptTemplate"
            rows="6"
            required
            class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <div class="flex gap-2">
          <button
            type="submit"
            :disabled="saving"
            class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
          <button
            type="button"
            class="rounded border px-4 py-2 text-sm font-medium hover:bg-gray-50"
            @click="cancelForm"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- List -->
    <p v-if="loading" class="text-sm text-gray-400">Loading…</p>
    <p v-else-if="!showForm && callTypes.length === 0" class="text-sm text-gray-400">
      No call types yet.
    </p>

    <div v-else-if="callTypes.length" class="space-y-3">
      <div
        v-for="ct in callTypes"
        :key="ct.id"
        class="rounded-lg border p-4"
        :class="editingId === ct.id ? 'border-blue-300 bg-blue-50' : ''"
      >
        <div class="mb-1 flex items-start justify-between gap-4">
          <div>
            <p class="font-medium">{{ ct.name }}</p>
            <p v-if="ct.description" class="text-sm text-gray-500">{{ ct.description }}</p>
          </div>
          <div class="flex shrink-0 gap-2">
            <button
              class="rounded border px-3 py-1 text-xs hover:bg-gray-50"
              @click="openEdit(ct)"
            >
              Edit
            </button>
            <button
              class="rounded border border-red-200 px-3 py-1 text-xs text-red-600 hover:bg-red-50"
              @click="confirmDelete(ct.id)"
            >
              Delete
            </button>
          </div>
        </div>
        <p class="mt-2 line-clamp-2 text-xs text-gray-400">{{ ct.promptTemplate }}</p>
      </div>
    </div>

    <ConfirmDialog
      v-model="showDeleteDialog"
      title="Delete call type"
      :message="`Are you sure you want to delete '${deletingName}'? This cannot be undone.`"
      confirm-label="Delete"
      :loading="deleting"
      @confirm="doDelete"
    />
  </div>
</template>
