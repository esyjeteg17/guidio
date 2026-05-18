<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import {
	useChat,
	type ChatMessage,
	type ChatSession,
} from '~/composables/useChat'

const props = defineProps<{
	mode: 'fonts' | 'moodboard' | 'colors'
	title: string
	description: string
	basePath: string
	projectId?: number | null
}>()

const route = useRoute()
const router = useRouter()
const chat = useChat()
const api = useApi()

interface ProjectContext {
	id: number
	name: string
	team: number | null
}
interface TeamContext {
	id: number
	name: string
}

const sessionProject = ref<ProjectContext | null>(null)
const sessionTeam = ref<TeamContext | null>(null)

const current = ref<ChatSession | null>(null)
const input = ref('')
const sending = ref(false)
const error = ref<string | null>(null)
const modeMenuOpen = ref(false)
const showFilters = ref(false)
const filterPopoverRef = ref<HTMLElement | null>(null)
const filterToggleRef = ref<HTMLElement | null>(null)
function onFiltersClickOutside(e: MouseEvent) {
	if (!showFilters.value) return
	const t = e.target as Node
	if (filterPopoverRef.value?.contains(t)) return
	if (filterToggleRef.value?.contains(t)) return
	showFilters.value = false
}
function onEsc(e: KeyboardEvent) {
	if (e.key === 'Escape') showFilters.value = false
}
onMounted(() => {
	document.addEventListener('mousedown', onFiltersClickOutside)
	document.addEventListener('keydown', onEsc)
})
onBeforeUnmount(() => {
	document.removeEventListener('mousedown', onFiltersClickOutside)
	document.removeEventListener('keydown', onEsc)
})

const sessionId = computed(() => {
	const id = route.params.id
	return Array.isArray(id) ? id[0] : id
})

const effectiveProjectId = computed<number | null>(() => {
	if (props.projectId != null) return props.projectId
	if (current.value?.project) return current.value.project
	const q = route.query.project
	const v = Array.isArray(q) ? q[0] : q
	return v ? Number(v) : null
})

const modes = [
	{ id: 'fonts' as const, label: 'Подбор шрифтов', path: '/app/fonts' },
	{
		id: 'moodboard' as const,
		label: 'Генерация мудборда',
		path: '/app/moodboard',
	},
]

const fontFilters = reactive({
	style: '',
	character: '',
	purpose: '',
	type: '',
})
const moodFilters = reactive({
	projectType: '',
	format: '',
	mood: '',
	visualStyle: '',
	palette: '',
})

const headerCrumbs = computed<
	Array<{ label: string; to?: string; maxWidth?: string }>
>(() => {
	if (sessionTeam.value && sessionProject.value) {
		return [
			{ label: 'Команды', to: '/app/team/new' },
			{
				label: sessionTeam.value.name,
				to: `/app/team/${sessionTeam.value.id}`,
				maxWidth: '160px',
			},
			{
				label: sessionProject.value.name,
				to: `/app/projects/${sessionProject.value.id}`,
				maxWidth: '200px',
			},
		]
	}
	if (sessionProject.value) {
		return [
			{ label: 'Проекты', to: '/app/projects' },
			{
				label: sessionProject.value.name,
				to: `/app/projects/${sessionProject.value.id}`,
				maxWidth: '240px',
			},
		]
	}
	return [{ label: 'Новый подбор', to: '/app/start' }]
})

async function switchMode(id: 'fonts' | 'moodboard') {
	modeMenuOpen.value = false
	const target = modes.find(m => m.id === id)
	if (!target) return
	if (id === props.mode) return
	const pid = effectiveProjectId.value

	// Inside a project: try to open the existing session of the target mode in the same project.
	if (pid) {
		try {
			const list = await chat.list(id, pid)
			if (list.length) {
				const latest = list.sort((a, b) =>
					(b.updated_at || '').localeCompare(a.updated_at || ''),
				)[0]
				if (latest) {
					await router.push(`${target.path}/${latest.id}`)
					return
				}
			}
		} catch {
			/* ignore — fall through to empty state */
		}
		await router.push(`${target.path}?project=${pid}`)
		return
	}

	await router.push(target.path)
}

