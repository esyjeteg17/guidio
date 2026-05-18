<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import { useAuthStore } from '~/stores/auth'

interface RecentProject {
	id: number
	name: string
	kind: string
	updated_at: string
}

interface ProjectBrief {
	id: number
	name: string
	description?: string
	kind: string
	is_favorite?: boolean
	updated_at: string
}

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const api = useApi()

const sidebarOpen = ref(false)
const recentProjects = ref<RecentProject[]>([])
const activeProjectId = ref<number | null>(null)

/* --------------------- Project search --------------------- */
const projectSearchOpen = ref(false)
const projectQuery = ref('')
const projectsList = ref<ProjectBrief[]>([])
const projectsLoading = ref(false)
const projectSearchPopover = ref<HTMLElement | null>(null)
const projectSearchToggle = ref<HTMLElement | null>(null)

async function loadProjectsList() {
	projectsLoading.value = true
	try {
		const data = await api.get<{ results: ProjectBrief[] } | ProjectBrief[]>(
			'/projects/',
		)
		projectsList.value = Array.isArray(data) ? data : data.results
	} catch {
		projectsList.value = []
	} finally {
		projectsLoading.value = false
	}
}

const filteredProjects = computed(() => {
	const q = projectQuery.value.trim().toLowerCase()
	const list = projectsList.value
	if (!q) return list.slice(0, 10)
	return list
		.filter(
			p =>
				p.name.toLowerCase().includes(q) ||
				(p.description || '').toLowerCase().includes(q),
		)
		.slice(0, 20)
})

function toggleProjectSearch() {
	projectSearchOpen.value = !projectSearchOpen.value
	if (projectSearchOpen.value && !projectsList.value.length) loadProjectsList()
}

function openProject(p: ProjectBrief) {
	projectSearchOpen.value = false
	projectQuery.value = ''
	router.push(`/app/projects/${p.id}`)
}

function onProjectSearchClickOutside(e: MouseEvent) {
	if (!projectSearchOpen.value) return
	const t = e.target as Node
	if (projectSearchPopover.value?.contains(t)) return
	if (projectSearchToggle.value?.contains(t)) return
	projectSearchOpen.value = false
}

function onProjectSearchEsc(e: KeyboardEvent) {
	if (e.key === 'Escape') projectSearchOpen.value = false
}

onMounted(() => {
	document.addEventListener('mousedown', onProjectSearchClickOutside)
	document.addEventListener('keydown', onProjectSearchEsc)
})
onBeforeUnmount(() => {
	document.removeEventListener('mousedown', onProjectSearchClickOutside)
	document.removeEventListener('keydown', onProjectSearchEsc)
})

async function resolveCurrentProjectId(): Promise<number | null> {
	const path = route.path
	// Direct project page
	const projectMatch = path.match(/^\/app\/projects\/(\d+)/)
	if (projectMatch && projectMatch[1]) return Number(projectMatch[1])

	// Chat session pages — look up session to find its project
	const sessionMatch = path.match(/^\/app\/(fonts|moodboard)\/(\d+)/)
	if (sessionMatch && sessionMatch[2]) {
		try {
			const session = await api.get<{ project: number | null }>(
				`/ai/sessions/${sessionMatch[2]}/`,
			)
			return session.project ?? null
		} catch {
			return null
		}
	}

	// Empty chat with ?project= hint
	const q = route.query.project
	const v = Array.isArray(q) ? q[0] : q
	if (v) return Number(v)

	return null
}

async function loadRecent() {
	try {
		const data = await api.get<{ results: RecentProject[] } | RecentProject[]>(
			'/projects/',
		)
		const list = Array.isArray(data) ? data : data.results
		const sorted = list
			.slice()
			.sort((a: any, b: any) =>
				(b.updated_at || '').localeCompare(a.updated_at || ''),
			)

		const activeId = await resolveCurrentProjectId()
		activeProjectId.value = activeId
		if (activeId) {
			const idx = sorted.findIndex(p => p.id === activeId)
			let active: RecentProject | null = null
			if (idx >= 0) {
				active = sorted.splice(idx, 1)[0] ?? null
			} else {
				try {
					active = await api.get<RecentProject>(`/projects/${activeId}/`)
				} catch {
					active = null
				}
			}
			if (active) sorted.unshift(active)
		}

		recentProjects.value = sorted.slice(0, 3)
	} catch {
		recentProjects.value = []
	}
}

/* --------------------- New project modal --------------------- */
const showNewProject = ref(false)

function openNewProject() {
	showNewProject.value = true
}

async function onProjectCreated(project: { id: number }) {
	await router.push(`/app/projects/${project.id}`)
}

watch(
	() => route.fullPath,
	() => {
		sidebarOpen.value = false
		loadRecent()
	},
)

onMounted(loadRecent)
</script>

