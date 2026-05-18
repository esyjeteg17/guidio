<script setup lang="ts">
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'default' })
useHead({ title: 'Guidio — твой помощник по подбору стилевых решений' })

interface Article {
	id: number
	title: string
	slug: string
	tag: string
	hue: string
	cover: string
	excerpt: string
}

const api = useApi()
const articles = ref<Article[]>([])

onMounted(async () => {
	try {
		const data = await api.get<{ results: Article[] } | Article[]>(
			'/blog/articles/',
		)
		const list = Array.isArray(data) ? data : data.results
		articles.value = list.slice(0, 3)
	} catch {
		// ignore
	}
})

const hueBg: Record<string, string> = {
	cream: 'bg-bloom-cream',
	mint: 'bg-bloom-mint/40',
	lilac: 'bg-bloom-lilac/30',
	peach: 'bg-bloom-pink/40',
	sky: 'bg-bloom-peri/30',
}

const features = [
	{
		title: 'Подбор по описанию',
		desc: 'Вы можете просто описать проект своими словами, а система подскажет подходящие шрифтовые решения.',
		icon: 'type',
	},
	{
		title: 'Гибкие фильтры',
		desc: 'Вы можете уточнить подбор по стилю, характеру, настроению и типу проекта.',
		icon: 'sliders',
	},
	{
		title: 'Генерация мудборда',
		desc: 'По вашему описанию сервис поможет собрать визуальное направление и референсы.',
		icon: 'grid',
	},
	{
		title: 'Работа в диалоге',
		desc: 'Вместо сложного интерфейса вы получаете понятный диалог, в котором удобно уточнять запрос и получать новые варианты.',
		icon: 'chat',
	},
	{
		title: 'Совместная работа',
		desc: 'Вы можете обсуждать идеи, сохранять решения и работать над проектом вместе с командой.',
		icon: 'team',
	},
	{
		title: 'Блог для дизайнеров',
		desc: 'В отдельном разделе доступны статьи по типографике, стилю, композиции и визуальным решениям.',
		icon: 'book',
	},
]

const steps = [
	{
		n: 1,
		title: 'Опишите задачу',
		desc: 'Расскажите, для какого проекта вы ищете решение и какое впечатление хотите передать.',
		icon: 'spark',
	},
	{
		n: 2,
		title: 'Уточните подбор',
		desc: 'Добавьте фильтры, чтобы сделать рекомендации точнее.',
		icon: 'filters',
	},
	{
		n: 3,
		title: 'Получите результат',
		desc: 'Сервис предложит шрифты, подскажет визуальное направление и поможет собрать мудборд.',
		icon: 'layers',
	},
]
</script>

