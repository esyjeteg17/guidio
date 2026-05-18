<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: false, middleware: 'guest' })
useHead({ title: 'Вход — Guidio' })

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)

async function onSubmit() {
	error.value = null
	loading.value = true
	try {
		await auth.login(email.value.trim(), password.value)
		const redirect = (route.query.redirect as string) || '/app/start'
		await router.push(redirect)
	} catch (e: any) {
		error.value = e?.data?.detail || 'Неверный email или пароль'
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

			<div class="flex-1 flex items-center justify-center">
				<div class="w-full max-w-100">
					<h1
						class="font-display text-4xl font-semibold text-center text-ink-900 mb-2"
					>
						Вход в аккаунт
					</h1>
					<p class="text-center text-sm text-ink-500 mb-10">
						Рады видеть вас снова
					</p>

					<form class="space-y-5" @submit.prevent="onSubmit">
						<div>
							<div class="text-sm text-ink-700 mb-1.5">Электронная почта</div>
							<UiInput
								v-model="email"
								type="email"
								autocomplete="email"
								placeholder="Введите адрес"
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
						</div>

						<div>
							<div class="flex items-center justify-between mb-1.5">
								<span class="text-sm text-ink-700">Пароль</span>
								<a href="#" class="text-sm text-accent-600 hover:underline"
									>Забыли пароль?</a
								>
							</div>
							<UiInput
								v-model="password"
								:type="showPassword ? 'text' : 'password'"
								autocomplete="current-password"
								placeholder="Введите пароль"
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
						</div>

						<p v-if="error" class="text-sm text-red-500">{{ error }}</p>

						<button
							type="submit"
							class="btn-accent w-full py-3.5 text-base"
							:disabled="loading"
						>
							<span v-if="loading">Входим…</span>
							<span v-else>Продолжить</span>
						</button>
					</form>

					<p class="mt-6 text-center text-sm text-ink-500">
						Впервые здесь?
						<NuxtLink
							to="/register"
							class="text-accent-600 font-medium hover:underline"
							>Создайте аккаунт</NuxtLink
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
