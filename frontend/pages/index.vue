<template>
  <div class="p-6">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Dashboard</h1>
      <NuxtLink
        to="/recordings/upload"
        class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        Upload Recording
      </NuxtLink>
    </div>

    <div class="mb-8 grid grid-cols-3 gap-4">
      <div class="rounded-lg border p-4">
        <p class="text-sm text-gray-500">Total Recordings</p>
        <p class="text-3xl font-bold">—</p>
      </div>
      <div class="rounded-lg border p-4">
        <p class="text-sm text-gray-500">Processing</p>
        <p class="text-3xl font-bold">—</p>
      </div>
      <div class="rounded-lg border p-4">
        <p class="text-sm text-gray-500">Completed</p>
        <p class="text-3xl font-bold">—</p>
      </div>
    </div>

    <h2 class="mb-3 text-lg font-semibold">Recent Recordings</h2>
    <p class="text-sm text-gray-400">No recordings yet.</p>
  </div>
</template>
