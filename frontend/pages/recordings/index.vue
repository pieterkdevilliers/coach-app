<template>
  <div class="p-6">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Recordings</h1>
      <NuxtLink
        to="/recordings/upload"
        class="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        Upload
      </NuxtLink>
    </div>

    <div class="mb-4 flex gap-3">
      <select class="rounded border px-3 py-2 text-sm">
        <option value="">All call types</option>
      </select>
      <select class="rounded border px-3 py-2 text-sm">
        <option value="">All statuses</option>
        <option value="pending">Pending</option>
        <option value="processing">Processing</option>
        <option value="complete">Complete</option>
        <option value="failed">Failed</option>
      </select>
    </div>

    <div class="overflow-hidden rounded-lg border">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-left">
          <tr>
            <th class="px-4 py-3 font-medium">Title</th>
            <th class="px-4 py-3 font-medium">Client</th>
            <th class="px-4 py-3 font-medium">Call Type</th>
            <th class="px-4 py-3 font-medium">Date</th>
            <th class="px-4 py-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="px-4 py-3 text-gray-400" colspan="5">No recordings found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
