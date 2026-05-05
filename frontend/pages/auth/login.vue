<script setup lang="ts">
definePageMeta({ layout: false })

const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    await navigateTo('/')
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-sm rounded-lg border bg-white p-8 shadow-sm">
      <h1 class="mb-6 text-center text-2xl font-bold">Sign in</h1>

      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="mb-1 block text-sm font-medium">Email</label>
          <input
            v-model="email"
            type="email"
            required
            autocomplete="email"
            class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Password</label>
          <input
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            class="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <p class="mt-4 text-center text-sm text-gray-500">
        New business?
        <NuxtLink to="/auth/register" class="text-blue-600 hover:underline">Create an account</NuxtLink>
      </p>
    </div>
  </div>
</template>
