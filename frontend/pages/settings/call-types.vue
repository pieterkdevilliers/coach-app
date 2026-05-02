<script setup lang="ts">
const showForm = ref(false)
</script>

<template>
  <div class="p-6">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Call Types</h1>
      <button
        class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        @click="showForm = true"
      >
        New Call Type
      </button>
    </div>

    <!-- New / edit form -->
    <div v-if="showForm" class="mb-6 rounded-lg border p-4">
      <h2 class="mb-4 text-lg font-semibold">New Call Type</h2>
      <form class="space-y-4">
        <div>
          <label class="mb-1 block text-sm font-medium">Name</label>
          <input type="text" class="w-full rounded border px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Description</label>
          <input type="text" class="w-full rounded border px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Prompt Template</label>
          <textarea rows="5" class="w-full rounded border px-3 py-2 text-sm" />
        </div>
        <div class="flex gap-2">
          <button
            type="submit"
            class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Save
          </button>
          <button
            type="button"
            class="rounded border px-4 py-2 text-sm font-medium hover:bg-gray-50"
            @click="showForm = false"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- Call types list -->
    <div class="space-y-2">
      <p class="text-sm text-gray-400">No call types yet.</p>
    </div>
  </div>
</template>
