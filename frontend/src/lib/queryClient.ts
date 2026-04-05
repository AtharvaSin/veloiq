import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // 30s — treat data as fresh for this long
      gcTime: 5 * 60_000, // 5min — keep in cache after unused
      retry: 1, // retry once on failure
      refetchOnWindowFocus: false, // POC — don't thrash backend
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 0, // POST/PATCH failures should bubble immediately
    },
  },
})
