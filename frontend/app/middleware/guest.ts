import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async () => {
  if (import.meta.server) return
  const auth = useAuthStore()
  if (!auth.ready) {
    await auth.bootstrap()
  }
  if (auth.isAuthenticated) return navigateTo('/app/start')
})
