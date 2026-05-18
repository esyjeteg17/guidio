<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import { useChat, type ChatSummary } from '~/composables/useChat'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'app', middleware: 'auth' })
useHead({ title: 'Проект — Guidio' })

interface UserBrief {
	id: number
	email: string
	username: string
	full_name: string
}
interface Project {
	id: number
	name: string
	description: string
	kind: string
	brief: string
	is_favorite: boolean
	is_archived: boolean
	archived_at: string | null
	team: number | null
	owner: UserBrief
	collaborators: UserBrief[]
	is_owner: boolean
	invite_token: string
	summary_payload: any | null
	summary_generated_at: string | null
	created_at: string
	updated_at: string
}

interface TeamBrief {
	id: number
	name: string
}

const auth = useAuthStore()

const route = useRoute()
const router = useRouter()
const api = useApi()
const chat = useChat()

const projectId = computed(() => Number(route.params.id))

const project = ref<Project | null>(null)
const sessions = ref<ChatSummary[]>([])
const loading = ref(true)
const editing = ref(false)
const editForm = reactive({ name: '', description: '', brief: '' })

const projectTeam = ref<TeamBrief | null>(null)
const myTeams = ref<TeamBrief[]>([])
const showMoveTeam = ref(false)
const movingToTeam = ref(false)
const moveTeamError = ref<string | null>(null)

async function loadTeamInfo() {
	if (!project.value?.team) {
		projectTeam.value = null
		return
	}
	try {
		projectTeam.value = await api.get<TeamBrief>(
			`/teams/${project.value.team}/`,
		)
	} catch {
		projectTeam.value = null
	}
}

async function loadMyTeams() {
	try {
		const data = await api.get<{ results: TeamBrief[] } | TeamBrief[]>(
			'/teams/',
		)
		myTeams.value = Array.isArray(data) ? data : data.results
	} catch {
		myTeams.value = []
	}
}

async function load() {
	loading.value = true
	try {
		project.value = await api.get<Project>(`/projects/${projectId.value}/`)
		editForm.name = project.value.name
		editForm.description = project.value.description
		editForm.brief = project.value.brief
		const all = await chat.list(undefined, projectId.value)
		sessions.value = all.sort((a, b) =>
			(b.updated_at || '').localeCompare(a.updated_at || ''),
		)
		await loadTeamInfo()
	} catch {
		project.value = null
	} finally {
		loading.value = false
	}
}

function openMoveTeam() {
	moveTeamError.value = null
	showMoveTeam.value = true
	if (!myTeams.value.length) loadMyTeams()
}

async function moveToTeam(teamId: number | null) {
	if (!project.value) return
	movingToTeam.value = true
	moveTeamError.value = null
	try {
		const updated = await api.post<Project>(
			`/projects/${project.value.id}/move-to-team/`,
			{ team: teamId },
		)
		project.value = updated
		showMoveTeam.value = false
		await loadTeamInfo()
	} catch (e: any) {
		moveTeamError.value = e?.data?.detail || 'Не удалось перенести проект'
	} finally {
		movingToTeam.value = false
	}
}

async function toggleArchive() {
	if (!project.value) return
	const action = project.value.is_archived ? 'unarchive' : 'archive'
	const confirmText = project.value.is_archived
		? 'Восстановить проект из архива?'
		: `Перенести «${project.value.name}» в архив? Его не будет в основном списке.`
	if (!confirm(confirmText)) return
	try {
		const updated = await api.post<Project>(
			`/projects/${project.value.id}/${action}/`,
		)
		project.value = updated
	} catch (e: any) {
		alert(e?.data?.detail || 'Не удалось изменить статус проекта')
	}
}

async function saveEdits() {
	if (!project.value) return
	const updated = await api.patch<Project>(`/projects/${project.value.id}/`, {
		name: editForm.name,
		description: editForm.description,
		brief: editForm.brief,
	})
	project.value = updated
	editing.value = false
}

async function toggleFav() {
	if (!project.value) return
	const updated = await api.patch<Project>(`/projects/${project.value.id}/`, {
		is_favorite: !project.value.is_favorite,
	})
	project.value = updated
}

async function removeProject() {
	if (!project.value) return
	if (!confirm(`Удалить проект «${project.value.name}»?`)) return
	await api.delete(`/projects/${project.value.id}/`)
	await router.push('/app/projects')
}

