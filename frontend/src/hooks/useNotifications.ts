import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import type {
  PaginatedResponse,
  NotificationRead,
  NotificationsListParams,
  UUID,
} from '@/lib/types'

const BASE = '/notifications'

export function useNotificationsList(params: NotificationsListParams = {}) {
  return useQuery({
    queryKey: queryKeys.notifications.list(params),
    queryFn: () =>
      apiGet<PaginatedResponse<NotificationRead>>(BASE, params as Record<string, unknown>),
  })
}

export function useNotificationDetail(id: UUID, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.notifications.detail(id),
    queryFn: () => apiGet<NotificationRead>(`${BASE}/${id}`),
    enabled: options?.enabled ?? Boolean(id),
  })
}
