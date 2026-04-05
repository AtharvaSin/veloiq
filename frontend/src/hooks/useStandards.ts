import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiPost, apiPatch, type ApiError } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import type {
  PaginatedResponse,
  StandardRead,
  StandardCreate,
  StandardUpdate,
  StandardsListParams,
  UUID,
} from '@/lib/types'

const BASE = '/standards'

export function useStandardsList(params: StandardsListParams = {}) {
  return useQuery({
    queryKey: queryKeys.standards.list(params),
    queryFn: () =>
      apiGet<PaginatedResponse<StandardRead>>(BASE, params as Record<string, unknown>),
  })
}

export function useStandardDetail(id: UUID, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.standards.detail(id),
    queryFn: () => apiGet<StandardRead>(`${BASE}/${id}`),
    enabled: options?.enabled ?? Boolean(id),
  })
}

export function useCreateStandard() {
  const qc = useQueryClient()
  return useMutation<StandardRead, ApiError, StandardCreate>({
    mutationFn: (input) => apiPost<StandardRead, StandardCreate>(BASE, input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.standards.all })
    },
  })
}

export function useUpdateStandard() {
  const qc = useQueryClient()
  return useMutation<StandardRead, ApiError, { id: UUID; input: StandardUpdate }>({
    mutationFn: ({ id, input }) =>
      apiPatch<StandardRead, StandardUpdate>(`${BASE}/${id}`, input),
    onSuccess: (_data, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.standards.all })
      qc.invalidateQueries({ queryKey: queryKeys.standards.detail(id) })
    },
  })
}