async function loadProjectContext(projectIdValue: number | null) {
	if (!projectIdValue) {
		sessionProject.value = null
		sessionTeam.value = null
		return
	}
	try {
		const p = await api.get<ProjectContext>(`/projects/${projectIdValue}/`)
		sessionProject.value = { id: p.id, name: p.name, team: p.team }
		if (p.team) {
			try {
				const t = await api.get<TeamContext>(`/teams/${p.team}/`)
				sessionTeam.value = { id: t.id, name: t.name }
			} catch {
				sessionTeam.value = null
			}
		} else {
			sessionTeam.value = null
		}
	} catch {
		sessionProject.value = null
		sessionTeam.value = null
	}
}

async function loadCurrent() {
	if (!sessionId.value) {
		current.value = null
		await loadProjectContext(effectiveProjectId.value)
		return
	}
	try {
		current.value = await chat.get(sessionId.value)
	} catch {
		// Don't wipe a session we already have for the same id — happens when
		// `send()` set `current` from the quickGenerate response and the GET
		// races / fails. Otherwise, fall back to empty.
		if (current.value?.id !== Number(sessionId.value)) {
			current.value = null
		}
	}
	await loadProjectContext(
		current.value?.project ?? effectiveProjectId.value ?? null,
	)
}

watch(effectiveProjectId, async pid => {
	if (!sessionId.value) await loadProjectContext(pid)
})

onMounted(() => {
	const hint = route.query.hint
	if (hint && !sessionId.value) {
		const hintStr = Array.isArray(hint) ? hint[0] : hint
		if (hintStr)
			input.value = `Подбери шрифты, похожие по характеру на пару ${hintStr}`
	}
})

/* --------------------- Blog strip below composer --------------------- */
interface Article {
	id: number
	title: string
	slug: string
	tag: string
	hue: string
	cover: string
	excerpt: string
}
const articles = ref<Article[]>([])
const blogHueBg: Record<string, string> = {
	cream: 'bg-bloom-cream',
	mint: 'bg-bloom-mint/40',
	lilac: 'bg-bloom-lilac/30',
	peach: 'bg-bloom-pink/40',
	sky: 'bg-bloom-peri/30',
}
onMounted(async () => {
	try {
		const data = await api.get<{ results: Article[] } | Article[]>(
			'/blog/articles/',
		)
		const list = Array.isArray(data) ? data : data.results
		articles.value = list.slice(0, 3)
	} catch {
		/* ignore */
	}
})

const activeFilters = computed<Record<string, string>>(() => {
	const f: Record<string, string> = {}
	if (props.mode === 'fonts') {
		if (fontFilters.style) f['стиль'] = fontFilters.style
		if (fontFilters.character) f['характер'] = fontFilters.character
		if (fontFilters.purpose) f['назначение'] = fontFilters.purpose
		if (fontFilters.type) f['шрифт для заголовка'] = fontFilters.type
	} else if (props.mode === 'moodboard') {
		if (moodFilters.projectType) f['тип проекта'] = moodFilters.projectType
		if (moodFilters.format) f['формат'] = moodFilters.format
		if (moodFilters.mood) f['настроение'] = moodFilters.mood
		if (moodFilters.visualStyle) f['стиль'] = moodFilters.visualStyle
		if (moodFilters.palette) f['палитра'] = moodFilters.palette
	}
	return f
})

function clearFilterKey(label: string) {
	if (props.mode === 'fonts') {
		const map: Record<string, keyof typeof fontFilters> = {
			стиль: 'style',
			характер: 'character',
			назначение: 'purpose',
			'шрифт для заголовка': 'type',
		}
		const k = map[label]
		if (k) fontFilters[k] = ''
	} else {
		const map: Record<string, keyof typeof moodFilters> = {
			'тип проекта': 'projectType',
			формат: 'format',
			настроение: 'mood',
			стиль: 'visualStyle',
			палитра: 'palette',
		}
		const k = map[label]
		if (k) moodFilters[k] = ''
	}
}

function resetFilters() {
	if (props.mode === 'fonts')
		Object.assign(fontFilters, {
			style: '',
			character: '',
			purpose: '',
			type: '',
		})
	else
		Object.assign(moodFilters, {
			projectType: '',
			format: '',
			mood: '',
			visualStyle: '',
			palette: '',
		})
}

