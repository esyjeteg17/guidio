<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'default' })
useHead({ title: 'Приглашение в проект — Guidio' })

const route = useRoute()
const router = useRouter()
const api = useApi()
const auth = useAuthStore()

const token = computed(() => String(route.params.token))
const state = ref<'idle' | 'joining' | 'done' | 'error'>('idle')
const error = ref<string | null>(null)
const projectId = ref<number | null>(null)
const projectName = ref<string | null>(null)

async function ensureAuth() {
	if (!auth.ready) await auth.bootstrap()
	if (!auth.isAuthenticated) {
		await router.push({
			path: '/login',
			query: { redirect: `/invite/project/${token.value}` },
		})
		return false
	}
	return true
}

async function join() {
	error.value = null
	state.value = 'joining'
	try {
		const res = await api.post<{ id: number; name: string }>(
			'/projects/join/',
			{ invite_token: token.value },
		)
		projectId.value = res.id
		projectName.value = res.name
		state.value = 'done'
	} catch (e: any) {
		error.value = e?.data?.detail || 'Ссылка недействительна или проект удалён'
		state.value = 'error'
	}
}

onMounted(async () => {
	const ok = await ensureAuth()
	if (ok) join()
})
</script>

<template>
	<div
		class="bloom-full min-h-[calc(100vh-200px)] flex items-center justify-center py-16 px-6"
	>
		<div class="card w-full max-w-md p-8 text-center">
			<div
				class="h-14 w-14 rounded-2xl bg-linear-to-br from-[#4373E4] to-[#4373E4] text-white mx-auto flex items-center justify-center mb-5"
			>
				<svg
					width="22"
					height="22"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
					<circle cx="9" cy="7" r="4" />
					<path d="M22 11h-6M19 8v6" />
				</svg>
			</div>

			<template v-if="state === 'joining' || state === 'idle'">
				<h1 class="font-display text-2xl font-semibold text-ink-900">
					Подключаемся к проекту…
				</h1>
				<p class="text-sm text-ink-500 mt-2">Ещё секунду.</p>
			</template>

			<template v-else-if="state === 'done'">
				<h1 class="font-display text-2xl font-semibold text-ink-900">
					Вы в проекте
				</h1>
				<p class="text-sm text-ink-500 mt-2">
					Теперь вы — соавтор проекта «{{ projectName }}». Можете заходить в
					любой момент из раздела «Проекты».
				</p>
				<div class="mt-6 flex gap-2 justify-center">
					<NuxtLink :to="`/app/projects/${projectId}`" class="btn-accent"
						>Открыть проект</NuxtLink
					>
					<NuxtLink to="/app/projects" class="btn-secondary">К списку</NuxtLink>
				</div>
			</template>

			<template v-else>
				<h1 class="font-display text-2xl font-semibold text-ink-900">
					Не получилось присоединиться
				</h1>
				<p class="text-sm text-red-500 mt-2">{{ error }}</p>
				<div class="mt-6 flex gap-2 justify-center">
					<button class="btn-secondary" @click="join">
						Попробовать ещё раз
					</button>
					<NuxtLink to="/app/projects" class="btn-ghost">К проектам</NuxtLink>
				</div>
			</template>
		</div>
	</div>
</template>
