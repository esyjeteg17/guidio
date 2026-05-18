<script setup lang="ts">
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'app', middleware: 'auth' })
useHead({ title: 'Новый подбор — Guidio' })

const router = useRouter()
const api = useApi()

const showNewProject = ref(false)
const pickedMode = ref<'fonts' | 'moodboard'>('fonts')

function pick(mode: 'fonts' | 'moodboard') {
  pickedMode.value = mode
  showNewProject.value = true
}

async function onProjectCreated(project: { id: number }) {
  const base = pickedMode.value === 'fonts' ? '/app/fonts' : '/app/moodboard'
  await router.push(`${base}?project=${project.id}`)
}

interface Article {
  id: number
  title: string
  slug: string
  tag: string
  hue: string
  cover: string
  excerpt: string
}

const articles = ref<Article[]>([])

onMounted(async () => {
  try {
    const data = await api.get<{ results: Article[] } | Article[]>('/blog/articles/')
    const list = Array.isArray(data) ? data : data.results
    articles.value = list.slice(0, 3)
  } catch { /* ignore */ }
})

const hueBg: Record<string, string> = {
  cream: 'bg-bloom-cream',
  mint: 'bg-bloom-mint/40',
  lilac: 'bg-bloom-lilac/30',
  peach: 'bg-bloom-pink/40',
  sky: 'bg-bloom-peri/30',
}
</script>

<template>
  <div class="min-h-full flex flex-col">
    <PageHeader :crumbs="[{ label: 'Новый подбор' }]" />

    <div class="flex-1 px-6 lg:px-10 py-10 lg:py-14">
      <div class="max-w-[960px] mx-auto">
        <div class="text-center mb-12">
          <h1 class="font-display text-4xl sm:text-5xl font-semibold text-ink-900">
            Выбери сценарий — и начнём
          </h1>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
          <button
            class="card-flat p-5 text-left transition-all duration-200 hover:shadow-card hover:-translate-y-1 hover:ring-2 hover:ring-accent-400 cursor-pointer"
            @click="pick('moodboard')"
          >
            <div class="aspect-[5/3] rounded-2xl bg-ink-50 relative overflow-hidden mb-5">
              <div class="absolute left-[22%] top-[20%] h-20 w-14 rounded-xl bg-linear-to-br from-bloom-lilac to-bloom-peri rotate-[-12deg] shadow-lg" />
              <div class="absolute left-[35%] top-[30%] h-24 w-20 rounded-xl bg-linear-to-br from-accent-300 to-accent-500 shadow-lg" />
              <div class="absolute right-[20%] top-[18%] h-20 w-20 rounded-xl bg-linear-to-br from-bloom-pink to-accent-400 rotate-[14deg] shadow-lg" />
              <div class="absolute left-1/2 bottom-[18%] -translate-x-1/2 h-12 w-12 rounded-full bg-white ring-2 ring-accent-400 flex items-center justify-center text-accent-600 shadow-xl">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="9" />
                  <circle cx="8" cy="10" r="1.4" fill="currentColor" />
                  <circle cx="16" cy="10" r="1.4" fill="currentColor" />
                  <circle cx="12" cy="16" r="1.4" fill="currentColor" />
                </svg>
              </div>
            </div>
            <div class="font-display text-xl font-semibold text-ink-900">Генерация мудборда</div>
            <p class="mt-2 text-sm text-ink-500 leading-relaxed">
              Соберите визуальное направление, референсы и цветовую палитру по краткому описанию вашего проекта.
            </p>
          </button>

          <button
            class="card-flat p-5 text-left transition-all duration-200 hover:shadow-card hover:-translate-y-1 hover:ring-2 hover:ring-accent-400 cursor-pointer"
            @click="pick('fonts')"
          >
            <div class="aspect-[5/3] rounded-2xl bg-ink-50 relative overflow-hidden mb-5 flex items-center justify-center">
              <span class="font-display text-[120px] leading-none text-ink-800 mr-2">A</span>
              <span class="font-display italic text-[110px] leading-none text-accent-500">a</span>
              <span class="chip-white absolute bottom-4 right-4 !py-1.5 !px-3 gap-1.5">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M4 7V5h16v2M9 5v14M9 19h6M15 5v14"/></svg>
                AI Подбор
              </span>
            </div>
            <div class="font-display text-xl font-semibold text-ink-900">Подбор шрифтов</div>
            <p class="mt-2 text-sm text-ink-500 leading-relaxed">
              Найдите идеальную типографику под характер, стиль и настроение вашего бренда за пару секунд.
            </p>
          </button>
        </div>

        <!-- Blog block -->
        <div v-if="articles.length" class="mt-16">
          <div class="flex items-end justify-between mb-6">
            <h2 class="font-display text-2xl font-semibold text-ink-900">Блог</h2>
            <NuxtLink to="/blog" class="text-sm text-ink-500 hover:text-ink-800">Все статьи</NuxtLink>
          </div>
          <div class="grid md:grid-cols-3 gap-5">
            <NuxtLink
              v-for="a in articles" :key="a.id"
              :to="`/blog/${a.slug}`"
              class="card-flat overflow-hidden group"
            >
              <div class="aspect-4/3 flex items-center justify-center relative" :class="hueBg[a.hue] || 'bg-ink-50'">
                <img v-if="a.cover" :src="a.cover" :alt="a.title" class="absolute inset-0 w-full h-full object-cover" loading="lazy" />
                <span v-else class="font-display italic text-xl text-ink-500 opacity-60 px-5 text-center">
                  {{ a.title.split(' ').slice(0, 3).join(' ') }}
                </span>
              </div>
              <div class="p-5">
                <div class="chip mb-3">{{ a.tag }}</div>
                <h3 class="font-display text-base font-semibold text-ink-900 group-hover:text-accent-600 transition-colors leading-snug">{{ a.title }}</h3>
                <p v-if="a.excerpt" class="text-xs text-ink-500 mt-2 line-clamp-2">{{ a.excerpt }}</p>
                <div class="mt-3 text-sm text-[#242424] inline-flex items-center gap-1 group-hover:gap-2 transition-all duration-200">
                  Читать статью
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="transition-transform duration-200 group-hover:translate-x-1"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
                </div>
              </div>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <NewProjectModal
      v-model:open="showNewProject"
      :default-kind="pickedMode"
      title="Новый проект"
      description="Введите название — затем сразу перейдём к подбору."
      @created="onProjectCreated"
    />
  </div>
</template>
