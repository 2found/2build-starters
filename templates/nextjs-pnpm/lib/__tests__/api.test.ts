import { afterEach, describe, expect, test, vi } from 'vitest'
import { ApiError, apiFetch } from '@/lib/api'
import { parseEnv } from '@/lib/env'

afterEach(() => vi.unstubAllGlobals())

const respond = (status: number, body: unknown, headers: Record<string, string> = {}) =>
  vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify(body), { status, headers })))

describe('apiFetch', () => {
  test('returns JSON on success', async () => {
    respond(200, { status: 'ok' })
    await expect(apiFetch('/healthz', { baseUrl: 'http://api.test' })).resolves.toEqual({ status: 'ok' })
  })

  test('maps the API error envelope to ApiError', async () => {
    respond(400, { error: { code: 'INVALID_INPUT', message: 'Provide a name.', requestId: 'req-1' } })
    const error = await apiFetch('/greetings', { baseUrl: 'http://api.test' }).catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 400, code: 'INVALID_INPUT', message: 'Provide a name.', requestId: 'req-1' })
  })

  test('survives a non-JSON error body', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('bad gateway', { status: 502, headers: { 'x-request-id': 'req-2' } })))
    await expect(apiFetch('/x', { baseUrl: 'http://api.test' })).rejects.toMatchObject({ status: 502, code: 'HTTP_ERROR', requestId: 'req-2' })
  })
})

test('environment has a local default and rejects an invalid API URL', () => {
  expect(parseEnv({}).API_URL).toBe('http://localhost:3000')
  expect(() => parseEnv({ API_URL: 'not a url' })).toThrow()
})
