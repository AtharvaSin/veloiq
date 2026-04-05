/**
 * Mock auth session for POC demo mode.
 * Stores the "acting user" identity in localStorage.
 * Production replaces this with real OAuth/JWT session.
 *
 * This module is used by the API interceptor (api.ts) to attach
 * X-User-Id headers to all requests for audit trail purposes.
 */

const STORAGE_KEY = 'veloiq.demo.actor'

/**
 * Get the current demo actor (user ID).
 * Returns from localStorage, or fallback to env var, or "anonymous".
 */
export function getActor(): string {
  if (typeof window === 'undefined') return 'anonymous'
  const stored = window.localStorage.getItem(STORAGE_KEY)
  if (stored) return stored
  const fallback = import.meta.env.VITE_DEMO_ACTOR
  return typeof fallback === 'string' && fallback.length > 0 ? fallback : 'anonymous'
}

/**
 * Set the demo actor (user ID) in localStorage.
 * Used during login flow to persist actor identity across page reloads.
 */
export function setActor(name: string): void {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(STORAGE_KEY, name)
}

/**
 * Clear the demo session (logout).
 * Removes the stored actor from localStorage.
 */
export function clearSession(): void {
  if (typeof window === 'undefined') return
  window.localStorage.removeItem(STORAGE_KEY)
}

/**
 * Check if a demo session is active.
 * Returns true if actor is stored in localStorage (not anonymous fallback).
 */
export function hasSession(): boolean {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(STORAGE_KEY) !== null
}
