export function useApi() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  function url(path: string): string {
    return `${apiBase}${path}`
  }

  return { apiBase, url }
}