async function deleteSession(s: ChatSummary) {
	if (!confirm('Удалить эту сессию?')) return
	await chat.remove(s.id)
	sessions.value = sessions.value.filter(x => x.id !== s.id)
}

const summaryLoading = ref(false)
const summaryError = ref<string | null>(null)

/* ---------------------- Invite / collaborators ---------------------- */
const inviteUrl = computed(() => {
	if (!project.value || typeof window === 'undefined') return ''
	return `${window.location.origin}/invite/project/${project.value.invite_token}`
})
const inviteCopied = ref(false)
function copyInvite() {
	if (!inviteUrl.value) return
	navigator.clipboard?.writeText(inviteUrl.value)
	inviteCopied.value = true
	setTimeout(() => (inviteCopied.value = false), 1500)
}

const rotating = ref(false)
async function rotateInvite() {
	if (!project.value) return
	if (
		!confirm('Сгенерировать новую invite-ссылку? Старая перестанет работать.')
	)
		return
	rotating.value = true
	try {
		const res = await api.post<{ invite_token: string }>(
			`/projects/${project.value.id}/rotate-invite/`,
		)
		if (project.value) project.value.invite_token = res.invite_token
		inviteCopied.value = false
	} finally {
		rotating.value = false
	}
}

async function removeCollaborator(u: UserBrief) {
	if (!project.value) return
	const isSelf = u.id === auth.user?.id
	if (
		!confirm(
			isSelf
				? 'Покинуть проект?'
				: `Убрать ${u.full_name || u.username} из соавторов?`,
		)
	)
		return
	await api.delete(`/projects/${project.value.id}/collaborators/${u.id}/`)
	if (isSelf) {
		await router.push('/app/projects')
		return
	}
	if (project.value) {
		project.value.collaborators = project.value.collaborators.filter(
			c => c.id !== u.id,
		)
	}
}

const avatarGradients = [
	'from-accent-400 to-bloom-pink',
	'from-bloom-lilac to-accent-500',
	'from-bloom-peri to-accent-400',
	'from-bloom-mint to-emerald-400',
]
function gradFor(i: number) {
	return avatarGradients[i % avatarGradients.length]
}

async function regenerateSummary() {
	if (!project.value) return
	if (!sessions.value.length) {
		summaryError.value =
			'Добавьте хотя бы одну сессию — тогда есть из чего собирать рекомендации.'
		return
	}
	summaryLoading.value = true
	summaryError.value = null
	try {
		const res = await api.post<{
			summary_payload: any
			summary_generated_at: string
		}>(`/projects/${project.value.id}/summary/`)
		if (project.value) {
			project.value = {
				...project.value,
				summary_payload: res.summary_payload,
				summary_generated_at: res.summary_generated_at,
			}
		}
	} catch (e: any) {
		summaryError.value = e?.data?.detail || 'Не удалось сгенерировать сводку'
	} finally {
		summaryLoading.value = false
	}
}

function startSession(mode: 'fonts' | 'moodboard' | 'colors') {
	const basePath = mode === 'moodboard' ? '/app/moodboard' : '/app/fonts'
	// В проекте на каждый режим должна быть только одна сессия — если она уже
	// существует, открываем её вместо создания пустого композера.
	const existing = sessions.value.find(s => s.mode === mode)
	if (existing) {
		router.push(`${basePath}/${existing.id}`)
		return
	}
	router.push(`${basePath}?project=${projectId.value}`)
}

function openSession(s: ChatSummary) {
	const basePath = s.mode === 'moodboard' ? '/app/moodboard' : '/app/fonts'
	router.push(`${basePath}/${s.id}`)
}

const modeLabel: Record<string, string> = {
	fonts: 'Шрифты',
	moodboard: 'Мудборд',
	colors: 'Палитра',
	free: 'Чат',
}
const modeIcon: Record<string, string> = {
	fonts: 'type',
	moodboard: 'grid',
	colors: 'layers',
	free: 'chat',
}
const kindLabel: Record<string, string> = {
	fonts: 'Шрифты',
	moodboard: 'Мудборд',
	colors: 'Палитра',
	mixed: 'Смешанный',
}

