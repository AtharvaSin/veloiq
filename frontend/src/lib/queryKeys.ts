/**
 * Centralized TanStack Query key factory.
 * All hooks MUST use these — prevents key typos across the codebase
 * and makes targeted invalidation trivial.
 *
 * Pattern: resource.scope (all, list with params, detail with id)
 * Example: queryKeys.standards.list({ status: 'active', page: 1 })
 */

import type {
  UUID,
  StandardsListParams,
  CustomersListParams,
  CertificatesListParams,
  MatchesListParams,
  AssessmentsListParams,
  NotificationsListParams,
  EscalationsListParams,
  AuditListParams,
} from '@/lib/types'

export const queryKeys = {
  // ============ Standards ============
  standards: {
    all: ['standards'] as const,
    list: (params: StandardsListParams) => ['standards', 'list', params] as const,
    detail: (id: UUID) => ['standards', 'detail', id] as const,
  },

  // ============ Customers ============
  customers: {
    all: ['customers'] as const,
    list: (params: CustomersListParams) => ['customers', 'list', params] as const,
    detail: (id: UUID) => ['customers', 'detail', id] as const,
  },

  // ============ Certificates ============
  certificates: {
    all: ['certificates'] as const,
    list: (params: CertificatesListParams) => ['certificates', 'list', params] as const,
    detail: (id: UUID) => ['certificates', 'detail', id] as const,
  },

  // ============ Matches ============
  matches: {
    all: ['matches'] as const,
    list: (params: MatchesListParams) => ['matches', 'list', params] as const,
    detail: (id: UUID) => ['matches', 'detail', id] as const,
  },

  // ============ Assessments ============
  assessments: {
    all: ['assessments'] as const,
    list: (params: AssessmentsListParams) => ['assessments', 'list', params] as const,
    detail: (id: UUID) => ['assessments', 'detail', id] as const,
  },

  // ============ Notifications ============
  notifications: {
    all: ['notifications'] as const,
    list: (params: NotificationsListParams) => ['notifications', 'list', params] as const,
    detail: (id: UUID) => ['notifications', 'detail', id] as const,
  },

  // ============ Escalations ============
  escalations: {
    all: ['escalations'] as const,
    list: (params: EscalationsListParams) => ['escalations', 'list', params] as const,
    detail: (id: UUID) => ['escalations', 'detail', id] as const,
  },

  // ============ Audit ============
  audit: {
    all: ['audit'] as const,
    list: (params: AuditListParams) => ['audit', 'list', params] as const,
    detail: (id: UUID) => ['audit', 'detail', id] as const,
  },
} as const
