import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import type {
  PaginatedResponse,
  MatchResultRead,
  MatchesListParams,
  UUID,
} from '@/lib/types'

const BASE = '/matches'

export function useMatchesList(params: MatchesListParams = {}) {
  return useQuery({
    queryKey: queryKeys.matches.list(params),
    queryFn: () =>
      apiGet<PaginatedResponse<MatchResultRead>>(BASE, params as Record<string, unknown>),
  })
}

export function useMatchDetail(id: UUID, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.matches.detail(id),
    queryFn: () => apiGet<MatchResultRead>(`${BASE}/${id}`),
    enabled: options?.enabled ?? Boolean(id),
  })
}