/* --------------------- Voice input (Soniox transcription) --------------------- */
type VoiceState = 'idle' | 'recording' | 'transcribing'
const voiceState = ref<VoiceState>('idle')
const voiceError = ref<string | null>(null)
const mediaRecorder = ref<MediaRecorder | null>(null)
const recordedChunks = ref<Blob[]>([])
const recordingStream = ref<MediaStream | null>(null)
const recordingStart = ref<number>(0)
const recordingElapsed = ref<number>(0)
let elapsedTimer: ReturnType<typeof setInterval> | null = null

function pickRecorderMime(): string {
	const candidates = [
		'audio/webm;codecs=opus',
		'audio/webm',
		'audio/ogg;codecs=opus',
		'audio/mp4',
	]
	if (typeof MediaRecorder === 'undefined') return ''
	for (const m of candidates) {
		try {
			if (MediaRecorder.isTypeSupported(m)) return m
		} catch {
			/* ignore */
		}
	}
	return ''
}

function stopRecordingStream() {
	recordingStream.value?.getTracks().forEach(t => t.stop())
	recordingStream.value = null
	if (elapsedTimer) {
		clearInterval(elapsedTimer)
		elapsedTimer = null
	}
}

async function startRecording() {
	voiceError.value = null
	if (
		typeof navigator === 'undefined' ||
		!navigator.mediaDevices?.getUserMedia ||
		typeof MediaRecorder === 'undefined'
	) {
		voiceError.value = 'Голосовой ввод не поддерживается этим браузером'
		return
	}
	try {
		const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
		recordingStream.value = stream
		const mime = pickRecorderMime()
		const rec = mime
			? new MediaRecorder(stream, { mimeType: mime })
			: new MediaRecorder(stream)
		recordedChunks.value = []
		rec.addEventListener('dataavailable', (e: BlobEvent) => {
			if (e.data && e.data.size > 0) recordedChunks.value.push(e.data)
		})
		rec.addEventListener('stop', () => void onRecordingStop())
		rec.start()
		mediaRecorder.value = rec
		recordingStart.value = Date.now()
		recordingElapsed.value = 0
		voiceState.value = 'recording'
		elapsedTimer = setInterval(() => {
			recordingElapsed.value = Math.floor(
				(Date.now() - recordingStart.value) / 1000,
			)
			// Hard stop at 60s — Soniox bills per-minute and we want a short composer dictation.
			if (recordingElapsed.value >= 60) finishRecording()
		}, 250)
	} catch (e: any) {
		stopRecordingStream()
		voiceState.value = 'idle'
		voiceError.value =
			e?.name === 'NotAllowedError'
				? 'Нет доступа к микрофону. Разрешите запись и попробуйте снова.'
				: 'Не удалось начать запись'
	}
}

function finishRecording() {
	const rec = mediaRecorder.value
	if (rec && rec.state !== 'inactive') {
		try {
			rec.stop()
		} catch {
			/* ignore */
		}
	} else {
		// no recorder — just clean up
		stopRecordingStream()
		voiceState.value = 'idle'
	}
}

async function onRecordingStop() {
	stopRecordingStream()
	const chunks = recordedChunks.value
	recordedChunks.value = []
	mediaRecorder.value = null
	if (!chunks.length) {
		voiceState.value = 'idle'
		return
	}
	voiceState.value = 'transcribing'
	const type = chunks[0]?.type || 'audio/webm'
	const blob = new Blob(chunks, { type })
	if (blob.size < 800) {
		// Less than ~50ms of audio — likely a misclick.
		voiceState.value = 'idle'
		voiceError.value = 'Слишком короткая запись'
		return
	}
	try {
		const ext = type.includes('mp4')
			? 'm4a'
			: type.includes('ogg')
				? 'ogg'
				: 'webm'
		const form = new FormData()
		form.append('audio', blob, `recording.${ext}`)
		const res = await api.post<{ text: string }>('/ai/transcribe/', form)
		const text = (res?.text || '').trim()
		if (text) {
			input.value = input.value
				? `${input.value.replace(/\s+$/, '')} ${text}`
				: text
			await nextTick()
			autoResizeComposer()
			composerInputRef.value?.focus()
		} else {
			voiceError.value = 'Речь не распознана. Попробуйте ещё раз.'
		}
	} catch (e: any) {
		voiceError.value = e?.data?.detail || 'Не удалось распознать аудио'
	} finally {
		voiceState.value = 'idle'
	}
}

