'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import { makeQueryClient } from '@/lib/query/client'

// One QueryClient per browser session. An SPA-style login/logout must call
// queryClient.clear() so viewer-scoped data never leaks across accounts.
export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(makeQueryClient)
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
