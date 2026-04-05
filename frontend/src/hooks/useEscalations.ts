import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiPatch, type ApiError } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import type {
  PaginatedResponse,
  SalesEscalationRead,
  SalesEscalationUpdate,
  EscalationsListParams,
  UUID,
} from '@/lib/types'

const BASE = '/escalations'

export function useEscalationsList(params: EscalationsListParams = {}) {
  return useQuery({
    queryKey: queryKeys.escalations.list(params),
    queryFn: () =>
      apiGet<PaginatedResponse<SalesEscalationRead>>(BASE, params as Record<string, unknown>),
  })
}

export function useEscalationDetail(id: UUID, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.escalations.detail(id),
    queryFn: () => apiGet<SalesEscalationRead>(`${BASE}/${id}`),
    enabled: options?.enabled ?? Boolean(id),
  })
}

export function useUpdateEscalation() {
  const qc = useQueryClient()
  return useMutation<
    SalesEscalationRead,
    ApiError,
    { id: UUID; input: SalesEscalationUpdate }
  >({
    mutationFn: ({ id, input }) =>
      apiPatch<SalesEscalationRead, SalesEscalationUpdate>(`${BASE}/${id}`, input),
    onSuccess: (_data, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.escalations.all })
      qc.invalidateQueries({ queryKey: queryKeys.escalations.detail(id) })
    },
  })
}
