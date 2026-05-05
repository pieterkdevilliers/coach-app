<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
  title: string
  message: string
  confirmLabel?: string
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
}>()

function close() {
  emit('update:modelValue', false)
}

function confirm() {
  emit('confirm')
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.modelValue) close()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-150"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center"
        @click.self="close"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40" @click="close" />

        <!-- Dialog -->
        <div class="relative z-10 w-full max-w-sm rounded-lg bg-white p-6 shadow-xl">
          <h2 class="mb-2 text-base font-semibold">{{ title }}</h2>
          <p class="mb-6 text-sm text-gray-600">{{ message }}</p>

          <div class="flex justify-end gap-3">
            <button
              type="button"
              class="rounded border px-4 py-2 text-sm hover:bg-gray-50"
              @click="close"
            >
              Cancel
            </button>
            <button
              type="button"
              :disabled="loading"
              class="rounded bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              @click="confirm"
            >
              {{ loading ? 'Deleting…' : (confirmLabel ?? 'Confirm') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
