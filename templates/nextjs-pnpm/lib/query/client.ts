import { QueryClient } from '@tanstack/react-query'
import { ApiError } from '@/lib/api'

// These defaults are load limits, not preferences: focus refetches and retries of
// client errors multiply API traffic. Opt into fresher data per query instead.
export function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60_000,
        refetchOnWindowFocus: false,
        retry: (failures, error) => !(error instanceof ApiError && error.status < 500) && failures < 2,
      },
    },
  })
}
