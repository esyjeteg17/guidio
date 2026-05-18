<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'app', middleware: 'auth' })
useHead({ title: 'Проекты — Guidio' })

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
  cover: string | null
  is_favorite: boolean
  is_archived: boolean
  team: number | null
  owner: UserBrief
  collaborators: UserBrief[]
  is_owner: boolean
  invite_token: string
  created_at: string
  updated_at: string
}

const router = useRouter()
const api = useApi()
const auth = useAuthStore()
const projects = ref<Project[]>([])
const loading = ref(true)
const tab = ref<'all' | 'personal' | 'team' | 'shared' | 'archived'>('all')
const query = ref('')

const showNewProject = ref(false)
const creating = ref(false)
const createError = ref<string | null>(null)
const newProject = reactive({ name: '', description: '', kind: 'fonts', brief: '' })

const projectKinds = ['Подбор шрифтов', 'Генерация мудборда']
const ruToKind: Record<string, string> = { 'Подбор шрифтов': 'fonts', 'Генерация мудборда': 'moodboard' }
const kindToRu: Record<string, string> = { fonts: 'Подбор шрифтов', moodboard: 'Генерация мудборда' }
const newProjectKindRu = computed({
  get: () => kindToRu[newProject.kind] || 'Подбор шрифтов',
  set: (v: string) => { newProject.kind = ruToKind[v] || 'fonts' },
})

function openNewProject() {
  createError.value = null
  newProject.name = ''
  newProject.description = ''
  newProject.brief = ''
  newProject.kind = 'fonts'
  showNewProject.value = true
}

async function createProject() {
  if (!newProject.name.trim()) return
  creating.value = true
  createError.value = null
  try {
    const created = await api.post<{ id: number }>('/projects/', { ...newProject })
    showNewProject.value = false
    await load()
    await router.push(`/app/projects/${created.id}`)
  } catch (e: any) {
    createError.value = e?.data?.detail || 'Не удалось создать проект'
  } finally {
    creating.value = false
  }
}

async function load() {
  loading.value = true
  try {
    const data = await api.get<{ results: Project[] } | Project[]>('/projects/?archived=all')
    projects.value = Array.isArray(data) ? data : data.results
  } finally {
    loading.value = false
  }
}

async function remove(p: Project) {
  if (!confirm(`Удалить проект «${p.name}»?`)) return
  await api.delete(`/projects/${p.id}/`)
  projects.value = projects.value.filter(x => x.id !== p.id)
}

async function archive(p: Project) {
  const action = p.is_archived ? 'unarchive' : 'archive'
  const confirmText = p.is_archived
    ? 'Восстановить проект из архива?'
    : `Перенести «${p.name}» в архив?`
  if (!confirm(confirmText)) return
  try {
    const updated = await api.post<Project>(`/projects/${p.id}/${action}/`)
    const idx = projects.value.findIndex(x => x.id === p.id)
    if (idx !== -1) projects.value[idx] = updated
  } catch (e: any) {
    alert(e?.data?.detail || 'Не удалось изменить статус')
  }
}

const tabs: Array<{ id: 'all' | 'personal' | 'team' | 'shared' | 'archived', label: string }> = [
  { id: 'all', label: 'Все' },
  { id: 'personal', label: 'Мои' },
  { id: 'team', label: 'Командные' },
  { id: 'shared', label: 'Приглашения' },
  { id: 'archived', label: 'Архив' },
]

const filtered = computed(() => {
  const uid = auth.user?.id
  let list = projects.value
  if (tab.value === 'archived') {
    list = list.filter(p => p.is_archived)
  } else {
    list = list.filter(p => !p.is_archived)
    if (tab.value === 'personal') list = list.filter(p => !p.team && p.owner?.id === uid)
    else if (tab.value === 'team') list = list.filter(p => !!p.team)
    else if (tab.value === 'shared') list = list.filter(p => p.owner?.id !== uid && !p.team && (p.collaborators || []).some(c => c.id === uid))
  }
  if (query.value.trim()) {
    const q = query.value.toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q))
  }
  return list
})

const counts = computed(() => {
  const uid = auth.user?.id
  const active = projects.value.filter(p => !p.is_archived)
  return {
    all: active.length,
    personal: active.filter(p => !p.team && p.owner?.id === uid).length,
    team: active.filter(p => !!p.team).length,
    shared: active.filter(p => p.owner?.id !== uid && !p.team && (p.collaborators || []).some(c => c.id === uid)).length,
    archived: projects.value.filter(p => p.is_archived).length,
  }
})

