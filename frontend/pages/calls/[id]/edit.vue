<script setup lang="ts">
const route = useRoute()
const { apiFetch } = useAuthFetch()
const callId = route.params.id as string

interface CallType { id: string; name: string }

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const callTypes = ref<CallType[]>([])

const form = reactive({
  title: '',
  callTypeId: '',
  calledAt: '',
  durationSeconds: '' as string | number,
  notes: '',
})

onMounted(async () => {
  try {
    const [call, cts] = await Promise.all([
      apiFetch<{ title: string; callTypeId: string; calledAt: string; durationSeconds: number | null; notes: string | null }>(
        `/api/calls/${callId}`
      ),
      apiFetch<CallType[]>('/api/call-types'),
    ])
    form.title = call.title
    form.callTypeId = call.callTypeId
    form.calledAt = call.calledAt.slice(0, 16) // datetime-local format
    form.durationSeconds = call.durationSeconds ?? ''
    form.notes = call.notes ?? ''
    callTypes.value = cts
  } catch {
    error.value = 'Failed to load call'
  } finally {
    loading.value = false
  }
})

async function save() {
  error.value = ''
  saving.value = true
  try {
    await apiFetch(`/api/calls/${callId}`, {
      method: 'PUT',
      body: {
        title: form.title,
        call_type_id: form.callTypeId,
        called_at: new Date(form.calledAt).toISOString(),
        duration_seconds: form.durationSeconds ? Number(form.durationSeconds) : null,
        notes: form.notes || null,
      },
    })
    await navigateTo(`/calls/${callId}`)
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to save'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-xl p-6">
    <NuxtLink :to="`/calls/${callId}`" class="mb-4 inline-block text-sm text-blue-600 hover:underline">
      ← Back to call
    </NuxtLink>
    <h1 class="mb-6 text-2xl font-bold">Edit Call</h1>

    <p v-if="loading" class="text-sm text-gray-400">Loading…</p>

    <form v-else class="space-y-4" @submit.prevent="save">
      <div>
        <label class="mb-1 block text-sm font-medium">Title <span class="text-red-500">*</span></label>
        <input
          v-model="form.title"
          type="text"
          required
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Call Type <span class="text-red-500">*</span></label>
        <select
          v-model="form.callTypeId"
          required
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option v-for="ct in callTypes" :key="ct.id" :value="ct.id">{{ ct.name }}</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Date & Time <span class="text-red-500">*</span></label>
        <input
          v-model="form.calledAt"
          type="datetime-local"
          required
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Duration (seconds)</label>
        <input
          v-model="form.durationSeconds"
          type="number"
          min="0"
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Notes</label>
        <textarea
          v-model="form.notes"
          rows="3"
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <button
        type="submit"
        :disabled="saving"
        class="rounded bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {{ saving ? 'Saving…' : 'Save changes' }}
      </button>
    </form>
  </div>
</template>
