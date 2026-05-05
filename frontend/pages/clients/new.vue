<script setup lang="ts">
const { apiFetch } = useAuthFetch()
const form = reactive({
  fullName: '',
  email: '',
  phone: '',
  company: '',
  notes: '',
})
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const client = await apiFetch<{ id: string }>('/api/clients', {
      method: 'POST',
      body: {
        full_name: form.fullName,
        email: form.email || null,
        phone: form.phone || null,
        company: form.company || null,
        notes: form.notes || null,
      },
    })
    await navigateTo(`/clients/${client.id}`)
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to create client'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-xl p-6">
    <NuxtLink to="/clients" class="mb-4 inline-block text-sm text-blue-600 hover:underline">
      ← Back to clients
    </NuxtLink>
    <h1 class="mb-6 text-2xl font-bold">New Client</h1>

    <form class="space-y-4" @submit.prevent="submit">
      <div>
        <label class="mb-1 block text-sm font-medium">Full name <span class="text-red-500">*</span></label>
        <input v-model="form.fullName" type="text" required class="w-full rounded border px-3 py-2 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Company</label>
        <input v-model="form.company" type="text" class="w-full rounded border px-3 py-2 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Email</label>
        <input v-model="form.email" type="email" class="w-full rounded border px-3 py-2 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Phone</label>
        <input v-model="form.phone" type="tel" class="w-full rounded border px-3 py-2 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Notes</label>
        <textarea v-model="form.notes" rows="3" class="w-full rounded border px-3 py-2 text-sm" />
      </div>

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <button
        type="submit"
        :disabled="loading"
        class="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {{ loading ? 'Saving…' : 'Create client' }}
      </button>
    </form>
  </div>
</template>
