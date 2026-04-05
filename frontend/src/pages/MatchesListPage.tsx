import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { format } from 'date-fns'
import { Zap, Eye, AlertOctagon, Clock } from 'lucide-react'
import { DataTable, type DataTableColumn } from '@/components/shared/DataTable'
import { FilterBar, type FilterSpec } from '@/components/shared/FilterBar'
import { PaginationControls } from '@/components/shared/PaginationControls'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { KpiCard } from '@/components/shared/KpiCard'
import { ConfidencePillFromString } from '@/components/shared/ConfidencePill'
import { useMatchesList } from '@/hooks/useMatches'
import { ROUTES } from '@/lib/routes'
import type {
  ConfidenceTier,
  MatchResultRead,
  MatchStatus,
  MatchesListParams,
} from '@/lib/types'

const FILTER_SPECS: FilterSpec[] = [
  {
    key: 'confidence_tier',
    label: 'Confidence tier',
    type: 'select',
    options: [
      { label: 'Auto match', value: 'auto_match' },
      { label: 'Expert review', value: 'expert_review' },
      { label: 'Manual triage', value: 'manual_triage' },
    ],
  },
  {
    key: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'Pending', value: 'pending' },
      { label: 'Reviewed', value: 'reviewed' },
    ],
  },
]

const CONFIDENCE_TIERS: ConfidenceTier[] = [
  'auto_match',
  'expert_review',
  'manual_triage',
]
const MATCH_STATUSES: MatchStatus[] = ['pending', 'reviewed']

function isConfidenceTier(value: string): value is ConfidenceTier {
  return (CONFIDENCE_TIERS as string[]).includes(value)
}

function isMatchStatus(value: string): value is MatchStatus {
  return (MATCH_STATUSES as string[]).includes(value)
}

/** Format a DecimalStr score to 3 decimals, or '—' if missing/invalid. */
function formatScore(score: string | null | undefined): string {
  if (!score) return '—'
  const n = Number.parseFloat(score)
  return Number.isNaN(n) ? '—' : n.toFixed(3)
}

/** Format an ISO date string to a human-readable form, returning '—' for null/undefined. */
function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return format(new Date(iso), 'dd MMM yyyy')
  } catch {
    return iso
  }
}

export function MatchesListPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState<number>(() => {
    const p = searchParams.get('page')
    return p ? Number.parseInt(p, 10) : 1
  })

  const filters: Record<string, string> = {
    confidence_tier: searchParams.get('confidence_tier') ?? '',
    status: searchParams.get('status') ?? '',
  }

  const params: MatchesListParams = {
    page,
    limit: 25,
    sort: 'matched_at',
    order: 'desc',
    ...(filters.confidence_tier && isConfidenceTier(filters.confidence_tier)
      ? { confidence_tier: filters.confidence_tier }
      : {}),
    ...(filters.status && isMatchStatus(filters.status)
      ? { status: filters.status }
      : {}),
  }

  const { data, isLoading, isError, refetch } = useMatchesList(params)

  function handleFilterChange(key: string, value: string): void {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    next.set('page', '1')
    setSearchParams(next)
    setPage(1)
  }

  function handleReset(): void {
    setSearchParams(new URLSearchParams())
    setPage(1)
  }

  function handlePageChange(nextPage: number): void {
    const next = new URLSearchParams(searchParams)
    next.set('page', String(nextPage))
    setSearchParams(next)
    setPage(nextPage)
  }

  const rows = data?.data ?? []
  const countByTier = (tier: ConfidenceTier): number =>
    rows.filter((m) => m.confidence_tier === tier).length
  const countByStatus = (status: MatchStatus): number =>
    rows.filter((m) => m.status === status).length

  const columns: DataTableColumn<MatchResultRead>[] = [
    {
      key: 'similarity_score',
      label: 'Composite',
      render: (row) => <ConfidencePillFromString score={row.similarity_score} />,
    },
    {
      key: 'levenshtein_score',
      label: 'Levenshtein',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatScore(row.levenshtein_score),
    },
    {
      key: 'jaro_winkler_score',
      label: 'Jaro-Winkler',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatScore(row.jaro_winkler_score),
    },
    {
      key: 'token_set_score',
      label: 'Token set',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatScore(row.token_set_score),
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <StatusBadge status={row.status} variant="match" />,
    },
    {
      key: 'matched_at',
      label: 'Matched',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatDate(row.matched_at),
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <p className="section-label">Fuzzy match triage</p>
        <div className="flex items-center gap-3 mt-1">
          <h1 className="text-2xl font-bold text-primary">Match Queue</h1>
          {data && (
            <span className="inline-flex items-center rounded-tight bg-accent/10 px-2 py-0.5 font-mono text-xs font-semibold text-accent">
              {data.pagination.total} records
            </span>
          )}
        </div>
      </div>

      {data && (
        <section className="space-y-3">
          <p className="section-label">Confidence distribution</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KpiCard
              label="Auto match"
              value={countByTier('auto_match')}
              icon={Zap}
              accent
            />
            <KpiCard
              label="Expert review"
              value={countByTier('expert_review')}
              icon={Eye}
            />
            <KpiCard
              label="Manual triage"
              value={countByTier('manual_triage')}
              icon={AlertOctagon}
            />
            <KpiCard
              label="Pending"
              value={countByStatus('pending')}
              icon={Clock}
            />
          </div>
          <p className="text-xs text-muted">
            Metrics reflect current page ({data.data.length} records) ·{' '}
            {data.pagination.total} total
          </p>
        </section>
      )}

      <FilterBar
        filters={FILTER_SPECS}
        values={filters}
        onChange={handleFilterChange}
        onReset={handleReset}
      />

      {isLoading && <LoadingState rows={8} />}
      {isError && (
        <ErrorState
          message="Failed to load matches"
          onRetry={() => refetch()}
        />
      )}
      {data && (
        <>
          <DataTable
            columns={columns}
            data={data.data}
            rowKey={(row) => row.id}
            onRowClick={(row) => navigate(ROUTES.MATCH(row.id))}
            emptyMessage="No matches match the current filters."
          />
          <PaginationControls
            pagination={data.pagination}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  )
}
