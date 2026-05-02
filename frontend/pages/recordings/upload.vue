<template>
  <div class="mx-auto max-w-xl p-6">
    <h1 class="mb-6 text-2xl font-bold">Upload Recording</h1>

    <form class="space-y-4">
      <div>
        <label class="mb-1 block text-sm font-medium">File</label>
        <input
          type="file"
          accept="audio/*,video/*"
          class="w-full rounded border px-3 py-2 text-sm"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">Title</label>
        <input
          type="text"
          placeholder="Recording title"
          class="w-full rounded border px-3 py-2 text-sm"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">Call Type</label>
        <select class="w-full rounded border px-3 py-2 text-sm">
          <option value="">Select a call type…</option>
        </select>
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">Client Name</label>
        <input
          type="text"
          placeholder="Optional"
          class="w-full rounded border px-3 py-2 text-sm"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">Recorded Date</label>
        <input type="datetime-local" class="w-full rounded border px-3 py-2 text-sm" />
      </div>

      <button
        type="submit"
        class="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        Upload
      </button>
    </form>
  </div>
</template>
