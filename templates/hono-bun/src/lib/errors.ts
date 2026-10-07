import type { Context } from 'hono'
import type { RequestIdVariables } from 'hono/request-id'
import type { ContentfulStatusCode } from 'hono/utils/http-status'

export type AppEnv = { Variables: RequestIdVariables }

export function errorResponse(c: Context<AppEnv>, status: ContentfulStatusCode, code: string, message: string) {
  return c.json({ error: { code, message, requestId: c.get('requestId') } }, status)
}
