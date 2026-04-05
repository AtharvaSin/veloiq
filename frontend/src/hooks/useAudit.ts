import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import type {
  PaginatedResponse,
  AuditLogRead,
  AuditListParams,
  UUID,
} from '@/lib/types'

const BASE = '/audit'

export function useAuditList(params: AuditListParams = {}) {
  return useQuery({
    queryKey: queryKeys.audit.list(params),
    queryFn: () =>
      apiGet<PaginatedResponse<AuditLogRead>>(BASE, params as Record<string, unknown>),
  })
}

export function useAuditDetail(id: UUID, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.audit.detail(id),
    queryFn: () => apiGet<AuditLogRead>(`${BASE}/${id}`),
    enabled: options?.enabled ?? Boolean(id),
  })
}
