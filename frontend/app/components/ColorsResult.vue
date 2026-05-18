<script setup lang="ts">
interface Color { hex: string; name?: string; role?: string }
interface Palette { name: string; description?: string; colors: Color[] }
const props = defineProps<{ payload: { palettes?: Palette[] } }>()

function copy(text: string) { navigator.clipboard?.writeText(text) }
</script>

<template>
  <div v-if="props.payload?.palettes?.length" class="space-y-5">
    <article v-for="p in props.payload.palettes" :key="p.name">
      <div class="mb-4">
        <div class="font-semibold text-sm text-ink-900">{{ p.name }}</div>
        <p v-if="p.description" class="text-xs text-ink-500 mt-1">{{ p.description }}</p>
      </div>

      <!-- Big swatches row -->
      <div class="grid grid-cols-5 gap-2">
        <button
          v-for="c in p.colors.slice(0, 5)" :key="c.hex"
          class="group card-flat overflow-hidden text-left cursor-pointer"
          :title="`Скопировать ${c.hex}`"
          @click="copy(c.hex)"
        >
          <div class="aspect-square" :style="{ background: c.hex }" />
          <div class="px-2.5 py-2">
            <div class="text-[10px] text-ink-400 uppercase tracking-wide truncate">{{ c.role || c.name || '' }}</div>
            <div class="text-[11px] font-mono font-medium text-ink-800 mt-0.5">{{ c.hex }}</div>
          </div>
        </button>
      </div>
    </article>
  </div>
</template>
