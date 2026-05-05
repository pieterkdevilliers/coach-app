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
  createdAt: string
}

interface ClientNote {
  id: string
  content: string
  createdByName: string
  createdAt: string
}

const client = ref<Client | null>(null)
const clientNotes = ref<ClientNote[]>([])
const loading = ref(true)
const deleting = ref(false)
const showDeleteDialog = ref(false)
const error = ref('')

const newNote = ref('')
const savingNote = ref(false)

onMounted(async () => {
  try {
    ;[client.value, clientNotes.value] = await Promise.all([
      apiFetch<Client>(`/api/clients/${clientId}`),
      apiFetch<ClientNote[]>(`/api/clients/${clientId}/notes`),
    ])
  } catch {
    error.value = 'Client not found'
  } finally {
    loading.value = false
  }
})

async function addNote() {
  if (!newNote.value.trim()) return
  savingNote.value = true
  try {
    const note = await apiFetch<ClientNote>(`/api/clients/${clientId}/notes`, {
      method: 'POST',
      body: { content: newNote.value.trim() },
    })
    clientNotes.value.unshift(note)
    newNote.value = ''
  } finally {
    savingNote.value = false
  }
}

async function deleteNote(noteId: string) {
  await apiFetch(`/api/clients/${clientId}/notes/${noteId}`, { method: 'DELETE' })
  clientNotes.value = clientNotes.value.filter((n) => n.id !== noteId)
}

async function confirmDelete() {
  deleting.value = true
  try {
    await apiFetch(`/api/clients/${clientId}`, { method: 'DELETE' })
    await navigateTo('/')
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to delete client'
    deleting.value = false
    showDeleteDialog.value = false
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="p-6">
    <NuxtLink to="/" class="mb-4 inline-block text-sm text-blue-600 hover:underline">
      ← Back to clients
    </NuxtLink>

    <p v-if="loading" class="text-sm text-gray-400">Loading…</p>
    <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>

    <template v-else-if="client">
      <!-- Header -->
      <div class="mb-6 flex items-start justify-between">
        <div>
          <h1 class="text-2xl font-bold">{{ client.fullName }}</h1>
          <p v-if="client.company" class="text-gray-500">{{ client.company }}</p>
        </div>
        <div class="flex gap-2">
          <NuxtLink
            :to="`/clients/${clientId}/edit`"
            class="rounded border px-3 py-1.5 text-sm hover:bg-gray-50"
          >
            Edit
          </NuxtLink>
          <button
            class="rounded border border-red-200 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
            @click="showDeleteDialog = true"
          >
            Delete
          </button>
        </div>
      </div>

      <!-- Contact details -->
      <div class="mb-8 grid grid-cols-2 gap-4 rounded-lg border p-4 text-sm">
        <div>
          <p class="text-gray-500">Email</p>
          <p>{{ client.email ?? '—' }}</p>
        </div>
        <div>
          <p class="text-gray-500">Phone</p>
          <p>{{ client.phone ?? '—' }}</p>
        </div>
        <div v-if="client.notes" class="col-span-2">
          <p class="text-gray-500">Notes</p>
          <p class="whitespace-pre-wrap">{{ client.notes }}</p>
        </div>
      </div>

      <!-- Notes -->
      <h2 class="mb-3 text-lg font-semibold">Notes</h2>

      <form class="mb-6" @submit.prevent="addNote">
        <textarea
          v-model="newNote"
          rows="3"
          placeholder="Add a note…"
          class="mb-2 w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          :disabled="savingNote || !newNote.trim()"
          class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ savingNote ? 'Saving…' : 'Add note' }}
        </button>
      </form>

      <p v-if="clientNotes.length === 0" class="text-sm text-gray-400">No notes yet.</p>

      <ul v-else class="space-y-3">
        <li
          v-for="note in clientNotes"
          :key="note.id"
          class="rounded-lg border p-4 text-sm"
        >
          <p class="mb-3 whitespace-pre-wrap">{{ note.content }}</p>
          <div class="flex items-center justify-between text-xs text-gray-400">
            <span>{{ note.createdByName }} · {{ formatDate(note.createdAt) }}</span>
            <button
              class="text-red-400 hover:text-red-600"
              @click="deleteNote(note.id)"
            >
              Delete
            </button>
          </div>
        </li>
      </ul>

      <!-- Recordings — wired up when recording feature is complete -->
      <h2 class="mb-3 mt-8 text-lg font-semibold">Recordings</h2>
      <p class="text-sm text-gray-400">No recordings yet.</p>

      <ConfirmDialog
        v-model="showDeleteDialog"
        title="Delete client"
        :message="`Are you sure you want to delete ${client.fullName}? This cannot be undone.`"
        confirm-label="Delete"
        :loading="deleting"
        @confirm="confirmDelete"
      />
    </template>
  </div>
</template>
