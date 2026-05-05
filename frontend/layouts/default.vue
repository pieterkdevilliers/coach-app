<script setup lang="ts">
const authStore = useAuthStore()
const route = useRoute()

const nav = [
  { label: 'Clients', to: '/' },
  { label: 'Call Types', to: '/settings/call-types' },
  { label: 'Team', to: '/settings/users' },
]
</script>

<template>
  <div class="flex min-h-screen">
    <!-- Sidebar -->
    <aside class="flex w-56 flex-col border-r bg-gray-50">
      <div class="px-5 py-5">
        <span class="text-lg font-bold tracking-tight">Coach App</span>
      </div>

      <nav class="flex-1 space-y-0.5 px-3">
        <NuxtLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="flex items-center rounded px-3 py-2 text-sm font-medium transition-colors"
          :class="
            route.path === item.to
              ? 'bg-blue-50 text-blue-700'
              : 'text-gray-700 hover:bg-gray-100'
          "
        >
          {{ item.label }}
        </NuxtLink>
      </nav>

      <div class="border-t px-3 py-4">
        <p v-if="authStore.user" class="mb-2 truncate px-3 text-xs text-gray-500">
          {{ authStore.user.fullName }}
        </p>
        <button
          class="flex w-full items-center rounded px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
          @click="authStore.logout()"
        >
          Sign out
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-y-auto">
      <slot />
    </main>
  </div>
</template>
