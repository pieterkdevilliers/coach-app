import { defineStore } from 'pinia'

export interface AuthUser {
  id: string
  businessId: string
  email: string
  fullName: string
  role: 'owner' | 'coach'
  isActive: boolean
  createdAt: string
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = useCookie<string | null>('access_token', { default: () => null })
  const refreshToken = useCookie<string | null>('refresh_token', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 7,
  })
  const user = ref<AuthUser | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const isOwner = computed(() => user.value?.role === 'owner')

  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  async function login(email: string, password: string) {
    const data = await $fetch<{ accessToken: string; refreshToken: string }>(
      `${apiBase}/api/auth/login`,
      { method: 'POST', body: { email, password } }
    )
    accessToken.value = data.accessToken
    refreshToken.value = data.refreshToken
    await fetchMe()
  }

  async function register(payload: {
    businessName: string
    businessEmail: string
    fullName: string
    email: string
    password: string
  }) {
    const data = await $fetch<{ accessToken: string; refreshToken: string }>(
      `${apiBase}/api/auth/register`,
      {
        method: 'POST',
        body: {
          business_name: payload.businessName,
          business_email: payload.businessEmail,
          full_name: payload.fullName,
          email: payload.email,
          password: payload.password,
        },
      }
    )
    accessToken.value = data.accessToken
    refreshToken.value = data.refreshToken
    await fetchMe()
  }

  async function acceptInvite(token: string, fullName: string, password: string) {
    const data = await $fetch<{ accessToken: string; refreshToken: string }>(
      `${apiBase}/api/auth/accept-invite`,
      { method: 'POST', body: { token, full_name: fullName, password } }
    )
    accessToken.value = data.accessToken
    refreshToken.value = data.refreshToken
    await fetchMe()
  }

  async function fetchMe() {
    if (!accessToken.value) return
    user.value = await $fetch<AuthUser>(`${apiBase}/api/auth/me`, {
      headers: { Authorization: `Bearer ${accessToken.value}` },
    })
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    navigateTo('/auth/login')
  }

  return {
    accessToken,
    user,
    isAuthenticated,
    isOwner,
    login,
    register,
    acceptInvite,
    fetchMe,
    logout,
  }
})
