import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { format } from 'date-fns'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { DataTable, type DataTableColumn } from '@/components/shared/DataTable'
import { FilterBar, type FilterSpec } from '@/components/shared/FilterBar'
import { PaginationControls } from '@/components/shared/PaginationControls'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useAuditList } from '@/hooks/useAudit'
import type { AuditListParams, AuditLogRead } from '@/lib/types'

const FILTER_SPECS: FilterSpec[] = [
  {
    key: 'entity_type',
    label: 'Entity type',
    type: 'select',
    options: [
      { label: 'Certificate', value: 'certificate' },
      { label: 'Customer', value: 'customer' },
      { label: 'Assessment', value: 'assessment' },
      { label: 'Escalation', value: 'escalation' },
      { label: 'Standard', value: 'standard' },
      { label: 'Notification', value: 'notification' },
      { label: 'Match result', value: 'match_result' },
    ],
  },
  {
    key: 'action',
    label: 'Action',
    type: 'select',
    options: [
      { label: 'Created', value: 'created' },
      { label: 'Updated', value: 'updated' },
      { label: 'Deleted', value: 'deleted' },
      { label: 'Assessed', value: 'assessed' },
      { label: 'Notified', value: 'notified' },
      { label: 'Escalated', value: 'escalated' },
    ],
  },
  {
    key: 'actor',
    label: 'Actor',
    type: 'text',
    placeholder: 'Actor user ID',
  },
  {
    key: 'entity_id',
    label: 'Entity ID',
    type: 'text',
    placeholder: 'Entity UUID',
  },
]

/** Format an ISO date string with time, returning '—' for null/undefined. */
function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return format(new Date(iso), 'dd MMM yyyy HH:mm')
  } catch {
    return iso
  }
}

export function AuditTrailPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState<number>(() => {
    const p = searchParams.get('page')
    return p ? Number.parseInt(p, 10) : 1
  })
  const [selected, setSelected] = useState<AuditLogRead | null>(null)

  const filters: Record<string, string> = {
    entity_type: searchParams.get('entity_type') ?? '',
    action: searchParams.get('action') ?? '',
    actor: searchParams.get('actor') ?? '',
    entity_id: searchParams.get('entity_id') ?? '',
  }

  const params: AuditListParams = {
    page,
    limit: 25,
    sort: 'created_at',
    order: 'desc',
    ...(filters.entity_type && { entity_type: filters.entity_type }),
    ...(filters.action && { action: filters.action }),
    ...(filters.actor && { actor: filters.actor }),
    ...(filters.entity_id && { entity_id: filters.entity_id }),
  }

  const { data, isLoading, isError, refetch } = useAuditList(params)

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

  const columns: DataTableColumn<AuditLogRead>[] = [
    {
      key: 'created_at',
      label: 'Timestamp',
      className: 'font-mono text-xs text-muted whitespace-nowrap',
      render: (row) => formatDateTime(row.created_at),
    },
    {
      key: 'action',
      label: 'Action',
      render: (row) => (
        <Badge variant="outline" className="uppercase">
          {row.action}
        </Badge>
      ),
    },
    {
      key: 'entity_type',
      label: 'Entity',
      className: 'text-secondary uppercase tracking-wide text-xs',
    },
    {
      key: 'entity_id',
      label: 'Entity ID',
      className: 'font-mono text-xs text-accent',
      render: (row) => `${row.entity_id.slice(0, 8)}…`,
    },
    {
      key: 'actor',
      label: 'Actor',
      className: 'font-mono text-xs text-secondary',
    },
    {
      key: 'details',
      label: 'Details',
      render: () => (
        <button
          type="button"
          className="text-xs text-accent hover:underline"
          onClick={(e) => e.stopPropagation()}
        >
          View details
        </button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <p className="section-label">Immutable audit trail</p>
        <div className="flex items-center gap-3 mt-1">
          <h1 className="text-2xl font-bold text-primary">Audit Log</h1>
          {data && (
            <span className="inline-flex items-center rounded-tight bg-accent/10 px-2 py-0.5 font-mono text-xs font-semibold text-accent">
              {data.pagination.total} records
            </span>
          )}
        </div>
      </div>

      <FilterBar
        filters={FILTER_SPECS}
        values={filters}
        onChange={handleFilterChange}
        onReset={handleReset}
      />

      {isLoading && <LoadingState rows={8} />}
      {isError && (
        <ErrorState message="Failed to load audit log" onRetry={() => refetch()} />
      )}
      {data && (
        <>
          <DataTable
            columns={columns}
            data={data.data}
            rowKey={(row) => row.id}
            onRowClick={(row) => setSelected(row)}
            emptyMessage="No audit entries match the current filters."
          />
          <PaginationControls
            pagination={data.pagination}
            onPageChange={handlePageChange}
          />
        </>
      )}

      <Dialog
        open={!!selected}
        onOpenChange={(o) => {
          if (!o) setSelected(null)
        }}
      >
        <DialogContent className="max-w-2xl bg-surface border-divider">
          {selected && (
            <>
              <DialogHeader>
                <DialogTitle className="text-primary">
                  Audit entry · {selected.action}
                </DialogTitle>
                <DialogDescription className="font-mono text-xs text-muted">
                  {selected.entity_type} · {selected.entity_id}
                </DialogDescription>
              </DialogHeader>
              <div className="grid grid-cols-3 gap-3 border-y border-divider py-3">
                <div>
                  <p className="section-label">Actor</p>
                  <p className="mt-1 font-mono text-xs text-secondary">
                    {selected.actor}
                  </p>
                </div>
                <div>
                  <p className="section-label">Created at</p>
                  <p className="mt-1 font-mono text-xs text-secondary">
                    {formatDateTime(selected.created_at)}
                  </p>
                </div>
                <div>
                  <p className="section-label">IP address</p>
                  <p className="mt-1 font-mono text-xs text-secondary">
                    {selected.ip_address ?? '—'}
                  </p>
                </div>
              </div>
              <pre className="bg-obsidian border border-divider rounded p-4 text-xs font-mono text-secondary overflow-auto max-h-[60vh]">
                {JSON.stringify(selected.details, null, 2)}
              </pre>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
