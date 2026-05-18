<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'app', middleware: 'auth' })
useHead({ title: 'Команда — Guidio' })

interface UserBrief {
  id: number
  email: string
  username: string
  full_name: string
  role: string
}
interface Member {
  id: number
  user: UserBrief
  role: string
  joined_at: string
}
interface Team {
  id: number
  name: string
  description: string
  avatar: string | null
  owner: UserBrief
  invite_token: string
  members: Member[]
  members_count: number
  created_at: string
}
interface Project {
  id: number
  name: string
  description: string
  kind: string
  team: number | null
  updated_at: string
}

const route = useRoute()
const router = useRouter()
const api = useApi()
const auth = useAuthStore()

const teamId = computed(() => Number(route.params.id))
const team = ref<Team | null>(null)
const projects = ref<Project[]>([])
const loading = ref(true)
const copied = ref(false)
const showCreate = ref(false)
const newProject = reactive({ name: '', description: '', kind: 'mixed', brief: '' })
const projectKinds = ['Смешанный', 'Шрифты', 'Мудборд', 'Палитра']
const kindToRu: Record<string, string> = { mixed: 'Смешанный', fonts: 'Шрифты', moodboard: 'Мудборд', colors: 'Палитра' }
const ruToKind: Record<string, string> = { 'Смешанный': 'mixed', 'Шрифты': 'fonts', 'Мудборд': 'moodboard', 'Палитра': 'colors' }
const newProjectKindRu = computed({
  get: () => kindToRu[newProject.kind] || 'Смешанный',
  set: (v: string) => { newProject.kind = ruToKind[v] || 'mixed' },
})

const isOwner = computed(() => team.value && auth.user && team.value.owner.id === auth.user.id)

async function load() {
  loading.value = true
  try {
    team.value = await api.get<Team>(`/teams/${teamId.value}/`)
    const res = await api.get<{ results: Project[] } | Project[]>(`/projects/`)
    const list = Array.isArray(res) ? res : res.results
    projects.value = list.filter(p => p.team === teamId.value)
  } catch {
    team.value = null
  } finally {
    loading.value = false
  }
}

async function createTeamProject() {
  if (!newProject.name.trim() || !team.value) return
  const created = await api.post<Project>('/projects/', {
    ...newProject,
    team: team.value.id,
  })
  projects.value.unshift(created)
  newProject.name = ''
  newProject.description = ''
  newProject.brief = ''
  showCreate.value = false
}

async function leaveTeam() {
  if (!team.value) return
  if (!confirm('Покинуть команду?')) return
  await api.post(`/teams/${team.value.id}/leave/`)
  await router.push('/app/team/new')
}

async function deleteTeam() {
  if (!team.value || !isOwner.value) return
  if (!confirm(`Удалить команду «${team.value.name}»? Это действие необратимо.`)) return
  await api.delete(`/teams/${team.value.id}/`)
  await router.push('/app/team/new')
}

function copyInvite() {
  if (!team.value) return
  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  navigator.clipboard?.writeText(`${origin}/invite/${team.value.invite_token}`)
  copied.value = true
  setTimeout(() => (copied.value = false), 1500)
}

