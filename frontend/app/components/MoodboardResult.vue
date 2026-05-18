<script setup lang="ts">
import { useApi } from '~/composables/useApi'

interface Color {
  hex: string
  name?: string
  role?: string
  usage_percent?: number
}
interface Reference {
  title: string
  description: string
  search_query?: string
  image_url?: string
  image_fallback?: string
  source?: string
}
interface Payload {
  theme?: string
  description?: string
  mood?: string[]
  keywords?: string[]
  palette?: Color[]
  palette_rationale?: string
  references?: Reference[]
  textures?: string[]
  composition_principles?: string[]
  application_hint?: string
}

const router = useRouter()
const api = useApi()

const props = defineProps<{ payload: Payload; projectId?: number | null }>()

async function goToFonts() {
  const pid = props.projectId ?? null
  if (pid) {
    try {
      const data = await api.get<{ results: { id: number; updated_at: string }[] } | { id: number; updated_at: string }[]>(
        `/ai/sessions/?mode=fonts&project=${pid}`,
      )
      const list = Array.isArray(data) ? data : data.results
      if (list.length) {
        const latest = list.slice().sort((a, b) => (b.updated_at || '').localeCompare(a.updated_at || ''))[0]
        if (latest) {
          await router.push(`/app/fonts/${latest.id}`)
          return
        }
      }
    } catch { /* fall through */ }
    await router.push(`/app/fonts?project=${pid}`)
    return
  }
  await router.push('/app/fonts')
}

const copiedHex = ref<string>('')
function copyHex(hex: string) {
  navigator.clipboard?.writeText(hex)
  copiedHex.value = hex
  setTimeout(() => { if (copiedHex.value === hex) copiedHex.value = '' }, 1200)
}

function refImageSrc(ref: Reference): string | undefined {
  return ref.image_url || ref.image_fallback
}

function onImgError(e: Event, ref: Reference) {
  const el = e.target as HTMLImageElement
  if (ref.image_fallback && el.src !== ref.image_fallback) {
    el.src = ref.image_fallback
    return
  }
  const seed = encodeURIComponent((ref.search_query || ref.title || 'design').slice(0, 32))
  const f = `https://picsum.photos/seed/${seed}/800/600`
  if (el.src !== f) el.src = f
}

const roleLabel: Record<string, string> = {
  primary: 'основной',
  secondary: 'вторичный',
  accent: 'акцент',
  neutral: 'нейтральный',
  background: 'фон',
  text: 'текст',
}

/** Normalise usage percents so the proportion bar always fills 100%. */
const normalisedPalette = computed(() => {
  const pal = props.payload.palette || []
  if (!pal.length) return [] as (Color & { pct: number })[]
  const withExplicit = pal.map(c => ({ ...c, pct: Math.max(0, c.usage_percent ?? 0) }))
  const sum = withExplicit.reduce((a, c) => a + c.pct, 0)
  if (sum > 0) return withExplicit.map(c => ({ ...c, pct: (c.pct / sum) * 100 }))
  // equal split if no proportions given
  return withExplicit.map(c => ({ ...c, pct: 100 / pal.length }))
})

// Derive contrast color for text on a swatch (light vs dark).
function isDark(hex: string): boolean {
  const h = hex.replace('#', '')
  if (h.length !== 6) return false
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  // perceptual luminance
  const l = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return l < 0.55
}

</script>

