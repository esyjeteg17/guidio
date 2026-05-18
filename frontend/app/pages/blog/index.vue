<script setup lang="ts">
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'default' })
useHead({ title: 'Блог — Guidio' })

interface Article {
	id: number
	title: string
	slug: string
	tag: string
	hue: string
	cover: string
	excerpt: string
	author: string
	read_minutes: number
	published_at: string
}

const api = useApi()
const articles = ref<Article[]>([])
const loading = ref(true)
const query = ref('')
const activeTag = ref<string>('all')

const allowedTags = ['Визуальный стиль', 'Типографика']

async function load() {
	loading.value = true
	try {
		const data = await api.get<{ results: Article[] } | Article[]>(
			'/blog/articles/',
		)
		const list = Array.isArray(data) ? data : data.results
		articles.value = list.filter(a => allowedTags.includes(a.tag))
	} finally {
		loading.value = false
	}
}

const tags = computed(() => {
	const set = new Set<string>()
	for (const a of articles.value) {
		if (allowedTags.includes(a.tag)) set.add(a.tag)
	}
	return ['all', ...Array.from(set)]
})

const filtered = computed(() => {
	let list = articles.value
	if (activeTag.value !== 'all')
		list = list.filter(a => a.tag === activeTag.value)
	if (query.value.trim()) {
		const q = query.value.toLowerCase()
		list = list.filter(
			a =>
				a.title.toLowerCase().includes(q) ||
				(a.excerpt || '').toLowerCase().includes(q),
		)
	}
	return list
})

function formatDate(s: string) {
	return new Date(s).toLocaleDateString('ru-RU', {
		day: 'numeric',
		month: 'long',
		year: 'numeric',
	})
}

const hueBg: Record<string, string> = {
	cream: 'bg-bloom-cream',
	mint: 'bg-bloom-mint/40',
	lilac: 'bg-bloom-lilac/30',
	peach: 'bg-bloom-pink/40',
	sky: 'bg-bloom-peri/30',
}

onMounted(load)
</script>

<template>
	<div class="bloom-full">
		<section class="py-20">
			<div class="max-w-[1200px] mx-auto px-6">
				<div class="max-w-2xl mx-auto text-center mb-12">
					<h1
						class="font-display text-4xl sm:text-[44px] font-semibold text-ink-900 leading-tight"
					>
						Полезные материалы <br />
						<span class="hand" style="font-size: 1.1em">для дизайнеров</span>
					</h1>
					<p class="mt-5 text-ink-500">
						Статьи по типографике, стилю, композиции и подбору визуальных
						решений.
					</p>
				</div>

				<div class="flex items-center justify-between gap-4 mb-10 flex-wrap">
					<div class="flex flex-wrap gap-2">
						<button
							v-for="t in tags"
							:key="t"
							class="px-4 py-1.5 rounded-full text-sm font-medium transition-colors cursor-pointer"
							:class="
								activeTag === t
									? 'bg-ink-900 text-white'
									: 'bg-white ring-1 ring-ink-200 text-ink-600 hover:ring-ink-300'
							"
							@click="activeTag = t"
						>
							{{ t === 'all' ? 'Все' : t }}
						</button>
					</div>
					<div class="w-full sm:w-72">
						<UiInput v-model="query" placeholder="Поиск по статьям">
							<template #prefix>
								<svg
									width="14"
									height="14"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<circle cx="11" cy="11" r="7" />
									<path d="m21 21-4.3-4.3" />
								</svg>
							</template>
						</UiInput>
					</div>
				</div>

				<div v-if="loading" class="text-ink-400 text-sm">Загружаем…</div>

				<div
					v-else-if="!filtered.length"
					class="card-flat p-12 text-center text-ink-500 text-sm"
				>
					Ничего не нашлось.
				</div>

				<div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
					<NuxtLink
						v-for="a in filtered"
						:key="a.id"
						:to="`/blog/${a.slug}`"
						class="card-flat overflow-hidden group"
					>
						<div
							class="aspect-4/3 flex items-center justify-center relative"
							:class="hueBg[a.hue] || 'bg-ink-50'"
						>
							<img
								v-if="a.cover"
								:src="a.cover"
								:alt="a.title"
								class="absolute inset-0 w-full h-full object-cover"
								loading="lazy"
							/>
							<span
								v-else
								class="font-display italic text-3xl text-ink-500 opacity-60 px-6 text-center"
							>
								{{ a.title.split(' ').slice(0, 3).join(' ') }}
							</span>
						</div>
						<div class="p-5">
							<div class="flex items-center gap-2 mb-3">
								<div class="chip">{{ a.tag }}</div>
								<span class="text-[11px] text-ink-400"
									>{{ a.read_minutes }} мин чтения</span
								>
							</div>
							<h3
								class="font-display text-lg font-semibold text-ink-900 group-hover:text-accent-600 transition-colors leading-snug"
							>
								{{ a.title }}
							</h3>
							<p
								v-if="a.excerpt"
								class="text-sm text-ink-500 mt-2 line-clamp-2"
							>
								{{ a.excerpt }}
							</p>
							<div
								class="flex items-center justify-between mt-4 text-[11px] text-ink-400"
							>
								<span>{{ a.author }}</span>
								<span>{{ formatDate(a.published_at) }}</span>
							</div>
						</div>
					</NuxtLink>
				</div>
			</div>
		</section>
	</div>
</template>
