import { staticGreetingRepo } from './repo'
import { greetingRoutes } from './routes'
import { createGreet } from './use-case'

export const greetings = () => greetingRoutes(createGreet(staticGreetingRepo))
