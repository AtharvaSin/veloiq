import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { format } from 'date-fns'
import { CheckCircle2, Replace, XCircle, Clock } from 'lucide-react'
import { DataTable, type DataTableColumn } from '@/components/shared/DataTable'
import { FilterBar, type FilterSpec } from '@/components/shared/FilterBar'
import { PaginationControls } from '@/components/shared/PaginationControls'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { KpiCard } from '@/components/shared/KpiCard'
import { Badge } from '@/components/ui/badge'
import { useStandardsList } from '@/hooks/useStandards'
import type { StandardRead, StandardsListParams } from '@/lib/types'

const FILTER_SPECS: FilterSpec[] = [
  {
    key: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'Active', value: 'active' },
      { label: 'Superseded', value: 'superseded' },
      { label: 'Withdrawn', value: 'withdrawn' },
    ],
  },
  {
    key: 'committee',
    label: 'Committee',
    type: 'text',
    placeholder: 'e.g. ISO/TC 176',
  },
  {
    key: 'base_number',
    label: 'Base number',
    type: 'text',
    placeholder: 'e.g. 9001',
  },
]

/** Format an ISO date string to a human-readable form, returning '—' for null/undefined. */
function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return format(new Date(iso), 'dd MMM yyyy')
  } catch {
    return iso
  }
}

/** Map a standard lifecycle status to a Badge variant. */
function badgeVariantFor(
  status: string,
): 'default' | 'secondary' | 'destructive' {
  if (status === 'active') return 'default'
  if (status === 'superseded') return 'secondary'
  return 'destructive'
}

export function IngestionMonitorPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState<number>(() => {
    const p = searchParams.get('page')
    return p ? Number.parseInt(p, 10) : 1
  })

  const filters: Record<string, string> = {
    status: searchParams.get('status') ?? '',
    committee: searchParams.get('committee') ?? '',
    base_number: searchParams.get('base_number') ?? '',
  }

  const params: StandardsListParams = {
    page,
    limit: 25,
    sort: 'ingested_at',
    order: 'desc',
    ...(filters.status && { status: filters.status }),
    ...(filters.committee && { committee: filters.committee }),
    ...(filters.base_number && { base_number: filters.base_number }),
  }

  const { data, isLoading, isError, refetch } = useStandardsList(params)

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
  const countByStatus = (status: string): number =>
    rows.filter((s) => s.status === status).length
  const latestIngestedIso = rows.reduce<string | null>(
    (latest, row) =>
      latest == null || new Date(row.ingested_at) > new Date(latest)
        ? row.ingested_at
        : latest,
    null,
  )
  const latestIngested = latestIngestedIso ? formatDate(latestIngestedIso) : '—'

  const columns: DataTableColumn<StandardRead>[] = [
    {
      key: 'ac_code',
      label: 'AC Code',
      className: 'font-mono text-sm text-accent font-semibold whitespace-nowrap',
    },
    {
      key: 'title',
      label: 'Title',
      className: 'text-primary font-medium max-w-md truncate',
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => (
        <Badge variant={badgeVariantFor(row.status)}>
          {row.status.toUpperCase()}
        </Badge>
      ),
    },
    {
      key: 'replaced_by',
      label: 'Replaced by',
      className: 'font-mono text-xs text-muted',
      render: (row) => row.replaced_by ?? '—',
    },
    {
      key: 'committee',
      label: 'Committee',
      className: 'text-secondary text-xs',
      render: (row) => row.committee ?? '—',
    },
    {
      key: 'version_year',
      label: 'Year',
      className: 'font-mono text-xs text-muted',
      render: (row) => (row.version_year != null ? String(row.version_year) : '—'),
    },
    {
      key: 'ingested_at',
      label: 'Ingested',
      className: 'font-mono text-xs text-muted whitespace-nowrap',
      render: (row) => formatDate(row.ingested_at),
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <p className="section-label">Standards catalog</p>
        <div className="flex items-center gap-3 mt-1">
          <h1 className="text-2xl font-bold text-primary">Ingestion Monitor</h1>
          {data && (
            <span className="inline-flex items-center rounded-tight bg-accent/10 px-2 py-0.5 font-mono text-xs font-semibold text-accent">
              {data.pagination.total} records
            </span>
          )}
        </div>
      </div>

      {data && (
        <section className="space-y-3">
          <p className="section-label">Catalog summary</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KpiCard
              label="Active"
              value={countByStatus('active')}
              icon={CheckCircle2}
              accent
            />
            <KpiCard
              label="Superseded"
              value={countByStatus('superseded')}
              icon={Replace}
            />
            <KpiCard
              label="Withdrawn"
              value={countByStatus('withdrawn')}
              icon={XCircle}
            />
            <KpiCard
              label="Latest ingested"
              value={latestIngested}
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
          message="Failed to load standards catalog"
          onRetry={() => refetch()}
        />
      )}
      {data && (
        <>
          <DataTable
            columns={columns}
            data={data.data}
            rowKey={(row) => row.id}
            emptyMessage="No standards match the current filters."
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