<template>
	<div class="h-screen flex bg-[#fdfdfd]">
		<div
			v-if="sidebarOpen"
			class="fixed inset-0 z-30 bg-ink-900/30 backdrop-blur-sm lg:hidden"
			@click="sidebarOpen = false"
		/>

		<aside
			class="sidebar-raleway fixed lg:sticky top-0 left-0 z-40 h-screen w-[260px] bg-[#fafafa] border-r border-[#dfdfdf] flex flex-col transition-transform duration-200 ease-out"
			:class="
				sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
			"
		>
			<div class="p-4 flex items-center justify-between">
				<NuxtLink to="/" class="flex items-center text-ink-900">
					<img src="/full-logo.svg" alt="Guidio" class="h-9 w-auto" />
				</NuxtLink>
			</div>

			<!-- Project search -->
			<div class="px-4 pb-3 relative">
				<button
					ref="projectSearchToggle"
					class="flex items-center gap-2.5 w-full px-3 py-2.5 rounded-xl text-sm transition-colors ring-1 ring-[#dfdfdf]"
					@click="toggleProjectSearch"
				>
					<svg
						width="14"
						height="14"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						class="shrink-0"
					>
						<circle cx="11" cy="11" r="7" />
						<path d="m21 21-4.3-4.3" />
					</svg>
					<span class="flex-1 text-left">Поиск по проектам</span>
				</button>

				<Transition
					enter-active-class="transition duration-150 ease-out"
					enter-from-class="opacity-0 -translate-y-1"
					enter-to-class="opacity-100 translate-y-0"
					leave-active-class="transition duration-100 ease-in"
					leave-from-class="opacity-100 translate-y-0"
					leave-to-class="opacity-0 -translate-y-1"
				>
					<div
						v-if="projectSearchOpen"
						ref="projectSearchPopover"
						class="absolute left-4 right-4 top-full mt-1 card p-3 z-30"
					>
						<div
							class="flex items-center gap-2 px-3 py-2 rounded-xl bg-ink-50 mb-2"
						>
							<svg
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								class="text-ink-400 shrink-0"
							>
								<circle cx="11" cy="11" r="7" />
								<path d="m21 21-4.3-4.3" />
							</svg>
							<input
								v-model="projectQuery"
								type="text"
								placeholder="Название проекта..."
								class="flex-1 bg-transparent text-sm placeholder:text-ink-400 focus:outline-none"
								autofocus
							/>
							<button
								v-if="projectQuery"
								class="text-ink-400 hover:text-ink-700 cursor-pointer"
								title="Очистить"
								@click="projectQuery = ''"
							>
								<svg
									width="12"
									height="12"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2.4"
								>
									<path d="M18 6 6 18M6 6l12 12" />
								</svg>
							</button>
						</div>

						<div
							v-if="projectsLoading"
							class="px-3 py-4 text-xs text-ink-400 text-center"
						>
							Загружаем…
						</div>

						<div
							v-else-if="!filteredProjects.length"
							class="px-3 py-6 text-xs text-ink-400 text-center"
						>
							{{ projectQuery ? 'Ничего не найдено' : 'Пока нет проектов' }}
						</div>

						<div v-else class="max-h-[280px] overflow-y-auto -mx-1">
							<button
								v-for="p in filteredProjects"
								:key="p.id"
								class="w-full text-left px-3 py-2 rounded-lg hover:bg-ink-50 flex items-center gap-3 group cursor-pointer"
								@click="openProject(p)"
							>
								<div
									class="h-8 w-8 rounded-lg bg-ink-100 text-ink-600 flex items-center justify-center shrink-0 text-xs font-semibold"
								>
									{{ p.name.charAt(0).toUpperCase() }}
								</div>
								<div class="flex-1 min-w-0">
									<div
										class="text-sm text-ink-900 font-medium truncate group-hover:text-accent-600 transition-colors flex items-center gap-1.5"
									>
										{{ p.name }}
										<svg
											v-if="p.is_favorite"
											width="11"
											height="11"
											viewBox="0 0 24 24"
											fill="currentColor"
											class="text-amber-500 shrink-0"
										>
											<path
												d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z"
											/>
										</svg>
									</div>
									<div
										v-if="p.description"
										class="text-[11px] text-ink-500 truncate"
									>
										{{ p.description }}
									</div>
								</div>
							</button>
						</div>

						<div class="border-t border-ink-100 mt-2 pt-2">
							<NuxtLink
								to="/app/projects"
								class="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs text-[#757575] hover:bg-ink-50 hover:text-ink-900"
								@click="projectSearchOpen = false"
							>
								Все проекты
								<svg
									width="11"
									height="11"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<path d="M5 12h14M13 6l6 6-6 6" />
								</svg>
							</NuxtLink>
						</div>
					</div>
				</Transition>
			</div>

			<!-- Quick actions -->
			<div class="px-4 pb-3">
				<button
					class="btn-accent w-full justify-start!"
					@click="openNewProject"
				>
					<svg
						width="14"
						height="14"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2.4"
					>
						<path d="M12 5v14M5 12h14" />
					</svg>
					Новый проект
				</button>
			</div>

			<nav class="flex-1 overflow-y-auto px-4 pb-4">
				<div
					class="text-[10px] font-semibold tracking-widest text-ink-400 uppercase mt-3 mb-2"
				>
					Проекты
				</div>
				<div class="space-y-0.5">
					<NuxtLink
						to="/app/projects"
						class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-ink-600 hover:bg-ink-50 hover:text-ink-900 transition-colors"
						:class="
							route.path === '/app/projects' ? 'bg-ink-100! text-ink-900!' : ''
						"
					>
						<NavIcon name="folder" />
						Личные
					</NuxtLink>
					<NuxtLink
						to="/app/team/new"
						class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-ink-600 hover:bg-ink-50 hover:text-ink-900 transition-colors"
						:class="
							route.path.startsWith('/app/team')
								? 'bg-ink-100! text-ink-900!'
								: ''
						"
					>
						<NavIcon name="team" />
						Командные
					</NuxtLink>
				</div>

				<div
					class="text-[10px] font-semibold tracking-widest text-ink-400 uppercase mt-5 mb-2"
				>
					Недавние проекты
				</div>
				<div class="space-y-0.5">
					<div
						v-if="!recentProjects.length"
						class="text-xs text-ink-400 px-3 py-2"
					>
						Пока нет проектов
					</div>
					<NuxtLink
						v-for="p in recentProjects"
						:key="p.id"
						:to="`/app/projects/${p.id}`"
						class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors relative"
						:class="
							activeProjectId === p.id
								? 'bg-accent-50 text-accent-700 ring-1 ring-accent-200 font-medium'
								: 'text-ink-600 hover:bg-ink-50 hover:text-ink-900'
						"
					>
						<span
							v-if="activeProjectId === p.id"
							class="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-[3px] rounded-r-full bg-accent-500"
							aria-hidden="true"
						/>
						<svg
							width="14"
							height="14"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.8"
							class="shrink-0"
						>
							<path
								d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"
							/>
						</svg>
						<span class="flex-1 truncate">{{ p.name }}</span>
					</NuxtLink>
				</div>
			</nav>

			<div class="p-3 space-y-1">
				<NuxtLink
					to="/app/profile"
					class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-ink-600 hover:bg-ink-50 hover:text-ink-900"
				>
					<svg
						width="16"
						height="16"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.8"
					>
						<circle cx="12" cy="12" r="3" />
						<path
							d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3h.1a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8v.1a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"
						/>
					</svg>
					Настройки
				</NuxtLink>
				<div
					class="flex items-center gap-2.5 px-3 py-2 rounded-lg group cursor-default"
				>
					<div
						class="h-7 w-7 rounded-full bg-linear-to-br from-accent-400 to-bloom-pink flex items-center justify-center text-white text-xs font-semibold"
					>
						{{
							(auth.user?.full_name || auth.user?.email || 'U')
								.charAt(0)
								.toUpperCase()
						}}
					</div>
					<div class="flex-1 min-w-0 text-sm text-ink-800 truncate">
						{{ auth.user?.full_name || auth.user?.username || 'Пользователь' }}
					</div>
					<button
						class="p-1.5 rounded-lg hover:bg-ink-100 text-ink-400 opacity-0 group-hover:opacity-100"
						title="Выйти"
						@click="auth.logout()"
					>
						<svg
							width="14"
							height="14"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path
								d="M15 12H3M3 12l4-4M3 12l4 4M15 3h5a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-5"
							/>
						</svg>
					</button>
				</div>
			</div>
		</aside>

		<div class="flex-1 flex flex-col min-w-0 h-screen">
			<header
				class="lg:hidden shrink-0 bg-white/80 backdrop-blur-xl border-b border-ink-100 px-4 py-3 flex items-center gap-3"
			>
				<button
					class="p-2 rounded-lg hover:bg-ink-100 text-ink-700"
					aria-label="Меню"
					@click="sidebarOpen = true"
				>
					<svg
						width="20"
						height="20"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path d="M3 6h18M3 12h18M3 18h18" />
					</svg>
				</button>
				<NuxtLink to="/" class="flex items-center">
					<img src="/full-logo.svg" alt="Guidio" class="h-7 w-auto" />
				</NuxtLink>
			</header>

			<main
				class="flex-1 min-h-0 overflow-y-auto overflow-x-clip bg-[#fdfdfd]"
			>
				<slot />
			</main>
		</div>

		<NewProjectModal
			v-model:open="showNewProject"
			@created="onProjectCreated"
		/>
	</div>
</template>