function formatDate(s: string) {
	return new Date(s).toLocaleDateString('ru-RU', {
		day: 'numeric',
		month: 'long',
		year: 'numeric',
	})
}
function formatRelative(s: string) {
	const now = Date.now()
	const t = new Date(s).getTime()
	const diff = Math.floor((now - t) / 1000)
	if (diff < 60) return 'только что'
	if (diff < 3600) return `${Math.floor(diff / 60)} мин назад`
	if (diff < 86400) return `${Math.floor(diff / 3600)} ч назад`
	if (diff < 604800) return `${Math.floor(diff / 86400)} дн назад`
	return formatDate(s)
}

watch(projectId, load, { immediate: true })

const headerCrumbs = computed<
	Array<{ label: string; to?: string; maxWidth?: string }>
>(() => {
	const crumbs: Array<{ label: string; to?: string; maxWidth?: string }> = []
	if (projectTeam.value) {
		crumbs.push({ label: 'Команды', to: '/app/team/new' })
		crumbs.push({
			label: projectTeam.value.name,
			to: `/app/team/${projectTeam.value.id}`,
			maxWidth: '200px',
		})
	} else {
		crumbs.push({ label: 'Проекты', to: '/app/projects' })
	}
	crumbs.push({ label: project.value?.name || 'Проект' })
	return crumbs
})
</script>

