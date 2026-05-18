import { defineStore } from 'pinia'

export interface User {
  id: number
  email: string
  username: string
  full_name: string
  avatar: string | null
  role: string
  bio: string
  created_at: string
}

interface Tokens {
  access: string
  refresh: string
}

const STORAGE_KEY = 'guidio-auth'

function readStorage(): Tokens | null {
  if (import.meta.server) return null
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as Tokens) : null
  } catch {
    return null
  }
}

function writeStorage(tokens: Tokens | null) {
  if (import.meta.server) return
  if (tokens) localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens))
  else localStorage.removeItem(STORAGE_KEY)
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const access = ref<string | null>(null)
  const refresh = ref<string | null>(null)
  const ready = ref(false)

  const isAuthenticated = computed(() => !!user.value && !!access.value)

  function setTokens(tokens: Tokens) {
    access.value = tokens.access
    refresh.value = tokens.refresh
    writeStorage(tokens)
  }

  function clear() {
    user.value = null
    access.value = null
    refresh.value = null
    writeStorage(null)
  }

  async function fetchMe() {
    if (!access.value) return
    const { apiBase } = useRuntimeConfig().public
    user.value = await $fetch<User>(`${apiBase}/auth/me/`, {
      headers: { Authorization: `Bearer ${access.value}` },
    })
  }

  async function bootstrap() {
    if (import.meta.server) {
      ready.value = true
      return
    }
    const stored = readStorage()
    if (stored) {
      access.value = stored.access
      refresh.value = stored.refresh
      try {
        await fetchMe()
      } catch {
        clear()
      }
    }
    ready.value = true
  }

  async function login(email: string, password: string) {
    const { apiBase } = useRuntimeConfig().public
    const data = await $fetch<Tokens>(`${apiBase}/auth/login/`, {
      method: 'POST',
      body: { email, password },
    })
    setTokens(data)
    await fetchMe()
  }

  async function register(payload: {
    email: string
    username: string
    full_name: string
    password: string
    password_confirm: string
  }) {
    const { apiBase } = useRuntimeConfig().public
    const data = await $fetch<{ user: User } & Tokens>(`${apiBase}/auth/register/`, {
      method: 'POST',
      body: payload,
    })
    setTokens({ access: data.access, refresh: data.refresh })
    user.value = data.user
  }

  async function updateMe(patch: Partial<Pick<User, 'full_name' | 'role' | 'bio' | 'username'>>) {
    const { apiBase } = useRuntimeConfig().public
    const updated = await $fetch<User>(`${apiBase}/auth/me/`, {
      method: 'PATCH',
      body: patch,
      headers: { Authorization: `Bearer ${access.value}` },
    })
    user.value = { ...(user.value || ({} as User)), ...updated }
  }

  async function refreshAccess(): Promise<boolean> {
    if (!refresh.value) return false
    const { apiBase } = useRuntimeConfig().public
    try {
      const data = await $fetch<{ access: string; refresh?: string }>(`${apiBase}/auth/refresh/`, {
        method: 'POST',
        body: { refresh: refresh.value },
      })
      access.value = data.access
      if (data.refresh) refresh.value = data.refresh
      writeStorage({ access: access.value!, refresh: refresh.value! })
      return true
    } catch {
      clear()
      return false
    }
  }

  async function logout() {
    const { apiBase } = useRuntimeConfig().public
    if (refresh.value && access.value) {
      try {
        await $fetch(`${apiBase}/auth/logout/`, {
          method: 'POST',
          body: { refresh: refresh.value },
          headers: { Authorization: `Bearer ${access.value}` },
        })
      } catch {}
    }
    clear()
    await navigateTo('/login')
  }

  return {
    user,
    access,
    refresh,
    ready,
    isAuthenticated,
    bootstrap,
    setTokens,
    login,
    register,
    fetchMe,
    updateMe,
    refreshAccess,
    logout,
    clear,
  }
})
