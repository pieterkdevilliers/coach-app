<script setup lang="ts">
definePageMeta({ layout: false })

const route = useRoute()
const authStore = useAuthStore()
const token = computed(() => route.query.token as string ?? '')
const fullName = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await authStore.acceptInvite(token.value, fullName.value, password.value)
    await navigateTo('/')
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to accept invite'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-sm rounded-lg border bg-white p-8 shadow-sm">
      <h1 class="mb-2 text-center text-2xl font-bold">Accept invitation</h1>
      <p class="mb-6 text-center text-sm text-gray-500">Set up your coach account</p>

      <p v-if="!token" class="text-sm text-red-600">Invalid or missing invite link.</p>

      <form v-else class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="mb-1 block text-sm font-medium">Full name</label>
          <input v-model="fullName" type="text" required class="w-full rounded border px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Password</label>
          <input v-model="password" type="password" required autocomplete="new-password" class="w-full rounded border px-3 py-2 text-sm" />
        </div>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? 'Setting up account…' : 'Create account' }}
        </button>
      </form>
    </div>
  </div>
</template>
