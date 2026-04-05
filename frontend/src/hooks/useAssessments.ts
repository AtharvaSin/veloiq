import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import type {
  PaginatedResponse,
  AssessmentRead,
  AssessmentsListParams,
  UUID,
} from '@/lib/types'

const BASE = '/assessments'

export function useAssessmentsList(params: AssessmentsListParams = {}) {
  return useQuery({
    queryKey: queryKeys.assessments.list(params),
    queryFn: () =>
      apiGet<PaginatedResponse<AssessmentRead>>(BASE, params as Record<string, unknown>),
  })
}

export function useAssessmentDetail(id: UUID, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.assessments.detail(id),
    queryFn: () => apiGet<AssessmentRead>(`${BASE}/${id}`),
    enabled: options?.enabled ?? Boolean(id),
  })
}
