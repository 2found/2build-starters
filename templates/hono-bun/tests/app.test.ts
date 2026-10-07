import { describe, expect, test } from 'bun:test'
import { createApp } from '../src/app'
import { parseEnv } from '../src/lib/env'
import { createGreet } from '../src/modules/greetings/use-case'
import { z } from 'zod'

const errorSchema = z.object({ error: z.object({ code: z.string(), message: z.string(), requestId: z.string() }) })

const app = createApp()
const post = (body: string) => app.request('/greetings', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body,
})

describe('HTTP boundaries', () => {
  test('health and readiness respond without external services', async () => {
    for (const path of ['/healthz', '/readyz']) expect((await app.request(path)).status).toBe(200)
  })

  test('validates, trims and renders a localized greeting', async () => {
    const response = await post(JSON.stringify({ name: '  Long  ', locale: 'vi' }))
    expect(response.status).toBe(200)
    expect(await response.json()).toEqual({ message: 'Xin chào, Long!' })
    expect(response.headers.get('x-request-id')).toBeTruthy()
  })

  test.each([
    { name: '' }, { name: '   ' }, { name: 'a'.repeat(81) },
    { name: 'Long', locale: 'fr' }, { name: 'Long', unexpected: true }, {},
  ])('rejects invalid input %j', async (input) => {
    const response = await post(JSON.stringify(input))
    expect(response.status).toBe(400)
    const body = errorSchema.parse(await response.json())
    expect(body.error.code).toBe('INVALID_INPUT')
    expect(response.headers.get('x-request-id') ?? '').toBe(body.error.requestId)
  })

  test('malformed JSON and unknown routes use the error envelope', async () => {
    for (const [response, status] of [[await post('{'), 400], [await app.request('/missing'), 404]] as const) {
      expect(response.status).toBe(status)
      const body = errorSchema.parse(await response.json())
      expect(response.headers.get('x-request-id') ?? '').toBe(body.error.requestId)
      expect(body.error.message).toBeTruthy()
    }
  })

  test('unexpected failures hide internal details', async () => {
    const failing = createApp()
    failing.get('/failure', () => { throw new Error('private implementation detail') })
    const response = await failing.request('/failure')
    expect(response.status).toBe(500)
    expect(await response.text()).not.toContain('private implementation detail')
  })
})

test('use case accepts a repository adapter without HTTP', () => {
  const greet = createGreet({ salutation: () => 'Welcome' })
  expect(greet({ name: 'Long', locale: 'en' })).toEqual({ message: 'Welcome, Long!' })
})

test('environment has local defaults and rejects invalid ports/modes', () => {
  expect(parseEnv({})).toEqual({ PORT: 3000, NODE_ENV: 'development' })
  for (const PORT of ['', '0', '65536', 'abc']) expect(() => parseEnv({ PORT })).toThrow()
  expect(() => parseEnv({ NODE_ENV: 'unknown' })).toThrow()
})
