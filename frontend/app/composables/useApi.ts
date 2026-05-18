import type { FetchOptions } from 'ofetch'
import { useAuthStore } from '~/stores/auth'

export function useApi() {
  const auth = useAuthStore()
  const { apiBase } = useRuntimeConfig().public

  async function request<T>(url: string, options: FetchOptions = {}): Promise<T> {
    const headers: Record<string, string> = {
      ...((options.headers as Record<string, string>) || {}),
    }
    if (auth.access) headers.Authorization = `Bearer ${auth.access}`
    try {
      return await $fetch<T>(`${apiBase}${url}`, { ...options, headers } as any)
    } catch (err: any) {
      if (err?.status === 401 && auth.refresh) {
        const ok = await auth.refreshAccess()
        if (ok && auth.access) {
          headers.Authorization = `Bearer ${auth.access}`
          return await $fetch<T>(`${apiBase}${url}`, { ...options, headers } as any)
        }
      }
      throw err
    }
  }

  return {
    get: <T>(url: string, options: FetchOptions = {}) =>
      request<T>(url, { ...options, method: 'GET' }),
    post: <T>(url: string, body?: any, options: FetchOptions = {}) =>
      request<T>(url, { ...options, method: 'POST', body }),
    patch: <T>(url: string, body?: any, options: FetchOptions = {}) =>
      request<T>(url, { ...options, method: 'PATCH', body }),
    put: <T>(url: string, body?: any, options: FetchOptions = {}) =>
      request<T>(url, { ...options, method: 'PUT', body }),
    delete: <T>(url: string, options: FetchOptions = {}) =>
      request<T>(url, { ...options, method: 'DELETE' }),
  }
}
