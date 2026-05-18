<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: false, middleware: 'guest' })
useHead({ title: 'Регистрация — Guidio' })

const auth = useAuthStore()
const router = useRouter()

const form = reactive({
	email: '',
	username: '',
	full_name: '',
	role: '',
	password: '',
	password_confirm: '',
})
const agree = ref(false)
const showPassword = ref(false)
const showConfirm = ref(false)
const loading = ref(false)
const errors = ref<Record<string, string>>({})

const passwordStrength = computed(() => {
	const p = form.password
	if (!p) return { level: 0, label: '', color: '' }
	let score = 0
	if (p.length >= 8) score++
	if (/[a-zа-я]/i.test(p) && /[A-ZА-Я]/.test(p)) score++
	if (/\d/.test(p)) score++
	if (/[^\w\s]/.test(p)) score++
	if (score <= 1) return { level: 1, label: 'слабый', color: 'bg-red-400' }
	if (score === 2) return { level: 2, label: 'средний', color: 'bg-amber-400' }
	if (score === 3)
		return { level: 3, label: 'хороший', color: 'bg-emerald-400' }
	return { level: 4, label: 'сильный', color: 'bg-emerald-500' }
})

const passwordsMatch = computed(
	() => !form.password_confirm || form.password === form.password_confirm,
)

async function onSubmit() {
	errors.value = {}
	if (!passwordsMatch.value) {
		errors.value.password_confirm = 'Пароли не совпадают'
		return
	}
	if (!agree.value) {
		errors.value._global = 'Подтвердите согласие с условиями'
		return
	}
	if (!form.username.trim()) form.username = form.email.split('@')[0] || 'user'
	if (!form.full_name.trim()) form.full_name = form.username

	loading.value = true
	try {
		await auth.register({ ...form })
		await router.push('/app/start')
	} catch (e: any) {
		const data = e?.data
		if (data && typeof data === 'object') {
			for (const key of Object.keys(data)) {
				errors.value[key] = Array.isArray(data[key])
					? data[key][0]
					: String(data[key])
			}
		} else {
			errors.value._global = 'Не удалось зарегистрироваться'
		}
	} finally {
		loading.value = false
	}
}
</script>

