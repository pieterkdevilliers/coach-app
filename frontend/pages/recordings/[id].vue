<script setup lang="ts">
const route = useRoute()
const recordingId = route.params.id as string

const activeTab = ref<'transcript' | 'extraction' | 'queries'>('transcript')
</script>

<template>
  <div class="p-6">
    <NuxtLink to="/recordings" class="mb-4 inline-block text-sm text-blue-600 hover:underline">
      ← Back to recordings
    </NuxtLink>

    <!-- Metadata header -->
    <div class="mb-6 rounded-lg border p-4">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-xl font-bold">Recording</h1>
          <p class="text-sm text-gray-500">ID: {{ recordingId }}</p>
        </div>
        <span class="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium">—</span>
      </div>
    </div>

    <!-- Tabs -->
    <div class="mb-4 flex gap-1 border-b">
      <button
        v-for="tab in ['transcript', 'extraction', 'queries'] as const"
        :key="tab"
        class="px-4 py-2 text-sm font-medium capitalize"
        :class="activeTab === tab ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'"
        @click="activeTab = tab"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Transcript tab -->
    <div v-if="activeTab === 'transcript'">
      <p class="text-sm text-gray-400">No transcript available yet.</p>
    </div>

    <!-- Extraction tab -->
    <div v-else-if="activeTab === 'extraction'">
      <p class="text-sm text-gray-400">No extraction available yet.</p>
    </div>

    <!-- Queries tab -->
    <div v-else-if="activeTab === 'queries'">
      <div class="mb-4 flex gap-2">
        <input
          type="text"
          placeholder="Ask a question about this recording…"
          class="flex-1 rounded border px-3 py-2 text-sm"
        />
        <button class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
          Ask
        </button>
      </div>
      <p class="text-sm text-gray-400">No queries yet.</p>
    </div>
  </div>
</template>
