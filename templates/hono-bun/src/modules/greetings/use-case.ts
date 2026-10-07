import type { GreetingInput } from './domain'
import type { GreetingRepo } from './repo'

export const createGreet = (repo: GreetingRepo) => (input: GreetingInput) => ({
  message: `${repo.salutation(input.locale)}, ${input.name}!`,
})
