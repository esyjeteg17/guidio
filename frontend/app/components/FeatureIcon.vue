<script setup lang="ts">
const props = defineProps<{ name: string; compact?: boolean }>()
</script>

<template>
  <div
    :class="[
      'flex items-center justify-center text-ink-700',
      props.compact ? 'h-auto w-auto text-white' : 'h-11 w-11 rounded-xl bg-ink-50'
    ]"
  >
    <svg :width="props.compact ? 22 : 22" :height="props.compact ? 22 : 22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
      <template v-if="props.name === 'type'">
        <path d="M4 7V5h16v2M9 5v14M9 19h6M15 5v14" />
      </template>
      <template v-else-if="props.name === 'sliders'">
        <path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h14M18 18h2" />
        <circle cx="15" cy="6" r="1.5" />
        <circle cx="10" cy="12" r="1.5" />
        <circle cx="16" cy="18" r="1.5" />
      </template>
      <template v-else-if="props.name === 'grid'">
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </template>
      <template v-else-if="props.name === 'sparkles'">
        <path d="M12 3l2 5 5 2-5 2-2 5-2-5-5-2 5-2 2-5zM19 14l1 2.5 2.5 1-2.5 1L19 21l-1-2.5-2.5-1 2.5-1L19 14z" />
      </template>
      <template v-else-if="props.name === 'chat'">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </template>
      <template v-else-if="props.name === 'team'">
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </template>
      <template v-else-if="props.name === 'book'">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
      </template>
      <template v-else-if="props.name === 'spark'">
        <path d="M12 3 13.5 9.5 20 11 13.5 12.5 12 19 10.5 12.5 4 11 10.5 9.5Z" />
      </template>
      <template v-else-if="props.name === 'filters'">
        <path d="M3 6h18M6 12h12M10 18h4" />
      </template>
      <template v-else-if="props.name === 'layers'">
        <path d="M12 3 3 8l9 5 9-5-9-5ZM3 13l9 5 9-5M3 18l9 5 9-5" />
      </template>
    </svg>
  </div>
</template>
