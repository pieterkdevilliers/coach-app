<script setup lang="ts">
const route = useRoute()
const { apiFetch } = useAuthFetch()
const clientId = route.params.id as string

interface CallType { id: string; name: string }

const callTypes = ref<CallType[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const form = reactive({
  title: '',
  callTypeId: '',
  calledAt: new Date().toISOString().slice(0, 16),
  durationSeconds: '' as string | number,
  notes: '',
})

onMounted(async () => {
  try {
    callTypes.value = await apiFetch<CallType[]>('/api/call-types')
    if (callTypes.value.length) form.callTypeId = callTypes.value[0].id
  } catch {
    error.value = 'Failed to load call types'
  } finally {
    loading.value = false
  }
})

async function save() {
  error.value = ''
  saving.value = true
  try {
    const call = await apiFetch<{ id: string }>(`/api/clients/${clientId}/calls`, {
      method: 'POST',
      body: {
        title: form.title,
        call_type_id: form.callTypeId,
        called_at: new Date(form.calledAt).toISOString(),
        duration_seconds: form.durationSeconds ? Number(form.durationSeconds) : null,
        notes: form.notes || null,
      },
    })
    await navigateTo(`/calls/${call.id}`)
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to create call'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-xl p-6">
    <NuxtLink :to="`/clients/${clientId}`" class="mb-4 inline-block text-sm text-blue-600 hover:underline">
      ← Back to client
    </NuxtLink>
    <h1 class="mb-6 text-2xl font-bold">New Call</h1>

    <p v-if="loading" class="text-sm text-gray-400">Loading…</p>

    <form v-else class="space-y-4" @submit.prevent="save">
      <div>
        <label class="mb-1 block text-sm font-medium">Title <span class="text-red-500">*</span></label>
        <input
          v-model="form.title"
          type="text"
          required
          placeholder="e.g. Quarterly Business Review"
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
          placeholder="Optional"
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Notes</label>
        <textarea
          v-model="form.notes"
          rows="3"
          placeholder="Pre-call notes or context"
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <button
        type="submit"
        :disabled="saving"
        class="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {{ saving ? 'Creating…' : 'Create call' }}
      </button>
    </form>
  </div>
</template>
