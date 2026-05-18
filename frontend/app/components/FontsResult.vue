<script setup lang="ts">
interface FontSpec {
  family: string
  google_fonts?: boolean
  category?: string
  weight?: number
  style?: string
  available_weights?: number[]
  source?: 'google_fonts' | 'local' | 'external'
  file_url?: string | null
}
interface FontPair {
  name: string
  heading: FontSpec
  body: FontSpec
  sample_title?: string
  sample_body?: string
  pangram?: string
  use_cases?: string[]
  mood?: string[]
  rationale?: string
}
const props = defineProps<{ payload: { pairs?: FontPair[] } }>()

/** Build a single Google Fonts CSS link that loads every italic+weight we might need for all pairs. */
const gfHref = computed(() => {
  const families = new Map<string, Set<number>>()
  for (const p of props.payload?.pairs || []) {
    for (const spec of [p.heading, p.body]) {
      if (!spec?.google_fonts || !spec.family) continue
      const set = families.get(spec.family) ?? new Set<number>()
      if (spec.weight) set.add(spec.weight)
      for (const w of spec.available_weights || []) set.add(w)
      // Always guarantee minimal coverage
      ;[400, 500, 600, 700].forEach(w => set.add(w))
      families.set(spec.family, set)
    }
  }
  if (!families.size) return ''
  const parts = [...families.entries()].map(([fam, weights]) => {
    const w = [...weights].sort((a, b) => a - b)
    const axis = w.map(x => `0,${x}`).concat(w.map(x => `1,${x}`)).join(';')
    return `family=${fam.replace(/ /g, '+')}:ital,wght@${axis}`
  })
  return `https://fonts.googleapis.com/css2?${parts.join('&')}&display=swap`
})

function fontFormat(url: string): string {
  const ext = url.split('?')[0]?.split('.').pop()?.toLowerCase() || ''
  if (ext === 'ttf') return 'truetype'
  if (ext === 'otf') return 'opentype'
  if (ext === 'woff2') return 'woff2'
  if (ext === 'woff') return 'woff'
  return 'truetype'
}

/** @font-face declarations for local/external fonts that bring their own file. */
const localFontFaceCss = computed(() => {
  const seen = new Set<string>()
  const lines: string[] = []
  for (const p of props.payload?.pairs || []) {
    for (const spec of [p.heading, p.body]) {
      if (!spec?.family || spec.google_fonts) continue
      if (!spec.file_url) continue
      const key = `${spec.family}|${spec.file_url}`
      if (seen.has(key)) continue
      seen.add(key)
      const fmt = fontFormat(spec.file_url)
      lines.push(
        `@font-face { font-family: '${spec.family.replace(/'/g, "\\'")}'; ` +
          `src: url('${spec.file_url}') format('${fmt}'); ` +
          `font-display: swap; }`,
      )
    }
  }
  return lines.join('\n')
})

useHead(() => {
  const head: Record<string, any> = {}
  if (gfHref.value) {
    head.link = [{
      key: `fonts-${gfHref.value}`,
      rel: 'stylesheet',
      href: gfHref.value,
    }]
  }
  if (localFontFaceCss.value) {
    head.style = [{
      key: `local-fonts-${localFontFaceCss.value.length}`,
      children: localFontFaceCss.value,
    }]
  }
  return head
})
</script>

<template>
  <div v-if="props.payload?.pairs?.length" class="space-y-4">
    <FontPairCard
      v-for="(p, i) in props.payload.pairs"
      :key="`${p.name}-${i}`"
      :pair="p"
      :index="i"
    />
  </div>
</template>
