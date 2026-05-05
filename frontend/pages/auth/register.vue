<script setup lang="ts">
definePageMeta({ layout: false })

const authStore = useAuthStore()
const form = reactive({
  businessName: '',
  businessEmail: '',
  fullName: '',
  email: '',
  password: '',
})
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await authStore.register(form)
    await navigateTo('/')
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-sm rounded-lg border bg-white p-8 shadow-sm">
      <h1 class="mb-6 text-center text-2xl font-bold">Create your account</h1>

      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="mb-1 block text-sm font-medium">Business name</label>
          <input v-model="form.businessName" type="text" required class="w-full rounded border px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Business email</label>
          <input v-model="form.businessEmail" type="email" required class="w-full rounded border px-3 py-2 text-sm" />
        </div>
        <hr class="my-1" />
        <div>
          <label class="mb-1 block text-sm font-medium">Your full name</label>
          <input v-model="form.fullName" type="text" required class="w-full rounded border px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Your email</label>
          <input v-model="form.email" type="email" required autocomplete="email" class="w-full rounded border px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Password</label>
          <input v-model="form.password" type="password" required autocomplete="new-password" class="w-full rounded border px-3 py-2 text-sm" />
        </div>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? 'Creating account…' : 'Create account' }}
        </button>
      </form>

      <p class="mt-4 text-center text-sm text-gray-500">
        Already have an account?
        <NuxtLink to="/auth/login" class="text-blue-600 hover:underline">Sign in</NuxtLink>
      </p>
    </div>
  </div>
</template>
