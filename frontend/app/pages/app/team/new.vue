<script setup lang="ts">
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'app', middleware: 'auth' })
useHead({ title: 'Команды — Guidio' })

interface Team {
  id: number
  name: string
  description: string
  avatar: string | null
  invite_token: string
  members: { id: number; user: { full_name: string; email: string }; role: string }[]
  members_count: number
  created_at: string
}

const api = useApi()
const teams = ref<Team[]>([])
const form = reactive({ name: '', description: '' })
const joinToken = ref('')
const loading = ref(false)
const error = ref<string | null>(null)
const inviteOrigin = computed(() => import.meta.client ? window.location.origin : '')
const showCreate = ref(false)

async function load() {
  const data = await api.get<{ results: Team[] } | Team[]>('/teams/')
  teams.value = Array.isArray(data) ? data : data.results
}

async function createTeam() {
  if (!form.name.trim()) return
  loading.value = true
  error.value = null
  try {
    await api.post<Team>('/teams/', { ...form })
    form.name = ''
    form.description = ''
    showCreate.value = false
    await load()
  } catch (e: any) {
    error.value = e?.data?.detail || 'Не удалось создать команду'
  } finally {
    loading.value = false
  }
}

async function joinTeam() {
  if (!joinToken.value.trim()) return
  try {
    await api.post('/teams/join/', { invite_token: joinToken.value.trim() })
    joinToken.value = ''
    await load()
  } catch (e: any) {
    error.value = e?.data?.detail || 'Неверный код приглашения'
  }
}

function copyInvite(t: Team) {
  navigator.clipboard?.writeText(`${inviteOrigin.value}/invite/${t.invite_token}`)
}

const avatarGradients = [
  'from-accent-400 to-bloom-pink',
  'from-bloom-lilac to-accent-500',
  'from-bloom-peri to-accent-400',
  'from-bloom-mint to-accent-300',
  'from-bloom-pink to-bloom-lilac',
]

function gradientFor(i: number) {
  return avatarGradients[i % avatarGradients.length]
}

onMounted(load)
</script>

<template>
  <div class="min-h-full flex flex-col">
    <PageHeader :crumbs="[{ label: 'Команды' }]" />

    <div class="flex-1 px-6 lg:px-10 py-8">
      <div class="max-w-275 mx-auto">
        <div class="flex items-center justify-between mb-6 flex-wrap gap-3">
          <div>
            <h1 class="font-display text-3xl font-semibold text-ink-900">Мои команды</h1>
            <p class="text-sm text-ink-500 mt-1">Приглашайте коллег и работайте над подборками вместе.</p>
          </div>
          <button class="btn-accent btn-sm" @click="showCreate = true">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 5v14M5 12h14"/></svg>
            Новая команда
          </button>
        </div>

        <!-- Join by code -->
        <div class="card-flat p-5 mb-8 flex flex-wrap items-end gap-4">
          <div class="flex-1 min-w-60">
            <div class="text-xs font-medium text-ink-700 mb-1.5">Присоединиться по коду</div>
            <UiInput v-model="joinToken" placeholder="Вставьте invite-код" />
          </div>
          <button class="btn-secondary" @click="joinTeam">Присоединиться</button>
        </div>

        <div v-if="!teams.length" class="card-flat p-12 text-center">
          <div class="text-ink-500 text-sm">Пока нет команд. Создайте первую или присоединитесь по коду.</div>
        </div>

        <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <NuxtLink
            v-for="(t, idx) in teams" :key="t.id"
            :to="`/app/team/${t.id}`"
            class="card-flat p-5 hover:shadow-soft transition-shadow block"
          >
            <div class="flex items-center gap-3 mb-4">
              <div
                class="h-11 w-11 rounded-2xl bg-linear-to-br text-white font-display font-semibold flex items-center justify-center text-lg"
                :class="gradientFor(idx)"
              >
                {{ t.name.charAt(0).toUpperCase() }}
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="font-display text-base font-semibold text-ink-900 truncate">{{ t.name }}</h4>
                <div class="text-xs text-ink-500">{{ t.members_count }} участник{{ t.members_count === 1 ? '' : t.members_count < 5 ? 'а' : 'ов' }}</div>
              </div>
            </div>

            <p v-if="t.description" class="text-sm text-ink-500 line-clamp-2 mb-4">{{ t.description }}</p>

            <div class="flex -space-x-2 mb-4">
              <div
                v-for="(m, i) in t.members.slice(0, 5)" :key="m.id"
                class="h-7 w-7 rounded-full bg-linear-to-br ring-2 ring-white text-white text-[10px] font-semibold flex items-center justify-center"
                :class="gradientFor(i)"
                :title="m.user.full_name || m.user.email"
              >
                {{ (m.user.full_name || m.user.email).charAt(0).toUpperCase() }}
              </div>
              <div
                v-if="t.members_count > 5"
                class="h-7 w-7 rounded-full bg-ink-100 ring-2 ring-white text-[10px] font-semibold text-ink-600 flex items-center justify-center"
              >
                +{{ t.members_count - 5 }}
              </div>
            </div>

            <div class="flex items-center gap-2 pt-3 border-t border-ink-100">
              <code class="text-[11px] font-mono text-ink-500 truncate flex-1">{{ t.invite_token }}</code>
              <button
                class="btn-secondary btn-sm"
                @click.stop.prevent="copyInvite(t)"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
                Копировать
              </button>
            </div>
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <div v-if="showCreate" class="fixed inset-0 z-50 bg-ink-900/40 backdrop-blur-sm flex items-center justify-center p-4" @click.self="showCreate = false">
      <div class="card w-full max-w-lg p-6">
        <h3 class="font-display text-xl font-semibold text-ink-900 mb-4">Новая команда</h3>
        <div class="space-y-4">
          <div>
            <div class="text-xs font-medium text-ink-700 mb-1.5">Название</div>
            <UiInput v-model="form.name" placeholder="Design Studio" />
          </div>
          <div>
            <div class="text-xs font-medium text-ink-700 mb-1.5">Описание</div>
            <UiInput v-model="form.description" :rows="3" placeholder="Над чем работает команда" />
          </div>
          <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
        </div>
        <div class="flex gap-2 mt-5 justify-end">
          <button class="btn-secondary" @click="showCreate = false">Отмена</button>
          <button class="btn-accent" :disabled="loading" @click="createTeam">
            {{ loading ? 'Создаём…' : 'Создать' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
