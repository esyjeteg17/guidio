<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'app', middleware: 'auth' })
useHead({ title: 'Профиль — Guidio' })

const auth = useAuthStore()
const api = useApi()

const form = reactive({
  full_name: auth.user?.full_name || '',
  username: auth.user?.username || '',
  role: auth.user?.role || '',
  bio: auth.user?.bio || '',
})
const passwords = reactive({ old_password: '', new_password: '' })

const saving = ref(false)
const savingPwd = ref(false)
const msg = ref<string | null>(null)
const error = ref<string | null>(null)

watch(() => auth.user, (u) => {
  if (u) {
    form.full_name = u.full_name
    form.username = u.username
    form.role = u.role
    form.bio = u.bio
  }
}, { immediate: true })

async function save() {
  saving.value = true
  msg.value = null
  error.value = null
  try {
    await auth.updateMe({ ...form })
    msg.value = 'Профиль обновлён'
  } catch (e: any) {
    error.value = e?.data?.detail || 'Не удалось сохранить'
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  if (!passwords.old_password || !passwords.new_password) return
  savingPwd.value = true
  msg.value = null
  error.value = null
  try {
    await api.post('/auth/password/', { ...passwords })
    passwords.old_password = ''
    passwords.new_password = ''
    msg.value = 'Пароль обновлён'
  } catch (e: any) {
    error.value = e?.data?.old_password?.[0] || e?.data?.new_password?.[0] || 'Не удалось обновить пароль'
  } finally {
    savingPwd.value = false
  }
}
</script>

<template>
  <div class="min-h-full flex flex-col">
    <PageHeader :crumbs="[{ label: 'Настройки профиля' }]" />

    <div class="flex-1 px-6 lg:px-10 py-8">
      <div class="max-w-225 mx-auto">
        <h1 class="font-display text-3xl font-semibold text-ink-900 mb-8">Профиль</h1>

        <div class="grid lg:grid-cols-3 gap-6">
          <!-- Avatar card -->
          <aside class="card-flat p-6 text-center h-fit">
            <div class="mx-auto h-24 w-24 rounded-3xl bg-linear-to-br from-accent-400 to-bloom-pink text-white text-3xl font-display font-semibold flex items-center justify-center shadow-lg">
              {{ (auth.user?.full_name || auth.user?.email || 'U').charAt(0).toUpperCase() }}
            </div>
            <div class="font-display text-lg font-semibold mt-4 text-ink-900">{{ auth.user?.full_name || auth.user?.username }}</div>
            <div class="text-xs text-ink-500 mt-0.5">{{ auth.user?.email }}</div>
            <div v-if="auth.user?.role" class="chip mx-auto mt-3 inline-flex">{{ auth.user.role }}</div>

            <button class="btn-secondary btn-sm w-full mt-5">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
              Загрузить аватар
            </button>
          </aside>

          <!-- Settings -->
          <section class="card-flat p-6 lg:col-span-2 space-y-6">
            <div>
              <h3 class="font-display text-lg font-semibold text-ink-900 mb-4">Личные данные</h3>
              <div class="grid sm:grid-cols-2 gap-4">
                <div>
                  <div class="text-xs font-medium text-ink-700 mb-1.5">Имя</div>
                  <UiInput v-model="form.full_name" />
                </div>
                <div>
                  <div class="text-xs font-medium text-ink-700 mb-1.5">Логин</div>
                  <UiInput v-model="form.username" />
                </div>
                <div class="sm:col-span-2">
                  <div class="text-xs font-medium text-ink-700 mb-1.5">Роль</div>
                  <UiInput v-model="form.role" placeholder="Designer, Lead, Student" />
                </div>
                <div class="sm:col-span-2">
                  <div class="text-xs font-medium text-ink-700 mb-1.5">О себе</div>
                  <UiInput v-model="form.bio" :rows="3" placeholder="Пара слов о вашем опыте и интересах" />
                </div>
              </div>
              <button class="btn-accent mt-4" :disabled="saving" @click="save">
                {{ saving ? 'Сохраняем…' : 'Сохранить изменения' }}
              </button>
            </div>

            <div class="h-px bg-ink-100" />

            <div>
              <h3 class="font-display text-lg font-semibold text-ink-900 mb-4">Сменить пароль</h3>
              <div class="grid sm:grid-cols-2 gap-4">
                <div>
                  <div class="text-xs font-medium text-ink-700 mb-1.5">Текущий пароль</div>
                  <UiInput v-model="passwords.old_password" type="password" autocomplete="current-password" />
                </div>
                <div>
                  <div class="text-xs font-medium text-ink-700 mb-1.5">Новый пароль</div>
                  <UiInput v-model="passwords.new_password" type="password" autocomplete="new-password" />
                </div>
              </div>
              <button class="btn-secondary mt-4" :disabled="savingPwd" @click="changePassword">
                {{ savingPwd ? 'Обновляем…' : 'Обновить пароль' }}
              </button>
            </div>

            <Transition enter-active-class="transition-opacity duration-200" enter-from-class="opacity-0">
              <p v-if="msg" class="text-sm text-emerald-600 flex items-center gap-1.5">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m5 12 5 5L20 7"/></svg>
                {{ msg }}
              </p>
            </Transition>
            <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>
