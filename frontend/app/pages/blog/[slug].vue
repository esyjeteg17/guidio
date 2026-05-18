<script setup lang="ts">
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'default' })

interface Article {
  id: number
  title: string
  slug: string
  tag: string
  hue: string
  cover: string
  excerpt: string
  content: string
  author: string
  read_minutes: number
  published_at: string
  updated_at: string
}

const route = useRoute()
const router = useRouter()
const api = useApi()

const article = ref<Article | null>(null)
const loading = ref(true)
const notFound = ref(false)

const slug = computed(() => String(route.params.slug))

async function load() {
  loading.value = true
  notFound.value = false
  try {
    article.value = await api.get<Article>(`/blog/articles/${encodeURIComponent(slug.value)}/`)
  } catch (e: any) {
    if (e?.status === 404) notFound.value = true
  } finally {
    loading.value = false
  }
}

watch(slug, load, { immediate: true })

useHead(() => ({
  title: article.value ? `${article.value.title} — Guidio` : 'Статья — Guidio',
}))

const hueBg: Record<string, string> = {
  cream: 'bg-bloom-cream',
  mint: 'bg-bloom-mint/40',
  lilac: 'bg-bloom-lilac/30',
  peach: 'bg-bloom-pink/40',
  sky: 'bg-bloom-peri/30',
}

// Very light markdown-to-html for headings + paragraphs
const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  const text = article.value.content
  const blocks = text.split(/\n{2,}/)
  return blocks
    .map((block) => {
      const trimmed = block.trim()
      if (trimmed.startsWith('## ')) {
        return `<h2 class="font-display text-2xl font-semibold text-ink-900 mt-10 mb-3">${trimmed.slice(3)}</h2>`
      }
      if (trimmed.startsWith('# ')) {
        return `<h2 class="font-display text-3xl font-semibold text-ink-900 mt-10 mb-3">${trimmed.slice(2)}</h2>`
      }
      return `<p class="text-ink-700 leading-relaxed mb-5">${trimmed.replace(/\n/g, '<br />')}</p>`
    })
    .join('')
})

function formatDate(s: string) {
  return new Date(s).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>

<template>
  <div class="bloom-full">
    <article v-if="article" class="py-16">
      <div class="max-w-[760px] mx-auto px-6">
        <NuxtLink to="/blog" class="inline-flex items-center gap-1.5 text-sm text-ink-500 hover:text-ink-800 mb-8">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>
          Все статьи
        </NuxtLink>

        <div class="flex items-center gap-2 mb-5">
          <div class="chip">{{ article.tag }}</div>
          <span class="text-[11px] text-ink-400">{{ article.read_minutes }} мин чтения</span>
        </div>

        <h1 class="font-display text-4xl sm:text-[44px] font-semibold text-ink-900 leading-tight mb-5">
          {{ article.title }}
        </h1>
        <p v-if="article.excerpt" class="text-lg text-ink-500 leading-relaxed mb-8">{{ article.excerpt }}</p>

        <div class="flex items-center justify-between pb-6 mb-10 border-b border-ink-100 text-sm">
          <div class="flex items-center gap-3">
            <div class="h-10 w-10 rounded-full bg-linear-to-br from-accent-400 to-bloom-pink text-white font-semibold flex items-center justify-center text-sm">
              {{ article.author.charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="font-medium text-ink-800">{{ article.author }}</div>
              <div class="text-[11px] text-ink-400">{{ formatDate(article.published_at) }}</div>
            </div>
          </div>
        </div>

        <div v-if="article.cover" class="aspect-16/9 rounded-2xl overflow-hidden mb-10">
          <img :src="article.cover" :alt="article.title" class="w-full h-full object-cover" />
        </div>
        <div v-else class="aspect-16/9 rounded-2xl flex items-center justify-center mb-10" :class="hueBg[article.hue] || 'bg-ink-50'">
          <span class="font-display italic text-4xl text-ink-500 opacity-50 px-8 text-center">{{ article.title }}</span>
        </div>

        <div class="prose-like" v-html="renderedContent" />
      </div>
    </article>

    <div v-else-if="loading" class="py-20 text-center text-ink-400 text-sm">Загружаем…</div>

    <div v-else-if="notFound" class="py-20 text-center">
      <h1 class="font-display text-3xl font-semibold text-ink-900 mb-3">Статья не найдена</h1>
      <button class="btn-secondary mt-3" @click="router.push('/blog')">Вернуться в блог</button>
    </div>
  </div>
</template>
