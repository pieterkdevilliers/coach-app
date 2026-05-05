<script setup lang="ts">
const route = useRoute()
const { apiFetch } = useAuthFetch()
const clientId = route.params.id as string

interface Client {
  id: string
  fullName: string
  email: string | null
  phone: string | null
  company: string | null
  notes: string | null
}

const loading = ref(true)
const saving = ref(false)
const error = ref('')

const form = reactive({
  fullName: '',
  email: '',
  phone: '',
  company: '',
  notes: '',
})

onMounted(async () => {
  try {
    const client = await apiFetch<Client>(`/api/clients/${clientId}`)
    form.fullName = client.fullName
    form.email = client.email ?? ''
    form.phone = client.phone ?? ''
    form.company = client.company ?? ''
    form.notes = client.notes ?? ''
  } catch {
    error.value = 'Client not found'
  } finally {
    loading.value = false
  }
})

async function save() {
  error.value = ''
  saving.value = true
  try {
    await apiFetch(`/api/clients/${clientId}`, {
      method: 'PUT',
      body: {
        full_name: form.fullName,
        email: form.email || null,
        phone: form.phone || null,
        company: form.company || null,
        notes: form.notes || null,
      },
    })
    await navigateTo(`/clients/${clientId}`)
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to save changes'
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
    <h1 class="mb-6 text-2xl font-bold">Edit Client</h1>

    <p v-if="loading" class="text-sm text-gray-400">Loading…</p>

    <form v-else class="space-y-4" @submit.prevent="save">
      <div>
        <label class="mb-1 block text-sm font-medium">Full name <span class="text-red-500">*</span></label>
        <input
          v-model="form.fullName"
          type="text"
          required
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Company</label>
        <input
          v-model="form.company"
          type="text"
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Email</label>
        <input
          v-model="form.email"
          type="email"
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Phone</label>
        <input
          v-model="form.phone"
          type="tel"
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Notes</label>
        <textarea
          v-model="form.notes"
          rows="4"
          class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <div class="pt-2">
        <button
          type="submit"
          :disabled="saving"
          class="rounded bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ saving ? 'Saving…' : 'Save changes' }}
        </button>
      </div>
    </form>
  </div>
</template>