<template>
  <div v-if="props.payload" class="space-y-6">
    <!-- Header -->
    <header v-if="props.payload.theme || props.payload.description" class="space-y-2">
      <h3 v-if="props.payload.theme" class="font-display text-xl font-semibold text-ink-900 leading-tight">
        {{ props.payload.theme }}
      </h3>
      <p v-if="props.payload.description" class="text-sm text-ink-500 leading-relaxed max-w-2xl">
        {{ props.payload.description }}
      </p>
    </header>

    <!-- Reference grid -->
    <section v-if="props.payload.references?.length">
      <div class="text-[10px] uppercase tracking-widest text-ink-400 mb-3">Референсы</div>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-2.5">
        <article
          v-for="(r, i) in props.payload.references.slice(0, 6)" :key="i"
          class="group relative rounded-2xl overflow-hidden bg-ink-100 aspect-4/3"
        >
          <img
            :src="refImageSrc(r)"
            :alt="r.title"
            class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
            loading="lazy"
            referrerpolicy="no-referrer"
            @error="onImgError($event, r)"
          />
        </article>
      </div>
    </section>

    <!-- Palette section -->
    <section v-if="normalisedPalette.length">
      <div class="flex items-center justify-between mb-3">
        <div class="text-[10px] uppercase tracking-widest text-ink-400">Палитра</div>
        <div class="text-[10px] text-ink-400">{{ normalisedPalette.length }} цветов · кликните, чтобы скопировать HEX</div>
      </div>

      <!-- Proportion bar -->
      <div class="flex h-2.5 rounded-full overflow-hidden ring-1 ring-ink-100 mb-3">
        <div
          v-for="c in normalisedPalette" :key="`bar-${c.hex}`"
          :style="{ background: c.hex, width: `${c.pct}%` }"
          :title="`${c.name || ''} · ${c.hex} · ${Math.round(c.pct)}%`"
        />
      </div>

      <!-- Palette rationale -->
      <p v-if="props.payload.palette_rationale" class="text-xs text-ink-500 leading-relaxed mb-3 bg-ink-50 rounded-xl px-4 py-3">
        {{ props.payload.palette_rationale }}
      </p>

      <!-- Swatches grid -->
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
        <button
          v-for="c in normalisedPalette" :key="c.hex"
          class="card-flat overflow-hidden text-left cursor-pointer hover:shadow-soft transition-shadow"
          :title="`Скопировать ${c.hex}`"
          @click="copyHex(c.hex)"
        >
          <div class="relative aspect-4/3" :style="{ background: c.hex }">
            <div class="absolute top-2 right-2 text-[9px] font-mono font-medium px-1.5 py-0.5 rounded"
                 :class="isDark(c.hex) ? 'bg-white/20 text-white' : 'bg-black/10 text-ink-900'">
              {{ Math.round(c.pct) }}%
            </div>
            <div v-if="copiedHex === c.hex"
                 class="absolute inset-0 flex items-center justify-center text-xs font-medium"
                 :class="isDark(c.hex) ? 'text-white' : 'text-ink-900'">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m5 12 5 5L20 7"/></svg>
            </div>
          </div>
          <div class="p-2.5">
            <div class="flex items-center gap-1.5">
              <span v-if="c.role" class="text-[9px] uppercase tracking-wider text-ink-400">
                {{ roleLabel[c.role] || c.role }}
              </span>
            </div>
            <div class="text-xs font-medium text-ink-900 truncate mt-0.5">{{ c.name || c.hex }}</div>
            <div class="text-[10px] font-mono text-ink-500">{{ c.hex.toUpperCase() }}</div>
          </div>
        </button>
      </div>
    </section>

    <!-- Textures -->
    <section v-if="props.payload.textures?.length" class="card-flat p-5">
      <div class="text-[10px] uppercase tracking-widest text-ink-400 mb-3">Фактуры</div>
      <div class="flex flex-wrap gap-1.5">
        <span v-for="t in props.payload.textures" :key="t" class="chip">{{ t }}</span>
      </div>
    </section>

    <!-- Composition principles -->
    <section v-if="props.payload.composition_principles?.length" class="card-flat p-5">
      <div class="text-[10px] uppercase tracking-widest text-ink-400 mb-3">Принципы композиции</div>
      <ul class="space-y-2">
        <li v-for="(p, i) in props.payload.composition_principles" :key="i" class="flex items-start gap-3">
          <span class="h-5 w-5 rounded-full bg-accent-50 text-accent-600 text-[11px] font-semibold flex items-center justify-center shrink-0 mt-0.5">
            {{ i + 1 }}
          </span>
          <span class="text-sm text-ink-700 leading-relaxed">{{ p }}</span>
        </li>
      </ul>
    </section>

    <!-- Switch to fonts CTA — last block -->
    <button
      class="w-full card-flat p-4 flex items-center justify-between gap-3 text-left hover:shadow-soft transition-shadow cursor-pointer group"
      @click="goToFonts"
    >
      <div>
        <div class="text-sm font-semibold text-ink-900">Перейти к подбору шрифтов</div>
        <div class="text-xs text-ink-500 mt-0.5">Продолжить в этом проекте — собрать шрифтовую пару под мудборд</div>
      </div>
      <span class="inline-flex items-center justify-center h-9 w-9 rounded-full bg-accent-50 text-accent-600 group-hover:bg-accent-100 transition-colors shrink-0">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
      </span>
    </button>

  </div>
</template>
