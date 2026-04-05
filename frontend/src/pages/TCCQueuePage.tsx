import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { format } from 'date-fns'
import { Badge } from '@/components/ui/badge'
import { DataTable, type DataTableColumn } from '@/components/shared/DataTable'
import { FilterBar, type FilterSpec } from '@/components/shared/FilterBar'
import { PaginationControls } from '@/components/shared/PaginationControls'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useAssessmentsList } from '@/hooks/useAssessments'
import type { AssessmentRead, AssessmentsListParams } from '@/lib/types'
import { ROUTES } from '@/lib/routes'

const FILTER_SPECS: FilterSpec[] = [
  {
    key: 'impact_classification',
    label: 'Impact',
    type: 'select',
    options: [
      { label: 'No change', value: 'no_change' },
      { label: 'Administrative', value: 'administrative' },
      { label: 'Minor technical', value: 'minor_technical' },
      { label: 'Major technical', value: 'major_technical' },
      { label: 'Safety critical', value: 'safety_critical' },
    ],
  },
  {
    key: 'decision',
    label: 'Decision',
    type: 'select',
    options: [
      { label: 'Approved', value: 'approved' },
      { label: 'Rejected', value: 'rejected' },
      { label: 'Escalated', value: 'escalated' },
    ],
  },
  {
    key: 'assessor_id',
    label: 'Assessor',
    type: 'text',
    placeholder: 'Dr. M. Weber',
  },
]

function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return format(new Date(iso), 'dd MMM yyyy · HH:mm')
  } catch {
    return iso
  }
}

function impactTone(impact: string): 'default' | 'secondary' | 'destructive' {
  switch (impact) {
    case 'safety_critical':
      return 'destructive'
    case 'major_technical':
      return 'default'
    default:
      return 'secondary'
  }
}

export function TCCQueuePage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState(() => {
    const p = searchParams.get('page')
    return p ? Number.parseInt(p, 10) : 1
  })

  const filters: Record<string, string> = {
    impact_classification: searchParams.get('impact_classification') ?? '',
    decision: searchParams.get('decision') ?? '',
    assessor_id: searchParams.get('assessor_id') ?? '',
  }

  const params: AssessmentsListParams = {
    page,
    limit: 25,
    sort: 'decided_at',
    order: 'desc',
    ...(filters.impact_classification && {
      impact_classification: filters.impact_classification as 'no_change' | 'administrative' | 'minor_technical' | 'major_technical' | 'safety_critical',
    }),
    ...(filters.decision && { decision: filters.decision as 'approved' | 'rejected' | 'escalated' }),
    ...(filters.assessor_id && { assessor_id: filters.assessor_id }),
  }

  const { data, isLoading, isError, refetch } = useAssessmentsList(params)

  function handleFilterChange(key: string, value: string) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    next.set('page', '1')
    setSearchParams(next)
    setPage(1)
  }

  function handleReset() {
    setSearchParams(new URLSearchParams())
    setPage(1)
  }

  function handlePageChange(nextPage: number) {
    const next = new URLSearchParams(searchParams)
    next.set('page', String(nextPage))
    setSearchParams(next)
    setPage(nextPage)
  }

  const columns: DataTableColumn<AssessmentRead>[] = [
    {
      key: 'assessor_id',
      label: 'Assessor',
      className: 'font-medium text-primary',
    },
    {
      key: 'impact_classification',
      label: 'Impact',
      render: (row) => (
        <Badge variant={impactTone(row.impact_classification)}>
          {row.impact_classification.replace(/_/g, ' ')}
        </Badge>
      ),
    },
    {
      key: 'action_required',
      label: 'Action',
      className: 'text-secondary capitalize',
      render: (row) => row.action_required.replace(/_/g, ' '),
    },
    {
      key: 'decision',
      label: 'Decision',
      render: (row) => (
        <StatusBadge status={row.decision} variant="default" />
      ),
    },
    {
      key: 'reason_code',
      label: 'Reason',
      className: 'font-mono text-xs text-muted',
    },
    {
      key: 'decided_at',
      label: 'Decided at',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatDateTime(row.decided_at),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div>
          <p className="section-label">Work queue</p>
          <div className="flex items-center gap-3 mt-1">
            <h1 className="text-2xl font-bold text-primary">TCC Assessments</h1>
            {data && (
              <span className="inline-flex items-center rounded-tight bg-accent/10 px-2 py-0.5 font-mono text-xs font-semibold text-accent">
                {data.pagination.total} records
              </span>
            )}
          </div>
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
        <ErrorState
          message="Failed to load assessments"
          hint="Check backend connectivity"
          onRetry={() => refetch()}
        />
      )}
      {data && (
        <>
          <DataTable
            columns={columns}
            data={data.data}
            rowKey={(row) => row.id}
            onRowClick={(row) => navigate(ROUTES.ASSESSMENT(row.id))}
            emptyMessage="No assessments match the current filters."
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
