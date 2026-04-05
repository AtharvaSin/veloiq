import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { format } from 'date-fns'
import {
  Send,
  MailCheck,
  Eye,
  MousePointerClick,
  AlertTriangle,
  Ban,
} from 'lucide-react'
import { DataTable, type DataTableColumn } from '@/components/shared/DataTable'
import { FilterBar, type FilterSpec } from '@/components/shared/FilterBar'
import { PaginationControls } from '@/components/shared/PaginationControls'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { KpiCard } from '@/components/shared/KpiCard'
import { useNotificationsList } from '@/hooks/useNotifications'
import type {
  NotificationRead,
  NotificationStatus,
  NotificationsListParams,
} from '@/lib/types'
import { cn } from '@/lib/utils'

const FILTER_SPECS: FilterSpec[] = [
  {
    key: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'Queued', value: 'queued' },
      { label: 'Sent', value: 'sent' },
      { label: 'Delivered', value: 'delivered' },
      { label: 'Opened', value: 'opened' },
      { label: 'Clicked', value: 'clicked' },
      { label: 'Bounced', value: 'bounced' },
      { label: 'Breached', value: 'breached' },
    ],
  },
  {
    key: 'customer_id',
    label: 'Customer ID (UUID)',
    type: 'text',
    placeholder: 'Paste customer UUID',
  },
]

const NOTIFICATION_STATUSES: NotificationStatus[] = [
  'queued',
  'sent',
  'delivered',
  'opened',
  'clicked',
  'bounced',
  'breached',
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

function isNotificationStatus(value: string): value is NotificationStatus {
  return (NOTIFICATION_STATUSES as string[]).includes(value)
}

export function NotificationCenterPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState<number>(() => {
    const p = searchParams.get('page')
    return p ? Number.parseInt(p, 10) : 1
  })

  const filters: Record<string, string> = {
    status: searchParams.get('status') ?? '',
    customer_id: searchParams.get('customer_id') ?? '',
  }

  const params: NotificationsListParams = {
    page,
    limit: 25,
    sort: 'sent_at',
    order: 'desc',
    ...(filters.status && isNotificationStatus(filters.status)
      ? { status: filters.status }
      : {}),
    ...(filters.customer_id && { customer_id: filters.customer_id }),
  }

  const { data, isLoading, isError, refetch } = useNotificationsList(params)

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
  const countByStatus = (status: NotificationStatus): number =>
    rows.filter((n) => n.status === status).length

  const columns: DataTableColumn<NotificationRead>[] = [
    {
      key: 'subject',
      label: 'Subject',
      className: 'text-primary max-w-md truncate',
    },
    {
      key: 'customer_id',
      label: 'Customer',
      className: 'font-mono text-xs text-muted',
      render: (row) => `${row.customer_id.slice(0, 8)}…`,
    },
    {
      key: 'template_language',
      label: 'Lang',
      className: 'font-mono text-xs text-muted uppercase',
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <StatusBadge status={row.status} variant="notification" />,
    },
    {
      key: 'sent_at',
      label: 'Sent',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatDate(row.sent_at),
    },
    {
      key: 'sla_deadline',
      label: 'SLA deadline',
      className: 'font-mono text-xs text-muted',
      render: (row) => (
        <span className={cn(row.status === 'breached' && 'text-danger')}>
          {formatDate(row.sla_deadline)}
        </span>
      ),
    },
    {
      key: 'delivered_at',
      label: 'Delivered',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatDate(row.delivered_at),
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <p className="section-label">Customer outreach</p>
        <div className="flex items-center gap-3 mt-1">
          <h1 className="text-2xl font-bold text-primary">Notification Center</h1>
          {data && (
            <span className="inline-flex items-center rounded-tight bg-accent/10 px-2 py-0.5 font-mono text-xs font-semibold text-accent">
              {data.pagination.total} records
            </span>
          )}
        </div>
      </div>

      {data && (
        <section className="space-y-3">
          <p className="section-label">Delivery funnel</p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <KpiCard label="Sent" value={countByStatus('sent')} icon={Send} />
            <KpiCard
              label="Delivered"
              value={countByStatus('delivered')}
              icon={MailCheck}
            />
            <KpiCard label="Opened" value={countByStatus('opened')} icon={Eye} />
            <KpiCard
              label="Clicked"
              value={countByStatus('clicked')}
              icon={MousePointerClick}
              accent
            />
            <KpiCard
              label="Bounced"
              value={countByStatus('bounced')}
              icon={Ban}
            />
            <KpiCard
              label="Breached"
              value={countByStatus('breached')}
              icon={AlertTriangle}
            />
          </div>
          <p className="text-xs text-muted">
            Funnel reflects current page ({data.data.length} records) ·{' '}
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
          message="Failed to load notifications"
          onRetry={() => refetch()}
        />
      )}
      {data && (
        <>
          <DataTable
            columns={columns}
            data={data.data}
            rowKey={(row) => row.id}
            emptyMessage="No notifications match the current filters."
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
