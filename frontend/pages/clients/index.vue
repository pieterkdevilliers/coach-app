<script setup lang="ts">
const { apiFetch } = useAuthFetch()

interface Client {
  id: string
  fullName: string
  email: string | null
  phone: string | null
  company: string | null
  createdAt: string
}

const clients = ref<Client[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    clients.value = await apiFetch<Client[]>('/api/clients')
  } catch {
    error.value = 'Failed to load clients'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="p-6">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Clients</h1>
      <NuxtLink
        to="/clients/new"
        class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        New Client
      </NuxtLink>
    </div>

    <p v-if="loading" class="text-sm text-gray-400">Loading…</p>
    <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>
    <p v-else-if="clients.length === 0" class="text-sm text-gray-400">No clients yet.</p>

    <div v-else class="overflow-hidden rounded-lg border">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-left">
          <tr>
            <th class="px-4 py-3 font-medium">Name</th>
            <th class="px-4 py-3 font-medium">Company</th>
            <th class="px-4 py-3 font-medium">Email</th>
            <th class="px-4 py-3 font-medium">Phone</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr
            v-for="client in clients"
            :key="client.id"
            class="cursor-pointer hover:bg-gray-50"
            @click="navigateTo(`/clients/${client.id}`)"
          >
            <td class="px-4 py-3 font-medium">{{ client.fullName }}</td>
            <td class="px-4 py-3 text-gray-500">{{ client.company ?? '—' }}</td>
            <td class="px-4 py-3 text-gray-500">{{ client.email ?? '—' }}</td>
            <td class="px-4 py-3 text-gray-500">{{ client.phone ?? '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
