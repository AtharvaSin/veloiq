import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiPost, apiPatch, type ApiError } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import type {
  PaginatedResponse,
  CustomerRead,
  CustomerCreate,
  CustomerUpdate,
  CustomersListParams,
  UUID,
} from '@/lib/types'

const BASE = '/customers'

export function useCustomersList(params: CustomersListParams = {}) {
  return useQuery({
    queryKey: queryKeys.customers.list(params),
    queryFn: () =>
      apiGet<PaginatedResponse<CustomerRead>>(BASE, params as Record<string, unknown>),
  })
}

export function useCustomerDetail(id: UUID, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.customers.detail(id),
    queryFn: () => apiGet<CustomerRead>(`${BASE}/${id}`),
    enabled: options?.enabled ?? Boolean(id),
  })
}

export function useCreateCustomer() {
  const qc = useQueryClient()
  return useMutation<CustomerRead, ApiError, CustomerCreate>({
    mutationFn: (input) => apiPost<CustomerRead, CustomerCreate>(BASE, input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.customers.all })
    },
  })
}

export function useUpdateCustomer() {
  const qc = useQueryClient()
  return useMutation<CustomerRead, ApiError, { id: UUID; input: CustomerUpdate }>({
    mutationFn: ({ id, input }) =>
      apiPatch<CustomerRead, CustomerUpdate>(`${BASE}/${id}`, input),
    onSuccess: (_data, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.customers.all })
      qc.invalidateQueries({ queryKey: queryKeys.customers.detail(id) })
    },
  })
}
