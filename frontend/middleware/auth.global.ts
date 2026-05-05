function tokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

export default defineNuxtRouteMiddleware((to) => {
  if (to.path.startsWith('/auth')) return

  const authStore = useAuthStore()

  if (!authStore.isAuthenticated || tokenExpired(authStore.accessToken!)) {
    authStore.accessToken = null
    return navigateTo('/auth/login')
  }
})