function toggleVoice() {
	if (voiceState.value === 'idle') void startRecording()
	else if (voiceState.value === 'recording') finishRecording()
	// while transcribing — кнопка disabled, ничего не делаем
}

onBeforeUnmount(() => {
	stopRecordingStream()
	const rec = mediaRecorder.value
	if (rec && rec.state !== 'inactive') {
		try {
			rec.stop()
		} catch {
			/* ignore */
		}
	}
})

function pushOptimisticUser(content: string): ChatMessage {
	const msg: ChatMessage = {
		id: -Date.now(), // negative id marks a client-only message
		role: 'user',
		content,
		payload: null,
		created_at: new Date().toISOString(),
	}
	if (!current.value) {
		current.value = {
			id: 0,
			mode: props.mode,
			title: content.slice(0, 80),
			project: effectiveProjectId.value,
			messages: [msg],
			created_at: new Date().toISOString(),
			updated_at: new Date().toISOString(),
		} as ChatSession
	} else {
		current.value.messages.push(msg)
	}
	return msg
}

async function send() {
	if (!input.value.trim() || sending.value) return
	sending.value = true
	error.value = null
	const content = input.value
	const filters = { ...activeFilters.value }
	input.value = ''
	showFilters.value = false

	// Always show the user's message immediately — before the network round-trip.
	pushOptimisticUser(content)

	if (!sessionId.value) {
		try {
			const res = await chat.quickGenerate(props.mode, content, {
				project: effectiveProjectId.value,
				filters,
			})
			// Set the real session from the response BEFORE navigation, so the
			// view never goes blank during the route transition.
			current.value = res.session
			// Update the URL without triggering a full reload — the [[id]].vue
			// route stays mounted, so `current` survives this navigation.
			await router.push(`${props.basePath}/${res.session.id}`)
		} catch (e: any) {
			error.value = e?.data?.detail || 'Не удалось отправить запрос'
			// Roll back the optimistic session so the empty-state reappears.
			current.value = null
		} finally {
			sending.value = false
		}
		return
	}

	try {
		const res = await chat.send(sessionId.value, content, filters)
		current.value = res.session
	} catch (e: any) {
		error.value = e?.data?.detail || 'Не удалось получить ответ'
		// Drop the optimistic message on failure so the composer state stays clean.
		if (current.value) {
			current.value.messages = current.value.messages.filter(m => m.id >= 0)
		}
	} finally {
		sending.value = false
	}
}

watch(sessionId, loadCurrent, { immediate: true })

const messagesRef = ref<HTMLDivElement | null>(null)
watch(
	() => current.value?.messages.length,
	async () => {
		await nextTick()
		if (messagesRef.value) {
			messagesRef.value.scrollTop = messagesRef.value.scrollHeight
		}
	},
)

const composerInputRef = ref<HTMLTextAreaElement | null>(null)
function autoResizeComposer() {
	const el = composerInputRef.value
	if (!el) return
	el.style.height = 'auto'
	el.style.height = `${Math.min(el.scrollHeight, 240)}px`
}
watch(input, async () => {
	await nextTick()
	autoResizeComposer()
})

const fontStyles = [
	'современный',
	'классический',
	'минималистичный',
	'декоративный',
	'технологичный',
	'editorial',
]
const fontChars = [
	'строгий',
	'дружелюбный',
	'премиальный',
	'нейтральный',
	'выразительный',
	'мягкий',
]
const fontPurposes = [
	'для бренда',
	'для сайта',
	'для приложения',
	'для презентации',
	'для упаковки',
	'для соцсетей',
]
const fontTypes = ['без засечек', 'с засечками']

