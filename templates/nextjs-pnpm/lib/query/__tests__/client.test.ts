import { describe, expect, test } from 'vitest'
import { ApiError } from '@/lib/api'
import { makeQueryClient } from '@/lib/query/client'
import { qk } from '@/lib/query/keys'

describe('query client load limits', () => {
  const queries = makeQueryClient().getDefaultOptions().queries!
  const retry = queries.retry as (failures: number, error: unknown) => boolean

  test('keeps conservative global defaults', () => {
    expect(queries.staleTime).toBe(60_000)
    expect(queries.refetchOnWindowFocus).toBe(false)
  })

  test('never retries a client error, retries server errors at most twice', () => {
    expect(retry(0, new ApiError(404, 'NOT_FOUND', 'missing'))).toBe(false)
    expect(retry(0, new ApiError(503, 'UNAVAILABLE', 'down'))).toBe(true)
    expect(retry(2, new ApiError(503, 'UNAVAILABLE', 'down'))).toBe(false)
  })

  test('keys come from qk', () => {
    expect(qk.health()).toEqual(['health'])
  })
})
