import { useAuthStore } from '~/stores/auth'

/**
 * Runs once on the client before any route middleware — loads tokens from
 * localStorage and fetches the current user so that auth/guest middleware
 * see the correct state on hard reloads.
 */
export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  if (!auth.ready) {
    await auth.bootstrap()
  }
})
