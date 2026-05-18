<script setup lang="ts">
definePageMeta({ layout: 'default' })
useHead({ title: 'Контакты — Guidio' })

const form = reactive({
	name: '',
	email: '',
	topic: '',
	message: '',
})
const topics = [
	'Общий вопрос',
	'Сотрудничество',
	'Стать автором блога',
	'Сообщить об ошибке',
	'Другое',
]
const sent = ref(false)
const sending = ref(false)

async function submit() {
	if (!form.name.trim() || !form.email.trim() || !form.message.trim()) return
	sending.value = true
	// В реальном сервисе — отправка на backend endpoint или email сервис.
	await new Promise(r => setTimeout(r, 600))
	sending.value = false
	sent.value = true
	form.name = ''
	form.email = ''
	form.topic = ''
	form.message = ''
}

const channels = [
	{
		title: 'Почта',
		value: 'hello@guidio.io',
		hint: 'Отвечаем в течение рабочего дня',
		icon: 'mail',
	},
	{
		title: 'Telegram',
		value: '@guidio_team',
		hint: 'Для быстрых вопросов',
		icon: 'send',
	},
]
</script>

<template>
	<div class="bloom-full">
		<section class="py-20">
			<div class="max-w-[960px] mx-auto px-6 text-center">
				<h1
					class="font-display text-4xl sm:text-[48px] font-semibold text-ink-900 leading-tight"
				>
					Свяжитесь с нами <br />
					<span class="hand" style="font-size: 1.1em">мы на связи</span>
				</h1>
				<p class="mt-6 text-ink-500 max-w-xl mx-auto leading-relaxed">
					Напишите про продукт, сотрудничество или просто поделитесь идеей —
					отвечаем всем.
				</p>
			</div>
		</section>

		<section class="pb-20">
			<div class="max-w-[1100px] mx-auto px-6">
				<div class="grid lg:grid-cols-5 gap-6">
					<!-- Channels -->
					<div class="lg:col-span-2 space-y-3">
						<div
							v-for="c in channels"
							:key="c.title"
							class="card-flat p-5 flex items-start gap-4"
						>
							<div
								class="h-11 w-11 rounded-xl bg-linear-to-br from-[#4373E4] to-[#4373E4] text-white shrink-0 flex items-center justify-center"
							>
								<svg
									v-if="c.icon === 'mail'"
									width="18"
									height="18"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<rect x="3" y="5" width="18" height="14" rx="3" />
									<path d="m3 7 9 6 9-6" />
								</svg>
								<svg
									v-else-if="c.icon === 'send'"
									width="18"
									height="18"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<path d="m22 2-7 20-4-9-9-4 20-7Z" />
								</svg>
								<svg
									v-else
									width="18"
									height="18"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<path
										d="M12 21s-7-7.2-7-12a7 7 0 0 1 14 0c0 4.8-7 12-7 12Z"
									/>
									<circle cx="12" cy="9" r="2.5" />
								</svg>
							</div>
							<div class="flex-1 min-w-0">
								<div class="text-xs text-ink-400 uppercase tracking-wider">
									{{ c.title }}
								</div>
								<div
									class="font-display text-lg font-semibold text-ink-900 mt-0.5 break-all"
								>
									{{ c.value }}
								</div>
								<div class="text-xs text-ink-500 mt-1">{{ c.hint }}</div>
							</div>
						</div>
					</div>

					<!-- Form -->
					<div class="lg:col-span-3">
						<div class="card p-7 lg:p-9">
							<h2 class="font-display text-2xl font-semibold text-ink-900 mb-1">
								Написать в команду
							</h2>
							<p class="text-sm text-ink-500 mb-6">
								Заполните форму — мы вернёмся с ответом в ближайший рабочий
								день.
							</p>

							<form class="space-y-4" @submit.prevent="submit">
								<div class="grid sm:grid-cols-2 gap-3">
									<div>
										<div class="text-xs font-medium text-ink-700 mb-1.5">
											Имя
										</div>
										<UiInput v-model="form.name" placeholder="Мария" />
									</div>
									<div>
										<div class="text-xs font-medium text-ink-700 mb-1.5">
											Email
										</div>
										<UiInput
											v-model="form.email"
											type="email"
											placeholder="you@studio.com"
										/>
									</div>
								</div>
								<div>
									<div class="text-xs font-medium text-ink-700 mb-1.5">
										Тема
									</div>
									<FilterSelect
										v-model="form.topic"
										:options="topics"
										placeholder="Выберите тему"
									/>
								</div>
								<div>
									<div class="text-xs font-medium text-ink-700 mb-1.5">
										Сообщение
									</div>
									<UiInput
										v-model="form.message"
										:rows="5"
										placeholder="О чём хотите поговорить?"
									/>
								</div>
								<button
									type="submit"
									class="btn-primary px-8 py-3.5 text-base"
									:disabled="sending"
								>
									<span v-if="sending">Отправляем…</span>
									<span v-else>Отправить</span>
								</button>
								<Transition
									enter-active-class="transition duration-200"
									enter-from-class="opacity-0 translate-y-1"
								>
									<div
										v-if="sent"
										class="flex items-center gap-2 text-sm text-emerald-600"
									>
										<svg
											width="14"
											height="14"
											viewBox="0 0 24 24"
											fill="none"
											stroke="currentColor"
											stroke-width="2.4"
										>
											<path d="m5 12 5 5L20 7" />
										</svg>
										Спасибо! Мы получили ваше сообщение.
									</div>
								</Transition>
							</form>
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
</template>
