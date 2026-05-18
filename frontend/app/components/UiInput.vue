<script setup lang="ts">
const props = defineProps<{
  modelValue: string | number | null | undefined
  placeholder?: string
  type?: string
  rows?: number
  disabled?: boolean
  autocomplete?: string
  iconLeft?: boolean
}>()
const emit = defineEmits<{ 'update:modelValue': [string], 'enter': [] }>()

const multiline = computed(() => (props.rows || 1) > 1)
const inputType = computed(() => props.type || 'text')

function onInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLInputElement | HTMLTextAreaElement).value)
}

function onEnter(e: KeyboardEvent) {
  if (!e.shiftKey && !multiline.value) emit('enter')
}
</script>

<template>
  <div class="relative">
    <span v-if="$slots.prefix" class="absolute left-4 top-1/2 -translate-y-1/2 text-ink-400 pointer-events-none">
      <slot name="prefix" />
    </span>

    <textarea
      v-if="multiline"
      :value="props.modelValue ?? ''"
      :placeholder="props.placeholder"
      :rows="props.rows"
      :disabled="props.disabled"
      class="w-full rounded-2xl bg-white px-4 py-3 text-sm text-ink-900 ring-1 ring-ink-200 hover:ring-ink-300 focus:outline-none focus:ring-2 focus:ring-accent-400 transition resize-none placeholder:text-ink-400 disabled:opacity-60 disabled:cursor-not-allowed"
      @input="onInput"
    />
    <input
      v-else
      :type="inputType"
      :value="props.modelValue ?? ''"
      :placeholder="props.placeholder"
      :disabled="props.disabled"
      :autocomplete="props.autocomplete"
      class="w-full rounded-full bg-white px-4 py-2.5 text-sm text-ink-900 ring-1 ring-ink-200 hover:ring-ink-300 focus:outline-none focus:ring-2 focus:ring-accent-400 transition placeholder:text-ink-400 disabled:opacity-60 disabled:cursor-not-allowed"
      :class="$slots.prefix ? 'pl-10' : ''"
      @input="onInput"
      @keydown.enter="onEnter"
    />

    <span v-if="$slots.suffix" class="absolute right-3 top-1/2 -translate-y-1/2">
      <slot name="suffix" />
    </span>
  </div>
</template>
