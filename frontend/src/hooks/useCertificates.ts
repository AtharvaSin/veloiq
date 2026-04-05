import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiPost, apiPatch, type ApiError } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import type {
  PaginatedResponse,
  CertificateRead,
  CertificateCreate,
  CertificateUpdate,
  CertificatesListParams,
  UUID,
} from '@/lib/types'

const BASE = '/certificates'

export function useCertificatesList(params: CertificatesListParams = {}) {
  return useQuery({
    queryKey: queryKeys.certificates.list(params),
    queryFn: () =>
      apiGet<PaginatedResponse<CertificateRead>>(BASE, params as Record<string, unknown>),
  })
}

export function useCertificateDetail(id: UUID, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.certificates.detail(id),
    queryFn: () => apiGet<CertificateRead>(`${BASE}/${id}`),
    enabled: options?.enabled ?? Boolean(id),
  })
}

export function useCreateCertificate() {
  const qc = useQueryClient()
  return useMutation<CertificateRead, ApiError, CertificateCreate>({
    mutationFn: (input) => apiPost<CertificateRead, CertificateCreate>(BASE, input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.certificates.all })
    },
  })
}

export function useUpdateCertificate() {
  const qc = useQueryClient()
  return useMutation<CertificateRead, ApiError, { id: UUID; input: CertificateUpdate }>({
    mutationFn: ({ id, input }) =>
      apiPatch<CertificateRead, CertificateUpdate>(`${BASE}/${id}`, input),
    onSuccess: (_data, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.certificates.all })
      qc.invalidateQueries({ queryKey: queryKeys.certificates.detail(id) })
    },
  })
}
