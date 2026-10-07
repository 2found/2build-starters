import type { Locale } from './domain'

export interface GreetingRepo {
  salutation(locale: Locale): string
}

// A static adapter keeps the starter stateless. A database adapter would own
// queries here without changing route or use-case contracts.
export const staticGreetingRepo: GreetingRepo = {
  salutation: (locale) => ({ en: 'Hello', vi: 'Xin chào' })[locale],
}
