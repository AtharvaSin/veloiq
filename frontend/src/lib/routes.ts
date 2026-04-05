/**
 * Centralized route path constants.
 * Use these instead of hardcoded strings in NavLink / navigate() calls.
 */
export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/',
  QUEUE: '/queue',
  ASSESSMENT: (id: string) => `/assessments/${id}`,
  ASSESSMENT_PATTERN: '/assessments/:id',
  MATCH: (id: string) => `/matches/${id}`,
  MATCH_PATTERN: '/matches/:id',
} as const

export type RouteKey = keyof typeof ROUTES
