import { createApp } from './app'
import { parseEnv } from './lib/env'

const env = parseEnv(process.env)
const server = Bun.serve({ port: env.PORT, fetch: createApp().fetch })
console.info(`Listening on http://localhost:${server.port}`)
