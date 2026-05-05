export function useAuthFetch() {
  const authStore = useAuthStore()
  const config = useRuntimeConfig()

  function authHeaders() {
    return authStore.accessToken
      ? { Authorization: `Bearer ${authStore.accessToken}` }
      : {}
  }

  async function apiFetch<T>(path: string, options: Parameters<typeof $fetch>[1] = {}): Promise<T> {
    try {
      return await $fetch<T>(`${config.public.apiBase}${path}`, {
        ...options,
        headers: { ...authHeaders(), ...(options.headers ?? {}) },
      })
    } catch (err: unknown) {
      if ((err as { status?: number })?.status === 401) {
        authStore.logout()
      }
      throw err
    }
  }

  return { apiFetch }
}