<template>
	<div class="min-h-screen flex">
		<div class="w-full lg:w-1/2 flex flex-col px-6 sm:px-16 py-8 bg-white">
			<NuxtLink to="/" class="inline-flex items-center text-ink-900">
				<img src="/full-logo.svg" alt="Guidio" class="h-9 w-auto" />
			</NuxtLink>

			<div class="flex-1 flex items-center justify-center py-10">
				<div class="w-full max-w-110">
					<h1
						class="font-display text-4xl font-semibold text-center text-ink-900 mb-2"
					>
						Создать аккаунт
					</h1>
					<p class="text-center text-sm text-ink-500 mb-8">
						Пара шагов — и вы сможете подбирать стилевые решения
					</p>

					<form class="space-y-4" @submit.prevent="onSubmit">
						<div class="grid grid-cols-2 gap-3">
							<div>
								<div class="text-sm text-ink-700 mb-1.5">Имя</div>
								<UiInput
									v-model="form.full_name"
									autocomplete="name"
									placeholder="Мария"
								/>
								<p v-if="errors.full_name" class="text-xs text-red-500 mt-1">
									{{ errors.full_name }}
								</p>
							</div>
							<div>
								<div class="text-sm text-ink-700 mb-1.5">Ник</div>
								<UiInput
									v-model="form.username"
									autocomplete="username"
									placeholder="maria"
								/>
								<p v-if="errors.username" class="text-xs text-red-500 mt-1">
									{{ errors.username }}
								</p>
							</div>
						</div>

						<div>
							<div class="text-sm text-ink-700 mb-1.5">Электронная почта</div>
							<UiInput
								v-model="form.email"
								type="email"
								autocomplete="email"
								placeholder="you@studio.com"
							>
								<template #prefix>
									<svg
										width="16"
										height="16"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="1.8"
									>
										<rect x="3" y="5" width="18" height="14" rx="3" />
										<path d="m3 7 9 6 9-6" />
									</svg>
								</template>
							</UiInput>
							<p v-if="errors.email" class="text-xs text-red-500 mt-1">
								{{ errors.email }}
							</p>
						</div>

						<div>
							<div class="text-sm text-ink-700 mb-1.5">
								Роль
								<span class="text-ink-400 font-normal">(необязательно)</span>
							</div>
							<UiInput
								v-model="form.role"
								placeholder="Brand Designer, Art Director, Student…"
							/>
						</div>

						<div>
							<div class="text-sm text-ink-700 mb-1.5">Пароль</div>
							<UiInput
								v-model="form.password"
								:type="showPassword ? 'text' : 'password'"
								autocomplete="new-password"
								placeholder="Не меньше 8 символов"
							>
								<template #prefix>
									<svg
										width="16"
										height="16"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="1.8"
									>
										<rect x="4" y="11" width="16" height="10" rx="2" />
										<path d="M8 11V7a4 4 0 0 1 8 0v4" />
									</svg>
								</template>
								<template #suffix>
									<button
										type="button"
										class="text-ink-400 hover:text-ink-600 p-1"
										@click="showPassword = !showPassword"
									>
										<svg
											v-if="!showPassword"
											width="18"
											height="18"
											viewBox="0 0 24 24"
											fill="none"
											stroke="currentColor"
											stroke-width="1.8"
										>
											<path
												d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"
											/>
											<circle cx="12" cy="12" r="3" />
										</svg>
										<svg
											v-else
											width="18"
											height="18"
											viewBox="0 0 24 24"
											fill="none"
											stroke="currentColor"
											stroke-width="1.8"
										>
											<path
												d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-6.5 0-10-7-10-7a19.8 19.8 0 0 1 5.17-5.94"
											/>
											<path
												d="M9.9 4.24A10.9 10.9 0 0 1 12 4c6.5 0 10 7 10 7a19.8 19.8 0 0 1-3.17 4.19"
											/>
											<path d="m1 1 22 22" />
										</svg>
									</button>
								</template>
							</UiInput>
							<div v-if="form.password" class="flex items-center gap-2 mt-2">
								<div class="flex gap-1 flex-1">
									<div
										v-for="i in 4"
										:key="i"
										class="flex-1 h-1 rounded-full bg-ink-100"
									>
										<div
											class="h-full rounded-full transition-all"
											:class="[
												i <= passwordStrength.level
													? passwordStrength.color
													: '',
											]"
											:style="{
												width: i <= passwordStrength.level ? '100%' : '0%',
											}"
										/>
									</div>
								</div>
								<span class="text-[11px] text-ink-500">{{
									passwordStrength.label
								}}</span>
							</div>
							<p v-if="errors.password" class="text-xs text-red-500 mt-1">
								{{ errors.password }}
							</p>
						</div>

						<div>
							<div class="text-sm text-ink-700 mb-1.5">Повторите пароль</div>
							<UiInput
								v-model="form.password_confirm"
								:type="showConfirm ? 'text' : 'password'"
								autocomplete="new-password"
								placeholder="Ещё раз тот же пароль"
							>
								<template #prefix>
									<svg
										width="16"
										height="16"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="1.8"
									>
										<path d="m5 12 5 5L20 7" />
									</svg>
								</template>
								<template #suffix>
									<button
										type="button"
										class="text-ink-400 hover:text-ink-600 p-1"
										@click="showConfirm = !showConfirm"
									>
										<svg
											v-if="!showConfirm"
											width="18"
											height="18"
											viewBox="0 0 24 24"
											fill="none"
											stroke="currentColor"
											stroke-width="1.8"
										>
											<path
												d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"
											/>
											<circle cx="12" cy="12" r="3" />
										</svg>
										<svg
											v-else
											width="18"
											height="18"
											viewBox="0 0 24 24"
											fill="none"
											stroke="currentColor"
											stroke-width="1.8"
										>
											<path
												d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-6.5 0-10-7-10-7a19.8 19.8 0 0 1 5.17-5.94"
											/>
											<path
												d="M9.9 4.24A10.9 10.9 0 0 1 12 4c6.5 0 10 7 10 7a19.8 19.8 0 0 1-3.17 4.19"
											/>
											<path d="m1 1 22 22" />
										</svg>
									</button>
								</template>
							</UiInput>
							<p v-if="!passwordsMatch" class="text-xs text-red-500 mt-1">
								Пароли не совпадают
							</p>
							<p
								v-else-if="errors.password_confirm"
								class="text-xs text-red-500 mt-1"
							>
								{{ errors.password_confirm }}
							</p>
						</div>

						<label
							class="flex items-start gap-2.5 text-sm text-ink-600 cursor-pointer select-none pt-1"
						>
							<span class="relative flex items-center justify-center mt-0.5">
								<input
									v-model="agree"
									type="checkbox"
									class="peer h-4 w-4 appearance-none rounded-md ring-1 ring-ink-300 checked:bg-accent-500 checked:ring-accent-500 transition-colors cursor-pointer"
								/>
								<svg
									class="absolute h-3 w-3 text-white pointer-events-none opacity-0 peer-checked:opacity-100 transition-opacity"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="3.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								>
									<path d="m5 12 5 5L20 7" />
								</svg>
							</span>
							<span class="leading-snug">
								Я согласен(а) с
								<a href="#" class="text-accent-600 hover:underline"
									>условиями использования</a
								>
								и
								<a href="#" class="text-accent-600 hover:underline"
									>политикой конфиденциальности</a
								>
							</span>
						</label>

						<p
							v-if="errors._global || errors.detail"
							class="text-sm text-red-500"
						>
							{{ errors._global || errors.detail }}
						</p>

						<button
							type="submit"
							class="btn-accent w-full py-3.5 text-base"
							:disabled="loading"
						>
							<span v-if="loading">Регистрируем…</span>
							<span v-else>Создать аккаунт</span>
						</button>
					</form>

					<p class="mt-6 text-center text-sm text-ink-500">
						Уже есть аккаунт?
						<NuxtLink
							to="/login"
							class="text-accent-600 font-medium hover:underline"
							>Войти</NuxtLink
						>
					</p>
				</div>
			</div>
		</div>

		<div class="hidden lg:block lg:w-1/2">
			<AuthShowcase />
		</div>
	</div>
</template>
