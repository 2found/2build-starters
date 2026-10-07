import { Hono } from 'hono'
import { HTTPException } from 'hono/http-exception'
import { logger } from 'hono/logger'
import { requestId } from 'hono/request-id'
import { errorResponse, type AppEnv } from './lib/errors'
import { greetings } from './modules/greetings'

export function createApp() {
  const app = new Hono<AppEnv>()
  app.use('*', requestId())
  app.use('*', logger())
  app.get('/healthz', (c) => c.json({ status: 'ok' }))
  // No external dependencies yet. Add dependency probes before claiming readiness
  // when integrating a database or another required service.
  app.get('/readyz', (c) => c.json({ status: 'ready' }))
  app.route('/greetings', greetings())
  app.notFound((c) => errorResponse(c, 404, 'NOT_FOUND', 'Route not found.'))
  app.onError((error, c) => {
    if (error instanceof HTTPException) {
      return errorResponse(c, error.status, 'INVALID_REQUEST', 'Request could not be processed.')
    }
    console.error({ requestId: c.get('requestId'), error })
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'An unexpected error occurred.')
  })
  return app
}