const moodProjectTypes = [
	'бренд',
	'сайт',
	'приложение',
	'упаковка',
	'соцсети',
	'презентация',
]
const moodMoods = [
	'спокойное',
	'яркое',
	'премиальное',
	'минималистичное',
	'эмоциональное',
	'технологичное',
	'тёплое',
	'холодное',
]
const moodStyles = [
	'минимализм',
	'editorial',
	'futuristic',
	'luxury',
	'playful',
	'natural',
	'corporate',
	'soft modern',
]
const moodPalettes = [
	'светлая',
	'тёмная',
	'пастельная',
	'контрастная',
	'нейтральная',
	'тёплая',
	'холодная',
]
const moodFormats = [
	'фотографии',
	'интерфейсы',
	'брендинг',
	'типографика',
	'упаковка',
	'интерьерная эстетика',
]

// Moodboard reference photos (client-side only, shown as inspiration hint)
interface RefPhoto {
	id: number
	url: string
}
const moodPhotos = ref<RefPhoto[]>([])
const photoInput = ref<HTMLInputElement | null>(null)

function triggerPhoto() {
	photoInput.value?.click()
}

function onPhotoPick(e: Event) {
	const files = (e.target as HTMLInputElement).files
	if (!files) return
	const remaining = 3 - moodPhotos.value.length
	Array.from(files)
		.slice(0, remaining)
		.forEach(f => {
			const url = URL.createObjectURL(f)
			moodPhotos.value.push({ id: Date.now() + Math.random(), url })
		})
	if (photoInput.value) photoInput.value.value = ''
}

function removePhoto(id: number) {
	const p = moodPhotos.value.find(x => x.id === id)
	if (p) URL.revokeObjectURL(p.url)
	moodPhotos.value = moodPhotos.value.filter(x => x.id !== id)
}
</script>