const avatarGradients = [
  'from-accent-400 to-bloom-pink',
  'from-bloom-lilac to-accent-500',
  'from-bloom-peri to-accent-400',
  'from-bloom-mint to-emerald-400',
  'from-bloom-pink to-bloom-lilac',
]
function gradientFor(i: number) {
  return avatarGradients[i % avatarGradients.length]
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

const roleLabel: Record<string, string> = {
  owner: 'Владелец', editor: 'Редактор', viewer: 'Наблюдатель',
}

function formatDate(s: string) {
  return new Date(s).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

watch(teamId, load, { immediate: true })

const headerCrumbs = computed<Array<{ label: string; to?: string; maxWidth?: string }>>(() => [
  { label: 'Команды', to: '/app/team/new' },
  { label: team.value?.name || 'Команда' },
])
</script>

<template>
  <div class="min-h-full flex flex-col">
    <PageHeader :crumbs="headerCrumbs" />

    <div v-if="loading" class="p-10 text-ink-400 text-sm">Загружаем…</div>

    <div v-else-if="!team" class="p-10 text-center">
      <div class="text-ink-500">Команда не найдена.</div>
      <NuxtLink to="/app/team/new" class="btn-secondary mt-4 inline-flex">К списку команд</NuxtLink>
    </div>

    <div v-else class="flex-1 px-6 lg:px-10 py-8">
      <div class="max-w-[1100px] mx-auto">
        <!-- Header -->
        <div class="flex items-start gap-5 mb-8 flex-wrap">
          <div
            class="h-16 w-16 rounded-3xl bg-linear-to-br from-accent-400 to-bloom-pink text-white font-display text-3xl font-semibold flex items-center justify-center shrink-0"
          >
            {{ team.name.charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <h1 class="font-display text-3xl font-semibold text-ink-900">{{ team.name }}</h1>
            <p v-if="team.description" class="text-sm text-ink-500 mt-1 max-w-2xl">{{ team.description }}</p>
            <div class="text-xs text-ink-400 mt-2">
              Создана {{ formatDate(team.created_at) }} · {{ team.members_count }} участник{{ team.members_count === 1 ? '' : team.members_count < 5 ? 'а' : 'ов' }}
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button v-if="isOwner" class="btn-ghost btn-sm text-red-500 hover:bg-red-50!" @click="deleteTeam">
              Удалить команду
            </button>
            <button v-else class="btn-secondary btn-sm" @click="leaveTeam">Покинуть</button>
          </div>
        </div>

        <div class="grid lg:grid-cols-3 gap-6 mb-8">
          <!-- Invite -->
          <div class="card-flat p-5 lg:col-span-2">
            <div class="text-xs font-medium text-ink-700 mb-2">Пригласить в команду</div>
            <p class="text-xs text-ink-500 mb-3">Поделитесь ссылкой — коллеги присоединятся по инвайт-коду.</p>
            <div class="flex items-center gap-2">
              <code class="flex-1 text-xs font-mono text-ink-700 bg-ink-50 rounded-full px-4 py-2.5 truncate">
                {{ team.invite_token }}
              </code>
              <button class="btn-secondary btn-sm" @click="copyInvite">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
                {{ copied ? 'Скопировано' : 'Копировать' }}
              </button>
            </div>
          </div>

          <!-- Members preview -->
          <div class="card-flat p-5">
            <div class="text-xs font-medium text-ink-700 mb-3">Участники</div>
            <div class="space-y-2">
              <div
                v-for="(m, i) in team.members.slice(0, 4)" :key="m.id"
                class="flex items-center gap-2.5"
              >
                <div
                  class="h-8 w-8 rounded-full bg-linear-to-br text-white text-[11px] font-semibold flex items-center justify-center shrink-0"
                  :class="gradientFor(i)"
                >
                  {{ (m.user.full_name || m.user.email).charAt(0).toUpperCase() }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-ink-900 truncate">
                    {{ m.user.full_name || m.user.username }}
                  </div>
                  <div class="text-[11px] text-ink-500">{{ roleLabel[m.role] || m.role }}</div>
                </div>
              </div>
              <div v-if="team.members_count > 4" class="text-[11px] text-ink-400">
                и ещё {{ team.members_count - 4 }}
              </div>
            </div>
          </div>
        </div>

        <!-- Team projects -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-display text-xl font-semibold text-ink-900">Проекты команды</h2>
            <button class="btn-accent btn-sm" @click="showCreate = true">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 5v14M5 12h14"/></svg>
              Новый проект
            </button>
          </div>

          <div v-if="!projects.length" class="card-flat p-10 text-center text-sm text-ink-500">
            Ещё нет проектов в этой команде.
          </div>

          <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            <NuxtLink
              v-for="p in projects" :key="p.id"
              :to="`/app/projects/${p.id}`"
              class="card-flat overflow-hidden group hover:shadow-soft transition-shadow"
            >
              <div class="aspect-4/3 flex items-center justify-center" :class="kindHue[p.kind] || 'bg-ink-50'">
                <span v-if="p.kind === 'fonts'" class="font-display italic text-4xl text-ink-600 opacity-70">Aa</span>
                <span v-else-if="p.kind === 'moodboard'" class="grid grid-cols-3 gap-1 p-3">
                  <div v-for="i in 9" :key="i" class="h-7 w-7 rounded bg-white/80 shadow-sm" />
                </span>
                <span v-else-if="p.kind === 'colors'" class="flex gap-1">
                  <div class="h-9 w-3 rounded-full bg-accent-400" />
                  <div class="h-9 w-3 rounded-full bg-bloom-pink" />
                  <div class="h-9 w-3 rounded-full bg-bloom-mint" />
                  <div class="h-9 w-3 rounded-full bg-bloom-cream" />
                </span>
                <span v-else class="font-display italic text-xl text-ink-500 opacity-70">Проект</span>
              </div>
              <div class="p-5">
                <div class="chip mb-3">{{ kindLabel[p.kind] }}</div>
                <h3 class="font-display text-base font-semibold text-ink-900 group-hover:text-accent-600 transition-colors leading-snug">{{ p.name }}</h3>
                <p v-if="p.description" class="text-xs text-ink-500 mt-2 line-clamp-2">{{ p.description }}</p>
                <div class="text-[11px] text-ink-400 mt-3">Обновлён {{ formatDate(p.updated_at) }}</div>
              </div>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <!-- New project modal -->
    <div v-if="showCreate" class="fixed inset-0 z-50 bg-ink-900/40 backdrop-blur-sm flex items-center justify-center p-4" @click.self="showCreate = false">
      <div class="card w-full max-w-lg p-6">
        <h3 class="font-display text-xl font-semibold text-ink-900 mb-4">Проект в команде</h3>
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
            <FilterSelect v-model="newProjectKindRu" :options="projectKinds" placeholder="Смешанный" />
          </div>
          <div>
            <div class="text-xs font-medium text-ink-700 mb-1.5">Бриф</div>
            <UiInput v-model="newProject.brief" :rows="3" placeholder="Что хотим получить" />
          </div>
        </div>
        <div class="flex gap-2 mt-5 justify-end">
          <button class="btn-secondary" @click="showCreate = false">Отмена</button>
          <button class="btn-accent" @click="createTeamProject">Создать</button>
        </div>
      </div>
    </div>
  </div>
</template>