function projectBadge(p: Project): string {
  if (p.team) return 'Командный'
  if (p.owner?.id !== auth.user?.id) return 'Приглашение'
  if ((p.collaborators || []).length) return 'С соавторами'
  return 'Личный'
}

const kindLabel: Record<string, string> = {
  fonts: 'Шрифты', moodboard: 'Мудборд', colors: 'Палитра', mixed: 'Смешанный',
}

const kindHue: Record<string, string> = {
  fonts: 'bg-bloom-cream',
  moodboard: 'bg-bloom-mint/40',
  colors: 'bg-bloom-lilac/30',
  mixed: 'bg-accent-100/50',
}

function formatDate(s: string) {
  return new Date(s).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

onMounted(load)
</script>

<template>
  <div class="min-h-full flex flex-col">
    <PageHeader :crumbs="[{ label: 'Проекты' }]" />

    <div class="flex-1 px-4 sm:px-6 lg:px-10 py-6 sm:py-8 min-w-0">
      <div class="max-w-275 mx-auto min-w-0">
        <div class="mb-6 flex items-start justify-between gap-3 sm:gap-4">
          <div class="min-w-0">
            <h1 class="font-display text-2xl sm:text-3xl font-semibold text-ink-900">Проекты</h1>
            <p class="text-sm text-ink-500 mt-1">Личные, командные и те, куда вас пригласили соавторами.</p>
          </div>
          <button class="btn-accent btn-sm shrink-0" @click="openNewProject">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 5v14M5 12h14"/></svg>
            <span class="hidden sm:inline">Новый проект</span>
            <span class="sm:hidden">Новый</span>
          </button>
        </div>

        <!-- Tabs + search -->
        <div class="flex items-center justify-between gap-4 mb-6 flex-wrap">
          <div class="-mx-4 sm:mx-0 px-4 sm:px-0 overflow-x-auto no-scrollbar w-full sm:w-auto">
            <div class="inline-flex bg-ink-100 rounded-full p-1 whitespace-nowrap">
              <button
                v-for="t in tabs" :key="t.id"
                class="px-4 py-1.5 rounded-full text-sm font-medium transition-colors cursor-pointer shrink-0"
                :class="tab === t.id ? 'bg-white text-ink-900 shadow-sm' : 'text-ink-500 hover:text-ink-700'"
                @click="tab = t.id"
              >
                {{ t.label }}
                <span class="ml-1 text-[11px] text-ink-400">
                  {{ counts[t.id] }}
                </span>
              </button>
            </div>
          </div>

          <div class="w-full sm:w-80">
            <UiInput v-model="query" placeholder="Найти проект">
              <template #prefix>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
              </template>
            </UiInput>
          </div>
        </div>

        <div v-if="loading" class="text-ink-400 text-sm">Загружаем…</div>

        <div v-else-if="!filtered.length" class="card-flat p-12 text-center">
          <div class="text-ink-500 text-sm">
            <template v-if="tab === 'shared'">Пока нет приглашений в чужие проекты.</template>
            <template v-else-if="tab === 'archived'">В архиве пусто.</template>
            <template v-else>Пока нет проектов в этой категории.</template>
          </div>
          <button v-if="tab !== 'archived'" class="btn-accent mt-4" @click="openNewProject">Создать проект</button>
        </div>

        <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <NuxtLink
            v-for="p in filtered" :key="p.id"
            :to="`/app/projects/${p.id}`"
            class="card-flat overflow-hidden group hover:shadow-soft transition-shadow"
          >
            <div class="aspect-4/3 flex items-center justify-center relative" :class="kindHue[p.kind] || 'bg-ink-50'">
              <span v-if="p.kind === 'fonts'" class="font-display italic text-5xl text-ink-600 opacity-70">Aa</span>
              <span v-else-if="p.kind === 'moodboard'" class="grid grid-cols-3 gap-1 p-3">
                <div v-for="i in 9" :key="i" class="h-8 w-8 rounded bg-white/80 shadow-sm" />
              </span>
              <span v-else-if="p.kind === 'colors'" class="flex gap-1">
                <div class="h-10 w-4 rounded-full bg-accent-400" />
                <div class="h-10 w-4 rounded-full bg-bloom-pink" />
                <div class="h-10 w-4 rounded-full bg-bloom-mint" />
                <div class="h-10 w-4 rounded-full bg-bloom-cream" />
              </span>
              <span v-else class="font-display italic text-2xl text-ink-500 opacity-70">Проект</span>

              <span class="absolute top-2 left-2 text-[10px] font-medium px-2 py-0.5 rounded-full bg-white/85 text-ink-700">
                {{ p.is_archived ? 'В архиве' : projectBadge(p) }}
              </span>
              <div class="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  v-if="p.is_owner"
                  class="h-7 w-7 rounded-full bg-white/90 flex items-center justify-center text-ink-400 hover:text-accent-600"
                  @click.stop.prevent="archive(p)"
                  :title="p.is_archived ? 'Восстановить из архива' : 'В архив'"
                >
                  <svg v-if="p.is_archived" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 3-6.7L3 8V3"/></svg>
                  <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="5" rx="1"/><path d="M4 9v10a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V9M9 13h6"/></svg>
                </button>
                <button
                  v-if="p.is_owner"
                  class="h-7 w-7 rounded-full bg-white/90 flex items-center justify-center text-ink-400 hover:text-red-500"
                  @click.stop.prevent="remove(p)"
                  title="Удалить"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M6 6l1 14a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-14"/></svg>
                </button>
              </div>
            </div>
            <div class="p-5">
              <div class="flex items-center gap-2 mb-3 flex-wrap">
                <div class="chip">{{ kindLabel[p.kind] }}</div>
                <div v-if="(p.collaborators || []).length" class="text-[11px] text-ink-400">
                  +{{ p.collaborators.length }} соавтор{{ p.collaborators.length === 1 ? '' : p.collaborators.length < 5 ? 'а' : 'ов' }}
                </div>
              </div>
              <h3 class="font-display text-base font-semibold text-ink-900 group-hover:text-accent-600 transition-colors leading-snug">{{ p.name }}</h3>
              <p v-if="p.description" class="text-xs text-ink-500 mt-2 line-clamp-2">{{ p.description }}</p>
              <div class="text-[11px] text-ink-400 mt-3">
                Обновлён {{ formatDate(p.updated_at) }}
                <span v-if="!p.is_owner && p.owner"> · владелец {{ p.owner.full_name || p.owner.username }}</span>
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>

  <!-- New project modal -->
  <div v-if="showNewProject" class="fixed inset-0 z-50 bg-ink-900/40 backdrop-blur-sm flex items-center justify-center p-4" @click.self="showNewProject = false">
    <div class="card w-full max-w-lg p-6">
      <h3 class="font-display text-xl font-semibold text-ink-900 mb-1">Новый проект</h3>
      <p class="text-xs text-ink-500 mb-5">Соберёт воедино сессии, финальные рекомендации и соавторов.</p>
      <div class="space-y-4">
        <div>
          <div class="text-xs font-medium text-ink-700 mb-1.5">Название</div>
          <UiInput v-model="newProject.name" placeholder="Rebranding 2026" />
        </div>
        <div>
          <div class="text-xs font-medium text-ink-700 mb-1.5">Описание</div>
          <UiInput v-model="newProject.description" :rows="2" placeholder="Короткое описание" />
        </div>
        <div>
          <div class="text-xs font-medium text-ink-700 mb-1.5">Тип</div>
          <FilterSelect v-model="newProjectKindRu" :options="projectKinds" placeholder="Подбор шрифтов" />
        </div>
        <div>
          <div class="text-xs font-medium text-ink-700 mb-1.5">Бриф</div>
          <UiInput v-model="newProject.brief" :rows="3" placeholder="Что хотим получить" />
        </div>
        <p v-if="createError" class="text-sm text-red-500">{{ createError }}</p>
      </div>
      <div class="flex gap-2 mt-5 justify-end">
        <button class="btn-secondary" :disabled="creating" @click="showNewProject = false">Отмена</button>
        <button class="btn-accent" :disabled="creating || !newProject.name.trim()" @click="createProject">
          {{ creating ? 'Создаём…' : 'Создать проект' }}
        </button>
      </div>
    </div>
  </div>
</template>
