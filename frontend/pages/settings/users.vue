<script setup lang="ts">
const { apiFetch } = useAuthFetch()
const authStore = useAuthStore()

interface UserItem {
  id: string
  fullName: string
  email: string
  role: 'owner' | 'coach'
}

interface Invitation {
  id: string
  email: string
  expiresAt: string
  inviteUrl: string | null
}

const users = ref<UserItem[]>([])
const invitations = ref<Invitation[]>([])
const inviteEmail = ref('')
const lastInviteUrl = ref('')
const loading = ref(true)
const inviting = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    ;[users.value, invitations.value] = await Promise.all([
      apiFetch<UserItem[]>('/api/users'),
      apiFetch<Invitation[]>('/api/invitations'),
    ])
  } finally {
    loading.value = false
  }
})

async function sendInvite() {
  error.value = ''
  inviting.value = true
  try {
    const inv = await apiFetch<Invitation>('/api/invitations', {
      method: 'POST',
      body: { email: inviteEmail.value },
    })
    lastInviteUrl.value = inv.inviteUrl ?? ''
    invitations.value.unshift(inv)
    inviteEmail.value = ''
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to send invite'
  } finally {
    inviting.value = false
  }
}

async function revokeInvite(id: string) {
  await apiFetch(`/api/invitations/${id}`, { method: 'DELETE' })
  invitations.value = invitations.value.filter((i) => i.id !== id)
}

async function deactivateUser(id: string) {
  await apiFetch(`/api/users/${id}`, { method: 'DELETE' })
  users.value = users.value.filter((u) => u.id !== id)
}
</script>

<template>
  <div class="p-6">
    <h1 class="mb-6 text-2xl font-bold">Team</h1>

    <p v-if="loading" class="text-sm text-gray-400">Loading…</p>

    <template v-else>
      <!-- Active users -->
      <h2 class="mb-3 text-lg font-semibold">Coaches</h2>
      <div class="mb-8 overflow-hidden rounded-lg border">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-left">
            <tr>
              <th class="px-4 py-3 font-medium">Name</th>
              <th class="px-4 py-3 font-medium">Email</th>
              <th class="px-4 py-3 font-medium">Role</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="u in users" :key="u.id">
              <td class="px-4 py-3">{{ u.fullName }}</td>
              <td class="px-4 py-3 text-gray-500">{{ u.email }}</td>
              <td class="px-4 py-3 capitalize">{{ u.role }}</td>
              <td class="px-4 py-3 text-right">
                <button
                  v-if="authStore.isOwner && u.id !== authStore.user?.id"
                  class="text-xs text-red-500 hover:underline"
                  @click="deactivateUser(u.id)"
                >
                  Remove
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Invite section (owner only) -->
      <template v-if="authStore.isOwner">
        <h2 class="mb-3 text-lg font-semibold">Invite a coach</h2>
        <form class="mb-4 flex gap-2" @submit.prevent="sendInvite">
          <input
            v-model="inviteEmail"
            type="email"
            required
            placeholder="coach@example.com"
            class="flex-1 rounded border px-3 py-2 text-sm"
          />
          <button
            type="submit"
            :disabled="inviting"
            class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {{ inviting ? 'Sending…' : 'Send invite' }}
          </button>
        </form>
        <p v-if="error" class="mb-3 text-sm text-red-600">{{ error }}</p>

        <div
          v-if="lastInviteUrl"
          class="mb-6 rounded border border-green-200 bg-green-50 p-3 text-sm"
        >
          <p class="mb-1 font-medium text-green-800">Invite link (share this):</p>
          <code class="break-all text-green-700">{{ lastInviteUrl }}</code>
        </div>

        <h2 class="mb-3 text-lg font-semibold">Pending invites</h2>
        <p v-if="invitations.length === 0" class="text-sm text-gray-400">No pending invites.</p>
        <ul v-else class="space-y-2">
          <li
            v-for="inv in invitations"
            :key="inv.id"
            class="flex items-center justify-between rounded border px-4 py-3 text-sm"
          >
            <span>{{ inv.email }}</span>
            <button class="text-xs text-red-500 hover:underline" @click="revokeInvite(inv.id)">
              Revoke
            </button>
          </li>
        </ul>
      </template>
    </template>
  </div>
</template>
