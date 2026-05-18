<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const route = useRoute()

const nav = [
	{ label: 'Главная', to: '/' },
	{ label: 'Возможности', to: '/#features' },
	{ label: 'О проекте', to: '/about' },
	{ label: 'Блог', to: '/blog' },
]

const mobileOpen = ref(false)
watch(
	() => route.fullPath,
	() => (mobileOpen.value = false),
)
</script>

<template>
	<div class="min-h-screen flex flex-col bg-[#fdfdfd]">
		<header class="sticky top-0 z-40 pt-5 px-5">
			<div
				class="max-w-[1240px] mx-auto flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/60 backdrop-blur-xl shadow-[0_8px_30px_-12px_rgba(30,30,50,0.08),inset_0_1px_0_rgba(255,255,255,0.6)] ring-1 ring-ink-100"
			>
				<NuxtLink to="/" class="flex items-center pr-2">
					<img src="/full-logo.svg" alt="Guidio" class="h-8 w-auto" />
				</NuxtLink>

				<nav
					class="hidden lg:flex items-center gap-7 text-sm text-ink-600 ml-4"
				>
					<NuxtLink
						v-for="item in nav"
						:key="item.to"
						:to="item.to"
						class="hover:text-ink-900 transition-colors"
						:class="
							route.hash === item.to.replace('/', '') ||
							(item.to === '/' && route.path === '/' && !route.hash)
								? 'text-ink-900 font-medium'
								: ''
						"
					>
						{{ item.label }}
					</NuxtLink>
				</nav>

				<div class="flex-1" />

				<div class="hidden md:flex items-center gap-2">
					<template v-if="auth.isAuthenticated">
						<NuxtLink to="/app/start" class="btn-secondary"
							>В приложение</NuxtLink
						>
					</template>
					<template v-else>
						<NuxtLink to="/register" class="btn-secondary"
							>Зарегистрироваться</NuxtLink
						>
						<NuxtLink to="/login" class="btn-primary">Войти</NuxtLink>
					</template>
				</div>

				<button
					class="lg:hidden p-2 rounded-lg hover:bg-ink-100 text-ink-700"
					aria-label="Меню"
					@click="mobileOpen = !mobileOpen"
				>
					<svg
						width="22"
						height="22"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path v-if="!mobileOpen" d="M3 6h18M3 12h18M3 18h18" />
						<path v-else d="M6 6l12 12M6 18L18 6" />
					</svg>
				</button>
			</div>

			<div
				v-if="mobileOpen"
				class="lg:hidden mt-2 mx-auto max-w-[1240px] rounded-3xl bg-white shadow-soft ring-1 ring-ink-100"
			>
				<div class="px-6 py-4 flex flex-col gap-3">
					<NuxtLink
						v-for="item in nav"
						:key="item.to"
						:to="item.to"
						class="text-ink-700 py-1.5"
					>
						{{ item.label }}
					</NuxtLink>
					<div class="flex gap-2 pt-2">
						<template v-if="auth.isAuthenticated">
							<NuxtLink to="/app/start" class="btn-primary flex-1"
								>В приложение</NuxtLink
							>
						</template>
						<template v-else>
							<NuxtLink to="/register" class="btn-secondary flex-1"
								>Регистрация</NuxtLink
							>
							<NuxtLink to="/login" class="btn-primary flex-1">Войти</NuxtLink>
						</template>
					</div>
				</div>
			</div>
		</header>

		<main class="flex-1">
			<slot />
		</main>

		<SiteFooter />
	</div>
</template>
