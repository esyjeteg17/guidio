<script setup lang="ts">
definePageMeta({ layout: 'default' })
useHead({ title: 'О проекте — Guidio' })

const values = [
	{
		title: 'Инструмент, а не генератор',
		desc: 'Мы не подменяем решение дизайнера. Мы помогаем его найти быстрее и аргументировать.',
		icon: 'spark',
	},
	{
		title: 'Живой диалог',
		desc: 'Подбор идёт в формате переписки: вы уточняете, сервис отвечает, вы принимаете решение.',
		icon: 'chat',
	},
	{
		title: 'Дизайн — это процесс',
		desc: 'Guidio помогает на всех этапах — от первого описания до финальных референсов и палитры.',
		icon: 'layers',
	},
]

const stats = [
	{ n: '10k+', label: 'вариантов шрифтовых пар' },
	{ n: '24/7', label: 'доступ к помощнику' },
	{ n: '2 мин', label: 'среднее время подбора' },
]
</script>

<template>
	<div class="bloom-full">
		<!-- Hero -->
		<section class="pt-20 pb-6">
			<div class="max-w-[960px] mx-auto px-6 text-center">
				<h1
					class="font-display text-4xl sm:text-[48px] font-semibold text-ink-900 leading-tight"
				>
					Guidio помогает быстрее находить <br />
					<span class="hand" style="font-size: 1.15em">стилевые решения</span>
				</h1>
				<p class="mt-6 text-lg text-ink-500 max-w-3xl mx-auto leading-relaxed">
					Мы делаем инструмент, который помогает дизайнерам сформулировать и
					зафиксировать визуальное направление: шрифтовую пару, палитру, мудборд
					— через удобный диалог.
				</p>
			</div>
		</section>

		<!-- Stats -->
		<section class="pt-2 pb-10">
			<div class="max-w-[1100px] mx-auto px-6">
				<div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
					<div
						v-for="s in stats"
						:key="s.label"
						class="card-flat p-7 text-center"
					>
						<div class="font-display text-4xl font-semibold text-ink-900">
							{{ s.n }}
						</div>
						<div class="text-sm text-ink-500 mt-1">{{ s.label }}</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Mission block -->
		<section class="py-20">
			<div class="max-w-[1100px] mx-auto px-6">
				<div class="grid lg:grid-cols-2 gap-10 items-center">
					<div>
						<h2
							class="font-display text-3xl sm:text-[36px] font-semibold text-ink-900 leading-tight"
						>
							Наша миссия
						</h2>
						<p class="mt-5 text-ink-600 leading-relaxed">
							Мы верим, что сильный стиль рождается из аргументированного
							выбора, а не из готовой подборки. Guidio — это пространство, где
							дизайнер задаёт вопрос, получает вариант, уточняет, пробует и
							приходит к решению, с которым удобно работать дальше.
						</p>
						<p class="mt-4 text-ink-600 leading-relaxed">
							Сервис создан выпускниками дизайн-школ вместе с практикующими
							арт-директорами. Мы собираем инструмент, которым хотим
							пользоваться сами.
						</p>
					</div>

					<div class="card p-6 relative">
						<div class="text-[10px] uppercase tracking-wider text-ink-400 mb-3">
							Guidio сегодня
						</div>
						<div class="space-y-3">
							<div class="card-flat p-4 flex items-center gap-3">
								<div
									class="h-10 w-10 rounded-xl bg-linear-to-br from-[#4373E4] to-[#4373E4] text-white flex items-center justify-center"
								>
									<svg
										width="16"
										height="16"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2.2"
									>
										<path d="M4 7V5h16v2M9 5v14M9 19h6M15 5v14" />
									</svg>
								</div>
								<div>
									<div class="font-semibold text-ink-900 text-sm">
										Подбор шрифтов
									</div>
									<div class="text-xs text-ink-500">
										Пары под характер, настроение, тип проекта
									</div>
								</div>
							</div>
							<div class="card-flat p-4 flex items-center gap-3">
								<div
									class="h-10 w-10 rounded-xl bg-linear-to-br from-bloom-pink to-bloom-lilac text-white flex items-center justify-center"
								>
									<svg
										width="16"
										height="16"
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
								</div>
								<div>
									<div class="font-semibold text-ink-900 text-sm">
										Генерация мудборда
									</div>
									<div class="text-xs text-ink-500">
										Визуальные направления и референсы
									</div>
								</div>
							</div>
							<div class="card-flat p-4 flex items-center gap-3">
								<div
									class="h-10 w-10 rounded-xl bg-linear-to-br from-bloom-mint to-emerald-400 text-white flex items-center justify-center"
								>
									<svg
										width="16"
										height="16"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2.2"
									>
										<circle cx="12" cy="12" r="9" />
										<path d="M12 3v18M3 12h18" />
									</svg>
								</div>
								<div>
									<div class="font-semibold text-ink-900 text-sm">
										Палитра и цвет
									</div>
									<div class="text-xs text-ink-500">
										Подбор и проверка цветовых решений
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Values -->
		<section class="py-20">
			<div class="max-w-[1100px] mx-auto px-6">
				<div class="max-w-xl mx-auto text-center mb-12">
					<h2
						class="font-display text-3xl sm:text-[36px] font-semibold text-ink-900"
					>
						Что для нас важно
					</h2>
				</div>
				<div class="grid md:grid-cols-3 gap-5">
					<div v-for="v in values" :key="v.title" class="card-flat p-7">
						<div
							class="h-11 w-11 rounded-xl bg-linear-to-br from-[#4373E4] to-[#4373E4] text-white flex items-center justify-center"
						>
							<FeatureIcon :name="v.icon" compact />
						</div>
						<h3 class="mt-5 font-display text-xl font-semibold text-ink-900">
							{{ v.title }}
						</h3>
						<p class="mt-2 text-sm text-ink-500 leading-relaxed">
							{{ v.desc }}
						</p>
					</div>
				</div>
			</div>
		</section>

		<!-- CTA -->
		<section class="py-20">
			<div class="max-w-[900px] mx-auto px-6">
				<div class="card p-10 text-center">
					<h2 class="font-display text-3xl font-semibold text-ink-900">
						Готовы попробовать?
					</h2>
					<p class="mt-3 text-ink-500 max-w-lg mx-auto">
						Создайте аккаунт и соберите первый мудборд или шрифтовую пару за
						пару минут.
					</p>
					<div class="mt-8 flex flex-wrap justify-center gap-3">
						<NuxtLink to="/register" class="btn-accent px-7 py-3.5 text-base"
							>Начать бесплатно</NuxtLink
						>
						<NuxtLink to="/contacts" class="btn-secondary px-7 py-3.5 text-base"
							>Связаться с нами</NuxtLink
						>
					</div>
				</div>
			</div>
		</section>
	</div>
</template>