<template>
	<div class="bloom-full overflow-x-clip">
		<!-- HERO -->
		<section>
			<div class="relative max-w-[1080px] mx-auto px-6 pt-36 pb-28">
				<!-- Floating chips pinned to the outer container so they don't overlap the title -->
				<div
					class="hidden lg:block absolute left-6 top-20 chip-white float-chip"
				>
					<span
						class="inline-flex items-center justify-center h-5 w-5 rounded-md bg-accent-100 text-accent-600"
					>
						<svg
							width="11"
							height="11"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2.5"
						>
							<path
								d="M12 3 13.5 9.5 20 11 13.5 12.5 12 19 10.5 12.5 4 11 10.5 9.5Z"
							/>
						</svg>
					</span>
					AI подбор
				</div>
				<div
					class="hidden lg:block absolute right-6 top-40 chip-white float-chip float-chip-delay-1"
				>
					<span
						class="inline-flex items-center justify-center h-5 w-5 rounded-md bg-bloom-mint text-emerald-700"
					>
						<svg
							width="11"
							height="11"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2.2"
						>
							<rect x="3" y="3" width="7" height="7" rx="1" />
							<rect x="14" y="3" width="7" height="7" rx="1" />
							<rect x="3" y="14" width="7" height="7" rx="1" />
							<rect x="14" y="14" width="7" height="7" rx="1" />
						</svg>
					</span>
					Moodboard
				</div>
				<div
					class="hidden lg:block absolute left-6 top-60 chip-white float-chip float-chip-delay-2"
				>
					<span
						class="inline-flex items-center justify-center h-5 w-5 rounded-md bg-bloom-lilac text-accent-700"
					>
						<svg
							width="11"
							height="11"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2.2"
						>
							<circle cx="9" cy="7" r="3" />
							<circle cx="17" cy="9" r="2.5" />
							<path d="M3 20a6 6 0 0 1 12 0M15 20a5 5 0 0 1 6-4.5" />
						</svg>
					</span>
					Командная работа
				</div>
				<div
					class="hidden lg:block absolute right-6 top-80 chip-white float-chip float-chip-delay-3"
				>
					<span
						class="inline-flex items-center justify-center h-5 w-5 rounded-md bg-bloom-pink text-pink-700"
					>
						<svg
							width="11"
							height="11"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2.2"
						>
							<path d="M3 6h18M7 12h10M10 18h4" />
						</svg>
					</span>
					Фильтры
				</div>

				<div class="relative max-w-[760px] mx-auto text-center">
					<h1
						class="font-display text-[40px] sm:text-5xl lg:text-[54px] font-semibold text-ink-900 leading-[1.15]"
					>
						Твой лучший помощник по подбору
						<span class="hand align-baseline" style="font-size: 1.2em"
							>стилевых решений</span
						>
					</h1>
					<p class="mt-6 text-ink-500 max-w-2xl mx-auto leading-relaxed">
						Опишите задачу своими словами, и Guidio подберёт шрифты и соберёт
						мудборд. Сервис помогает сформировать и зафиксировать дизайнерское
						решение, с которым удобно работать дальше. Никаких бесконечных
						поисков, только то, что подходит именно тебе.
					</p>

					<div class="mt-10 flex flex-wrap justify-center gap-3">
						<NuxtLink to="/register" class="btn-primary px-7 py-3.5 text-base"
							>Начать подбор</NuxtLink
						>
						<NuxtLink to="/#how" class="btn-secondary px-7 py-3.5 text-base"
							>Как это работает</NuxtLink
						>
					</div>
				</div>
			</div>
		</section>

		<!-- FEATURES -->
		<section id="features" class="py-20">
			<div class="max-w-[1200px] mx-auto px-6">
				<div class="max-w-2xl mx-auto text-center mb-14">
					<h2
						class="font-display text-3xl sm:text-[40px] font-semibold text-ink-900 leading-tight"
					>
						Все, что помогает быстрее найти<br />визуальное направление
					</h2>
					<p class="mt-4 text-ink-500">
						Сервис объединяет подбор шрифтов, фильтры, мудборды, командную
						работу и обучающие материалы в одном интерфейсе.
					</p>
				</div>

				<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
					<div v-for="f in features" :key="f.title" class="card-flat p-7">
						<FeatureIcon :name="f.icon" />
						<h3 class="mt-5 font-display text-xl font-semibold text-ink-900">
							{{ f.title }}
						</h3>
						<p class="mt-2 text-sm text-ink-500 leading-relaxed">
							{{ f.desc }}
						</p>
					</div>
				</div>
			</div>
		</section>

		<!-- HOW IT WORKS -->
		<section id="how" class="py-20">
			<div class="max-w-[1200px] mx-auto px-6">
				<div class="max-w-2xl mx-auto text-center mb-14">
					<h2
						class="font-display text-3xl sm:text-[40px] font-semibold text-ink-900"
					>
						Как это работает
					</h2>
					<p class="mt-4 text-ink-500">
						Весь процесс построен так, чтобы вы могли быстро перейти от идеи к
						осмысленному подбору шрифта или мудборда.
					</p>
				</div>

				<div class="grid md:grid-cols-3 gap-5">
					<div
						v-for="s in steps"
						:key="s.n"
						class="card p-7 relative overflow-hidden"
					>
						<span
							class="absolute -right-2 top-2 font-display text-[140px] leading-none font-semibold text-ink-100/80 select-none pointer-events-none"
							>{{ s.n }}</span
						>
						<div class="relative">
							<div
								class="h-11 w-11 rounded-xl bg-linear-to-br from-[#4373E4] to-[#4373E4] text-white flex items-center justify-center"
							>
								<FeatureIcon :name="s.icon" compact />
							</div>
							<h3 class="mt-5 font-display text-xl font-semibold text-ink-900">
								{{ s.title }}
							</h3>
							<p class="mt-2 text-sm text-ink-500 leading-relaxed">
								{{ s.desc }}
							</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- DIALOG PREVIEW -->
		<section class="py-20">
			<div class="max-w-[1200px] mx-auto px-6">
				<div class="max-w-4xl mx-auto text-center mb-12">
					<h2
						class="font-display text-3xl sm:text-[40px] font-semibold text-ink-900"
					>
						Удобный подбор в формате диалога
					</h2>
					<p class="mt-4 text-ink-500">
						Вы можете описать задачу, уточнить детали и сразу получить
						рекомендации. Такой формат делает работу с сервисом более
						естественной и удобной.
					</p>
				</div>
				<div class="max-w-[1100px] mx-auto">
					<DialogPreview />
				</div>
			</div>
		</section>

		<!-- TEAMS -->
		<section id="teams" class="py-20">
			<div
				class="max-w-[1200px] mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center"
			>
				<div class="card p-5">
					<div class="flex items-start justify-between mb-5">
						<div>
							<div class="font-display text-lg font-semibold text-ink-900">
								Проект: Rebranding 2024
							</div>
							<div class="text-xs text-ink-400 mt-0.5">
								Обновлено 2 часа назад
							</div>
						</div>
						<div class="flex items-center -space-x-2">
							<div
								class="h-7 w-7 rounded-full ring-2 ring-white bg-linear-to-br from-bloom-pink to-accent-400"
							/>
							<div
								class="h-7 w-7 rounded-full ring-2 ring-white bg-linear-to-br from-bloom-peri to-accent-600"
							/>
							<div
								class="h-7 w-7 rounded-full ring-2 ring-white bg-linear-to-br from-bloom-mint to-emerald-400"
							/>
							<span
								class="h-7 px-2 rounded-full ring-2 ring-white bg-ink-100 text-[10px] font-medium text-ink-700 flex items-center"
								>+3</span
							>
						</div>
					</div>

					<div class="card-flat p-4 mb-3 flex items-center gap-3">
						<div
							class="h-10 w-10 rounded-lg bg-ink-50 flex items-center justify-center font-display text-lg"
						>
							Aa
						</div>
						<div>
							<div class="text-sm font-semibold text-ink-900">
								Space Grotesk
							</div>
							<div class="text-xs text-ink-400">Добавлено Марией</div>
						</div>
					</div>

					<div class="flex gap-3">
						<div
							class="h-8 w-8 rounded-full bg-linear-to-br from-bloom-pink to-accent-400 shrink-0"
						/>
						<div>
							<div class="text-xs font-semibold text-ink-800">Мария</div>
							<div class="text-xs text-ink-500 mt-0.5 leading-relaxed">
								Давайте возьмём этот шрифт для акцентов, а в наборный пустим
								Onest. Смотрится очень свежо.
							</div>
						</div>
					</div>
				</div>

				<div>
					<h2
						class="font-display text-3xl sm:text-[40px] font-semibold text-ink-900"
					>
						Работайте над проектом вместе
					</h2>
					<p class="mt-4 text-ink-500 max-w-lg">
						Вы можете сохранять подборки, делиться результатами, обсуждать
						решения и формировать единое визуальное направление вместе с
						командой.
					</p>
					<div class="mt-8">
						<NuxtLink
							to="/app/team/new"
							class="btn-primary px-7 py-3.5 text-base"
							>Пригласить команду</NuxtLink
						>
					</div>
				</div>
			</div>
		</section>

		<!-- BLOG -->
		<section id="blog" class="py-20">
			<div class="max-w-[1200px] mx-auto px-6">
				<div class="max-w-2xl mx-auto text-center mb-12">
					<h2
						class="font-display text-3xl sm:text-[40px] font-semibold text-ink-900"
					>
						Полезные статьи
					</h2>
					<p class="mt-4 text-ink-500">
						Мы собрали полезные материалы, которые помогут вам увереннее
						работать со стилем и типографикой.
					</p>
				</div>
				<div v-if="!articles.length" class="text-center text-ink-400 text-sm">
					Скоро здесь появятся статьи.
				</div>
				<div v-else class="grid md:grid-cols-3 gap-5">
					<NuxtLink
						v-for="a in articles"
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
								class="font-display italic text-2xl text-ink-500 opacity-60 px-6 text-center"
							>
								{{ a.title.split(' ').slice(0, 3).join(' ') }}
							</span>
						</div>
						<div class="p-5">
							<div class="chip mb-3">{{ a.tag }}</div>
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
								class="mt-4 text-sm text-[#242424] inline-flex items-center gap-1 group-hover:gap-2 transition-all duration-200"
							>
								Читать статью
								<svg
									width="12"
									height="12"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									class="transition-transform duration-200 group-hover:translate-x-1"
								>
									<path d="M5 12h14M13 6l6 6-6 6" />
								</svg>
							</div>
						</div>
					</NuxtLink>
				</div>
				<div class="text-center mt-10">
					<NuxtLink to="/blog" class="btn-secondary">Все статьи</NuxtLink>
				</div>
			</div>
		</section>
	</div>
</template>
