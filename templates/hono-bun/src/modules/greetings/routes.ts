import { Hono } from 'hono'
import { validator } from 'hono/validator'
import { z } from 'zod'
import { errorResponse, type AppEnv } from '../../lib/errors'
import type { createGreet } from './use-case'

const inputSchema = z.object({
  name: z.string().trim().min(1).max(80),
  locale: z.enum(['en', 'vi']).default('en'),
}).strict()

export function greetingRoutes(greet: ReturnType<typeof createGreet>) {
  return new Hono<AppEnv>().post('/', validator('json', (value, c) => {
    const result = inputSchema.safeParse(value)
    if (!result.success) return errorResponse(c, 400, 'INVALID_INPUT', 'Provide a name of 1–80 characters and a supported locale.')
    return result.data
  }), (c) => c.json(greet(c.req.valid('json'))))
}
