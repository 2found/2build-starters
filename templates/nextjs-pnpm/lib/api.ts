import { parseEnv } from './env'

// Mirrors the API error envelope: { error: { code, message, requestId } }.
export class ApiError extends Error {
  constructor(readonly status: number, readonly code: string, message: string, readonly requestId?: string) {
    super(message)
    this.name = 'ApiError'
  }
}

type ErrorBody = { error?: { code?: string; message?: string; requestId?: string } }

// Server components fetch through apiFetch; client components wrap it in a
// TanStack query keyed from qk. Never send identity from a cacheable page.
export async function apiFetch<T>(path: string, init?: RequestInit & { baseUrl?: string }): Promise<T> {
  const { baseUrl = parseEnv(process.env).API_URL, ...request } = init ?? {}
  const response = await fetch(new URL(path, baseUrl), request)
  if (response.ok) return (await response.json()) as T
  const body = (await response.json().catch(() => ({}))) as ErrorBody
  throw new ApiError(
    response.status,
    body.error?.code ?? 'HTTP_ERROR',
    body.error?.message ?? `Request failed with ${response.status}`,
    body.error?.requestId ?? response.headers.get('x-request-id') ?? undefined,
  )
}