<template>
	<div class="h-full flex flex-col bg-[#fdfdfd]">
		<PageHeader :crumbs="headerCrumbs">
			<template #trailing>
				<div class="relative">
					<button
						class="inline-flex items-center gap-1 text-ink-900 font-medium"
						@click="modeMenuOpen = !modeMenuOpen"
					>
						{{ title }}
						<svg
							width="14"
							height="14"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							:class="modeMenuOpen ? 'rotate-180' : ''"
							class="transition-transform"
						>
							<path d="m6 9 6 6 6-6" />
						</svg>
					</button>
					<div
						v-if="modeMenuOpen"
						class="absolute top-full left-0 mt-2 w-[240px] card p-1.5 z-20"
					>
						<button
							v-for="m in modes"
							:key="m.id"
							class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm hover:bg-ink-50 text-left"
							:class="
								mode === m.id ? 'text-accent-600 font-medium' : 'text-ink-700'
							"
							@click="switchMode(m.id)"
						>
							{{ m.label }}
							<svg
								v-if="mode === m.id"
								width="14"
								height="14"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2.5"
							>
								<path d="M5 12l5 5L20 7" />
							</svg>
						</button>
					</div>
				</div>
			</template>
			<template #actions>
				<button class="flex items-center gap-1">
					<svg
						width="14"
						height="14"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path
							d="M12 3v12M7 8l5-5 5 5M5 15v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4"
						/>
					</svg>
					Поделиться
				</button>
			</template>
		</PageHeader>

		<div
			ref="messagesRef"
			class="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-8"
		>
			<div class="max-w-[760px] mx-auto space-y-6">
				<template v-if="current?.messages?.length">
					<ChatMessageItem
						v-for="m in current.messages"
						:key="m.id"
						:message="m"
						:mode="mode"
						:project-id="effectiveProjectId"
					/>
					<ChatLoader v-if="sending" :mode="mode" />
				</template>

				<!-- Empty state hint -->
				<div
					v-if="!current && !sending"
					class="pt-16 flex flex-col items-center text-center"
				>
					<div
						class="h-14 w-14 rounded-2xl bg-linear-to-br from-[#4373E4] to-[#4373E4] text-white flex items-center justify-center mb-5 shadow-soft"
					>
						<svg
							width="22"
							height="22"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2.2"
						>
							<path
								d="M12 3 13.5 9.5 20 11 13.5 12.5 12 19 10.5 12.5 4 11 10.5 9.5Z"
							/>
						</svg>
					</div>
					<h2 class="font-display text-2xl font-semibold text-ink-900 mb-2">
						{{ title }}
					</h2>
					<p class="text-sm text-ink-500 max-w-md leading-relaxed">
						{{ description }}
					</p>
					<p class="text-xs text-ink-400 mt-5">
						Опишите задачу ниже или откройте фильтры
						<svg
							class="inline -mt-0.5"
							width="12"
							height="12"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M3 6h18M7 12h10M10 18h4" />
						</svg>
						слева от поля ввода.
					</p>
				</div>
			</div>
		</div>

		<!-- Composer (sticky bottom, never scrolls away) -->
		<div class="shrink-0 px-4 sm:px-6 lg:px-8 pb-6 bg-[#fdfdfd]">
			<div class="max-w-[760px] mx-auto relative">
				<!-- Filters popover, anchored above composer -->
				<Transition
					enter-active-class="transition duration-200 ease-out"
					enter-from-class="opacity-0 translate-y-2"
					enter-to-class="opacity-100 translate-y-0"
					leave-active-class="transition duration-150 ease-in"
					leave-from-class="opacity-100 translate-y-0"
					leave-to-class="opacity-0 translate-y-2"
				>
					<div
						v-if="showFilters"
						ref="filterPopoverRef"
						class="absolute bottom-full left-0 right-0 mb-3 card p-6 z-20 max-h-[min(70vh,640px)] overflow-y-auto"
					>
						<div class="flex items-start justify-between gap-4 mb-5">
							<div>
								<div class="font-display text-lg font-semibold text-ink-900">
									Уточните подбор
								</div>
								<p class="text-xs text-ink-500 mt-1">
									{{
										mode === 'fonts'
											? 'Фильтры помогут точнее подобрать шрифт под вашу задачу.'
											: 'Фильтры сузят поиск референсов, палитры и типографики для мудборда.'
									}}
								</p>
							</div>
							<button
								class="p-1.5 rounded-lg text-ink-400 hover:text-ink-700 hover:bg-ink-50 shrink-0"
								@click="showFilters = false"
								title="Закрыть"
							>
								<svg
									width="16"
									height="16"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<path d="M18 6 6 18M6 6l12 12" />
								</svg>
							</button>
						</div>

						<!-- Fonts filters -->
						<div
							v-if="mode === 'fonts'"
							class="grid sm:grid-cols-2 gap-x-5 gap-y-4"
						>
							<div>
								<div class="text-xs font-medium text-ink-700 mb-1.5">
									Стиль шрифта
								</div>
								<FilterSelect
									v-model="fontFilters.style"
									:options="fontStyles"
									placeholder="любой"
								/>
							</div>
							<div>
								<div class="text-xs font-medium text-ink-700 mb-1.5">
									Назначение
								</div>
								<FilterSelect
									v-model="fontFilters.purpose"
									:options="fontPurposes"
									placeholder="любое"
								/>
							</div>
							<div>
								<div class="text-xs font-medium text-ink-700 mb-1.5">
									Характер
								</div>
								<FilterSelect
									v-model="fontFilters.character"
									:options="fontChars"
									placeholder="любой"
								/>
							</div>
							<div>
								<div class="text-xs font-medium text-ink-700 mb-1.5">
									Шрифт для заголовка
								</div>
								<FilterSelect
									v-model="fontFilters.type"
									:options="fontTypes"
									placeholder="любой"
								/>
							</div>
						</div>

						<!-- Moodboard filters -->
						<div
							v-else-if="mode === 'moodboard'"
							class="grid sm:grid-cols-2 gap-5"
						>
							<div class="space-y-4">
								<div>
									<div class="text-xs font-medium text-ink-700 mb-1.5">
										Тип проекта
									</div>
									<FilterSelect
										v-model="moodFilters.projectType"
										:options="moodProjectTypes"
										placeholder="любой"
									/>
								</div>
								<div>
									<div class="text-xs font-medium text-ink-700 mb-1.5">
										Настроение
									</div>
									<FilterSelect
										v-model="moodFilters.mood"
										:options="moodMoods"
										placeholder="любое"
									/>
								</div>
								<div>
									<div class="text-xs font-medium text-ink-700 mb-1.5">
										Визуальный стиль
									</div>
									<FilterSelect
										v-model="moodFilters.visualStyle"
										:options="moodStyles"
										placeholder="любой"
									/>
								</div>
							</div>
							<div class="space-y-4">
								<div>
									<div class="text-xs font-medium text-ink-700 mb-1.5">
										Формат
									</div>
									<FilterSelect
										v-model="moodFilters.format"
										:options="moodFormats"
										placeholder="любой"
									/>
								</div>
								<div>
									<div class="text-xs font-medium text-ink-700 mb-1.5">
										Палитра
									</div>
									<FilterSelect
										v-model="moodFilters.palette"
										:options="moodPalettes"
										placeholder="любая"
									/>
								</div>
								<!-- <div>
									<div class="text-xs font-medium text-ink-700 mb-1.5">
										Референсы
									</div>
									<p class="text-[11px] text-ink-500 leading-relaxed">
										Загрузите 1–3 фото, чтобы сервис лучше понял эстетику
									</p>
									<div class="flex items-center gap-2 mt-2">
										<div
											v-for="(slot, si) in 3"
											:key="slot"
											class="relative h-11 w-11 rounded-xl border-2 border-dashed border-ink-200 flex items-center justify-center overflow-hidden bg-ink-50/50"
										>
											<template v-if="moodPhotos[si]">
												<img
													:src="moodPhotos[si]!.url"
													class="absolute inset-0 w-full h-full object-cover"
													alt="reference"
												/>
												<button
													class="absolute top-0.5 right-0.5 h-4 w-4 rounded-full bg-white/90 text-ink-600 hover:text-red-500 flex items-center justify-center"
													@click="removePhoto(moodPhotos[si]!.id)"
													title="Удалить"
												>
													<svg
														width="8"
														height="8"
														viewBox="0 0 24 24"
														fill="none"
														stroke="currentColor"
														stroke-width="3"
													>
														<path d="M18 6 6 18M6 6l12 12" />
													</svg>
												</button>
											</template>
										</div>
										<button
											class="h-9 w-9 rounded-full bg-linear-to-br from-[#4373E4] to-[#4373E4] text-white flex items-center justify-center shadow-sm cursor-pointer hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed"
											:disabled="moodPhotos.length >= 3"
											@click="triggerPhoto"
											title="Добавить фото"
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
										</button>
										<input
											ref="photoInput"
											type="file"
											accept="image/*"
											multiple
											class="hidden"
											@change="onPhotoPick"
										/>
									</div>
								</div> -->
							</div>
						</div>

						<div class="flex justify-end gap-2 mt-6">
							<button class="btn-secondary btn-sm" @click="resetFilters">
								Сбросить
							</button>
							<button class="btn-primary btn-sm" @click="showFilters = false">
								Сохранить
							</button>
						</div>
					</div>
				</Transition>

				<p v-if="error" class="text-sm text-red-500 mb-2">{{ error }}</p>
				<p
					v-if="voiceError"
					class="text-xs text-red-500 mb-2 flex items-center gap-2"
				>
					<span class="flex-1">{{ voiceError }}</span>
					<button
						class="text-ink-400 hover:text-ink-700 cursor-pointer"
						@click="voiceError = null"
						title="Скрыть"
					>
						<svg
							width="11"
							height="11"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2.5"
						>
							<path d="M18 6 6 18M6 6l12 12" />
						</svg>
					</button>
				</p>
				<p
					v-if="voiceState === 'recording'"
					class="text-xs text-ink-500 mb-2 flex items-center gap-2"
				>
					Идёт запись… Нажмите на микрофон, чтобы остановить.
				</p>
				<p
					v-else-if="voiceState === 'transcribing'"
					class="text-xs text-ink-500 mb-2"
				>
					Распознаём речь…
				</p>

				<!-- Active filter chips (read-only hint, sent as metadata) -->
				<div
					v-if="Object.keys(activeFilters).length"
					class="flex flex-wrap gap-1.5 mb-2"
				>
					<button
						v-for="(value, label) in activeFilters"
						:key="label"
						class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium bg-accent-50 text-accent-700 ring-1 ring-accent-100 cursor-pointer hover:bg-accent-100"
						:title="`Убрать фильтр «${label}»`"
						@click="clearFilterKey(String(label))"
					>
						{{ label }}: {{ value }}
						<svg
							width="9"
							height="9"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="3"
						>
							<path d="M18 6 6 18M6 6l12 12" />
						</svg>
					</button>
				</div>

				<div class="card-flat flex items-center gap-2 pl-4 pr-1.5 py-1.5">
					<button
						ref="filterToggleRef"
						class="p-2 rounded-full cursor-pointer transition-colors"
						:class="
							showFilters
								? 'bg-accent-50 text-accent-600'
								: 'text-ink-400 hover:text-ink-700 hover:bg-ink-50'
						"
						title="Фильтры"
						@click="showFilters = !showFilters"
					>
						<svg
							width="18"
							height="18"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.8"
						>
							<path d="M3 6h18M7 12h10M10 18h4" />
						</svg>
					</button>
					<textarea
						ref="composerInputRef"
						v-model="input"
						rows="1"
						class="flex-1 bg-transparent resize-none text-sm placeholder:text-ink-400 focus:outline-none py-2.5 min-h-[40px] max-h-60 leading-relaxed overflow-y-auto"
						placeholder="Опишите задачу своими словами..."
						@input="autoResizeComposer"
						@keydown.enter.exact.prevent="send"
						@keydown.shift.enter.exact="() => {}"
					/>
					<button
						class="relative p-2 rounded-full transition-colors cursor-pointer disabled:cursor-default"
						:class="
							voiceState === 'recording'
								? 'bg-red-500 text-white hover:bg-red-600'
								: voiceState === 'transcribing'
									? 'bg-ink-100 text-ink-400'
									: 'text-ink-400 hover:text-ink-700 hover:bg-ink-50'
						"
						:disabled="voiceState === 'transcribing'"
						:title="
							voiceState === 'recording'
								? `Остановить запись (${recordingElapsed}s)`
								: voiceState === 'transcribing'
									? 'Распознаём речь…'
									: 'Голосовой ввод'
						"
						@click="toggleVoice"
					>
						<svg
							v-if="voiceState !== 'transcribing'"
							width="18"
							height="18"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.8"
						>
							<rect x="9" y="3" width="6" height="12" rx="3" />
							<path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
						</svg>
						<svg
							v-else
							class="animate-spin"
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M21 12a9 9 0 1 1-6.7-8.7" />
						</svg>
						<span
							v-if="voiceState === 'recording'"
							class="absolute top-0 right-0 h-2 w-2 rounded-full bg-white animate-pulse ring-2 ring-red-500"
						/>
					</button>
					<button
						class="h-10 w-10 rounded-full bg-linear-to-br from-[#4373E4] to-[#4373E4] text-white flex items-center justify-center shadow-sm disabled:opacity-50"
						:disabled="sending || !input.trim()"
						@click="send"
					>
						<svg
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2.2"
						>
							<path d="M12 19V5M5 12l7-7 7 7" />
						</svg>
					</button>
				</div>
			</div>
		</div>

		<!-- Blog strip — fixed under composer -->
		<!-- <div v-if="articles.length" class="shrink-0 border-t border-ink-100 px-4 sm:px-6 lg:px-8 py-4 bg-[#fdfdfd]">
      <div class="max-w-[760px] mx-auto">
        <div class="flex items-end justify-between mb-3">
          <h3 class="font-display text-sm font-semibold text-ink-900">Блог</h3>
          <NuxtLink to="/blog" class="text-xs text-ink-500 hover:text-ink-800">Все статьи</NuxtLink>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          <NuxtLink
            v-for="a in articles" :key="a.id"
            :to="`/blog/${a.slug}`"
            class="card-flat overflow-hidden flex group"
          >
            <div
              class="w-16 aspect-square shrink-0 relative"
              :class="blogHueBg[a.hue] || 'bg-ink-50'"
            >
              <img
                v-if="a.cover"
                :src="a.cover"
                :alt="a.title"
                class="absolute inset-0 w-full h-full object-cover"
                loading="lazy"
              />
            </div>
            <div class="flex-1 min-w-0 p-2.5">
              <div class="text-[10px] uppercase tracking-wider text-ink-400 truncate">{{ a.tag }}</div>
              <div class="text-xs font-medium text-ink-900 line-clamp-2 mt-0.5 group-hover:text-accent-600 transition-colors leading-snug">
                {{ a.title }}
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>
    </div> -->
	</div>
</template>