<template>
	<div class="min-h-full flex flex-col">
		<PageHeader :crumbs="headerCrumbs">
			<template v-if="project?.is_archived" #actions>
				<span class="chip bg-ink-100 text-ink-600 text-[10px]!">В архиве</span>
			</template>
		</PageHeader>

		<div v-if="loading" class="p-10 text-ink-400 text-sm">Загружаем…</div>

		<div v-else-if="!project" class="p-10 text-center">
			<div class="text-ink-500">Проект не найден.</div>
			<NuxtLink to="/app/projects" class="btn-secondary mt-4 inline-flex"
				>Вернуться</NuxtLink
			>
		</div>

		<div v-else class="flex-1 px-4 sm:px-6 lg:px-10 py-6 sm:py-8 min-w-0">
			<div class="max-w-[1100px] mx-auto min-w-0">
				<!-- Header -->
				<div class="flex items-start justify-between gap-4 mb-6 flex-wrap">
					<div class="min-w-0 flex-1">
						<div class="flex items-center gap-2 mb-2 flex-wrap">
							<div class="chip">
								{{ kindLabel[project.kind] || project.kind }}
							</div>
							<span
								v-if="project.team"
								class="chip bg-bloom-mint/40 text-emerald-700"
								>Командный</span
							>
							<span v-else class="chip">Личный</span>
						</div>
						<h1
							class="font-display text-2xl sm:text-3xl font-semibold text-ink-900 wrap-break-word"
						>
							{{ project.name }}
						</h1>
						<p
							v-if="project.description"
							class="text-sm text-ink-500 mt-1 max-w-2xl wrap-break-word"
						>
							{{ project.description }}
						</p>
						<div class="text-xs text-ink-400 mt-3">
							Обновлён {{ formatDate(project.updated_at) }}
						</div>
					</div>
					<div class="flex items-center gap-2 flex-wrap w-full sm:w-auto sm:shrink-0">
						<button
							class="h-9 w-9 rounded-full flex items-center justify-center cursor-pointer transition-colors"
							:class="
								project.is_favorite
									? 'bg-amber-50 text-amber-500'
									: 'bg-white hover:text-amber-500'
							"
							:title="
								project.is_favorite ? 'Убрать из избранного' : 'В избранное'
							"
							@click="toggleFav"
						>
							<svg
								width="15"
								height="15"
								viewBox="0 0 24 24"
								:fill="project.is_favorite ? 'currentColor' : 'none'"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z" />
							</svg>
						</button>
						<button
							v-if="project.is_owner"
							class="btn-secondary btn-sm"
							@click="openMoveTeam"
						>
							<svg
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
								<circle cx="9" cy="7" r="4" />
								<path d="M22 11h-6m3-3v6" />
							</svg>
							{{ project.team ? 'Сменить команду' : 'В команду' }}
						</button>
						<button class="btn-secondary btn-sm" @click="editing = true">
							<svg
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path
									d="M12 20h9M16.5 3.5a2.12 2.12 0 1 1 3 3L7 19l-4 1 1-4Z"
								/>
							</svg>
							Редактировать
						</button>
						<button
							v-if="project.is_owner"
							class="btn-secondary btn-sm"
							@click="toggleArchive"
						>
							<svg
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<rect x="2" y="4" width="20" height="5" rx="1" />
								<path d="M4 9v10a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V9M9 13h6" />
							</svg>
							{{ project.is_archived ? 'Из архива' : 'В архив' }}
						</button>
						<button
							class="btn-ghost btn-sm text-red-500 hover:bg-red-50!"
							@click="removeProject"
						>
							<svg
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path
									d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M6 6l1 14a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-14"
								/>
							</svg>
							Удалить
						</button>
					</div>
				</div>

				<!-- Brief -->
				<div v-if="project.brief" class="card-flat p-5 mb-8">
					<div class="text-[10px] uppercase tracking-wider text-ink-400 mb-2">
						Бриф
					</div>
					<p class="text-sm text-ink-700 whitespace-pre-wrap leading-relaxed">
						{{ project.brief }}
					</p>
				</div>

				<!-- New session actions -->
				<div class="mb-8">
					<div class="flex items-center justify-between mb-3">
						<h2 class="font-display text-xl font-semibold text-ink-900">
							Сессии в проекте
						</h2>
					</div>
					<div class="grid sm:grid-cols-2 gap-3">
						<button
							class="card-flat p-5 text-left hover:shadow-soft transition-shadow group"
							@click="startSession('fonts')"
						>
							<div
								class="h-10 w-10 rounded-xl bg-linear-to-br from-[#625ed7] to-[#af99cc] text-white flex items-center justify-center mb-3"
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
							<div class="font-semibold text-ink-900 text-sm">
								Подбор шрифтов
							</div>
							<div class="text-xs text-ink-500 mt-1">
								Пары, примеры использования, живой макет
							</div>
						</button>
						<button
							class="card-flat p-5 text-left hover:shadow-soft transition-shadow group"
							@click="startSession('moodboard')"
						>
							<div
								class="h-10 w-10 rounded-xl bg-linear-to-br from-bloom-pink to-bloom-lilac text-white flex items-center justify-center mb-3"
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
							<div class="font-semibold text-ink-900 text-sm">
								Генерация мудборда
							</div>
							<div class="text-xs text-ink-500 mt-1">
								Референсы, палитра и направление
							</div>
						</button>
					</div>
				</div>

				<!-- Sessions -->
				<!-- <div>
					<div class="flex items-center justify-between mb-3">
						<h2 class="font-display text-xl font-semibold text-ink-900">
							Сессии проекта
						</h2>
						<span class="text-xs text-ink-400">{{ sessions.length }} шт.</span>
					</div>

					<div
						v-if="!sessions.length"
						class="card-flat p-10 text-center text-sm text-ink-500"
					>
						Пока нет сессий. Начните с одного из сценариев выше.
					</div>

					<div v-else class="space-y-2">
						<div
							v-for="s in sessions"
							:key="s.id"
							class="card-flat p-4 flex items-center gap-4 hover:shadow-soft transition-shadow cursor-pointer group"
							@click="openSession(s)"
						>
							<div
								class="h-10 w-10 rounded-xl bg-ink-100 text-ink-600 flex items-center justify-center shrink-0"
							>
								<NavIcon :name="modeIcon[s.mode] || 'chat'" />
							</div>
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-2">
									<span class="chip bg-white ring-1 ring-ink-100">{{
										modeLabel[s.mode] || s.mode
									}}</span>
									<span class="text-xs text-ink-400"
										>{{ s.messages_count }} сообщений</span
									>
								</div>
								<div
									class="font-medium text-ink-900 text-sm mt-1 truncate group-hover:text-accent-600 transition-colors"
								>
									{{ s.title || `Сессия #${s.id}` }}
								</div>
								<div
									v-if="s.last_message?.content"
									class="text-xs text-ink-500 mt-0.5 truncate"
								>
									{{ s.last_message.content }}
								</div>
							</div>
							<div class="shrink-0 flex items-center gap-1">
								<span class="text-xs text-ink-400">{{
									formatRelative(s.updated_at)
								}}</span>
								<button
									class="p-1.5 rounded-lg text-ink-300 hover:text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100"
									title="Удалить сессию"
									@click.stop="deleteSession(s)"
								>
									<svg
										width="13"
										height="13"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
									>
										<path
											d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M6 6l1 14a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-14"
										/>
									</svg>
								</button>
							</div>
						</div>
					</div>
				</div>
 -->
				<!-- Collaborators -->

				<!-- AI Summary -->
				<div class="mt-10">
					<p v-if="summaryError" class="text-sm text-red-500 mb-3">
						{{ summaryError }}
					</p>
					<ProjectSummary
						:summary="project.summary_payload"
						:generated-at="project.summary_generated_at"
						:loading="summaryLoading"
						@regenerate="regenerateSummary"
					/>
				</div>
			</div>
		</div>

		<!-- Move to team modal -->
		<div
			v-if="showMoveTeam"
			class="fixed inset-0 z-50 bg-ink-900/40 backdrop-blur-sm flex items-center justify-center p-4"
			@click.self="showMoveTeam = false"
		>
			<div class="card w-full max-w-md p-6">
				<h3 class="font-display text-xl font-semibold text-ink-900 mb-1">
					{{ project?.team ? 'Сменить команду' : 'Перенести в команду' }}
				</h3>
				<p class="text-xs text-ink-500 mb-4">
					Выберите команду — соавторы из неё получат доступ к проекту.
				</p>

				<div
					v-if="!myTeams.length"
					class="text-sm text-ink-500 px-3 py-6 text-center"
				>
					У вас пока нет команд.
					<NuxtLink
						to="/app/team/new"
						class="text-accent-600 hover:underline"
						@click="showMoveTeam = false"
						>Создать команду</NuxtLink
					>
				</div>

				<div v-else class="space-y-1 max-h-[280px] overflow-y-auto">
					<button
						v-for="t in myTeams"
						:key="t.id"
						class="w-full text-left px-3 py-2.5 rounded-xl flex items-center gap-3 hover:bg-ink-50 transition-colors disabled:opacity-50 cursor-pointer"
						:class="project?.team === t.id ? 'bg-accent-50' : ''"
						:disabled="movingToTeam"
						@click="moveToTeam(t.id)"
					>
						<div
							class="h-9 w-9 rounded-xl bg-linear-to-br from-accent-400 to-bloom-pink text-white text-sm font-semibold flex items-center justify-center shrink-0"
						>
							{{ t.name.charAt(0).toUpperCase() }}
						</div>
						<div class="flex-1 min-w-0">
							<div class="text-sm font-medium text-ink-900 truncate">
								{{ t.name }}
							</div>
							<div
								v-if="project?.team === t.id"
								class="text-[11px] text-accent-600"
							>
								Текущая команда
							</div>
						</div>
						<svg
							v-if="project?.team === t.id"
							width="14"
							height="14"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2.5"
							class="text-accent-600 shrink-0"
						>
							<path d="m5 12 5 5L20 7" />
						</svg>
					</button>
				</div>

				<p v-if="moveTeamError" class="text-sm text-red-500 mt-3">
					{{ moveTeamError }}
				</p>

				<div class="flex justify-between items-center gap-2 mt-5">
					<button
						v-if="project?.team"
						class="btn-ghost text-red-500 hover:bg-red-50!"
						:disabled="movingToTeam"
						@click="moveToTeam(null)"
					>
						Сделать личным
					</button>
					<div class="flex gap-2 ml-auto">
						<button
							class="btn-secondary"
							:disabled="movingToTeam"
							@click="showMoveTeam = false"
						>
							Закрыть
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Edit modal -->
		<div
			v-if="editing"
			class="fixed inset-0 z-50 bg-ink-900/40 backdrop-blur-sm flex items-center justify-center p-4"
			@click.self="editing = false"
		>
			<div class="card w-full max-w-lg p-6">
				<h3 class="font-display text-xl font-semibold text-ink-900 mb-4">
					Редактировать проект
				</h3>
				<div class="space-y-4">
					<div>
						<div class="text-xs font-medium text-ink-700 mb-1.5">Название</div>
						<UiInput v-model="editForm.name" />
					</div>
					<div>
						<div class="text-xs font-medium text-ink-700 mb-1.5">Описание</div>
						<UiInput v-model="editForm.description" :rows="2" />
					</div>
					<div>
						<div class="text-xs font-medium text-ink-700 mb-1.5">Бриф</div>
						<UiInput v-model="editForm.brief" :rows="4" />
					</div>
				</div>
				<div class="flex gap-2 mt-5 justify-end">
					<button class="btn-secondary" @click="editing = false">Отмена</button>
					<button class="btn-accent" @click="saveEdits">Сохранить</button>
				</div>
			</div>
		</div>
	</div>
</template>
