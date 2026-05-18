<script setup lang="ts">
const props = defineProps<{
  modelValue: string
  options: string[]
  placeholder?: string
}>()
const emit = defineEmits<{ 'update:modelValue': [string] }>()

const open = ref(false)
const root = ref<HTMLElement | null>(null)

function toggle() { open.value = !open.value }

function select(v: string) {
  emit('update:modelValue', v)
  open.value = false
}

function onClickOutside(e: MouseEvent) {
  if (!root.value) return
  if (!root.value.contains(e.target as Node)) open.value = false
}
function onEsc(e: KeyboardEvent) {
  if (e.key === 'Escape') open.value = false
}

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside)
  document.addEventListener('keydown', onEsc)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onClickOutside)
  document.removeEventListener('keydown', onEsc)
})
</script>

<template>
  <div ref="root" class="relative">
    <button
      type="button"
      class="w-full flex items-center justify-between rounded-full bg-white px-4 py-2.5 text-sm text-ink-800 transition cursor-pointer"
      :class="open ? 'ring-2 ring-accent-400' : 'ring-1 ring-ink-200 hover:ring-ink-300'"
      @click="toggle"
    >
      <span :class="!props.modelValue && 'text-ink-400'">
        {{ props.modelValue || props.placeholder || 'любой' }}
      </span>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="open ? 'rotate-180' : ''" class="transition-transform text-ink-400 shrink-0">
        <path d="m6 9 6 6 6-6" />
      </svg>
    </button>

    <Transition
      enter-active-class="transition ease-out duration-150"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div v-if="open" class="absolute z-30 left-0 right-0 top-full mt-2 rounded-2xl bg-white shadow-soft ring-1 ring-ink-100 p-1.5 max-h-60 overflow-y-auto">
        <button
          type="button"
          class="w-full text-left px-3 py-2 rounded-xl text-sm hover:bg-ink-50 transition-colors cursor-pointer"
          :class="!props.modelValue ? 'text-accent-600 font-medium bg-accent-50' : 'text-ink-500'"
          @click="select('')"
        >
          {{ props.placeholder || 'любой' }}
        </button>
        <button
          v-for="o in props.options" :key="o"
          type="button"
          class="w-full text-left px-3 py-2 rounded-xl text-sm hover:bg-ink-50 transition-colors cursor-pointer"
          :class="props.modelValue === o ? 'text-accent-600 font-medium bg-accent-50' : 'text-ink-700'"
          @click="select(o)"
        >
          {{ o }}
        </button>
      </div>
    </Transition>
  </div>
</template>
