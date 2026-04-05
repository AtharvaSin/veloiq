import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { format } from 'date-fns'
import { AlertCircle, PhoneCall, CheckCircle2, DollarSign } from 'lucide-react'
import { DataTable, type DataTableColumn } from '@/components/shared/DataTable'
import { FilterBar, type FilterSpec } from '@/components/shared/FilterBar'
import { PaginationControls } from '@/components/shared/PaginationControls'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { KpiCard } from '@/components/shared/KpiCard'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useEscalationsList, useUpdateEscalation } from '@/hooks/useEscalations'
import { useToast } from '@/hooks/use-toast'
import type {
  EscalationsListParams,
  EscalationStatus,
  SalesEscalationRead,
} from '@/lib/types'

const FILTER_SPECS: FilterSpec[] = [
  {
    key: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'Open', value: 'open' },
      { label: 'Contacted', value: 'contacted' },
      { label: 'Resolved', value: 'resolved' },
    ],
  },
  {
    key: 'assigned_to',
    label: 'Assignee',
    type: 'text',
    placeholder: 'Assignee user ID',
  },
  {
    key: 'customer_id',
    label: 'Customer ID (UUID)',
    type: 'text',
    placeholder: 'Paste customer UUID',
  },
]

const ESCALATION_STATUSES: EscalationStatus[] = ['open', 'contacted', 'resolved']

/** Format an ISO date string to a human-readable form, returning '—' for null/undefined. */
function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return format(new Date(iso), 'dd MMM yyyy')
  } catch {
    return iso
  }
}

/** Format a decimal string as USD currency with no decimal digits. */
function formatCurrency(value: string | number): string {
  return Number(value).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  })
}

function isEscalationStatus(value: string): value is EscalationStatus {
  return (ESCALATION_STATUSES as string[]).includes(value)
}

interface ManageDialogProps {
  escalation: SalesEscalationRead
  onClose: () => void
}

/**
 * Subcomponent that owns its own form state so values reset cleanly per row
 * when mounted with `key={escalation.id}`.
 */
function SalesPipelineManageDialog({ escalation, onClose }: ManageDialogProps) {
  const { toast } = useToast()
  const updateMutation = useUpdateEscalation()
  const [status, setStatus] = useState<EscalationStatus>(escalation.status)
  const [assignee, setAssignee] = useState<string>(escalation.assigned_to ?? '')

  function handleSave(): void {
    updateMutation.mutate(
      {
        id: escalation.id,
        input: { status, assigned_to: assignee || null },
      },
      {
        onSuccess: () => {
          toast({
            title: 'Escalation updated',
            description: `Status set to ${status}`,
          })
          onClose()
        },
        onError: (err) => {
          toast({
            title: 'Update failed',
            description: err.message,
            variant: 'destructive',
          })
        },
      },
    )
  }

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Manage escalation</DialogTitle>
          <DialogDescription>
            {escalation.escalation_reason.replace(/_/g, ' ')} ·{' '}
            {escalation.customer_id.slice(0, 8)}…
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="escalation-status"
              className="text-xs text-muted uppercase tracking-label"
            >
              Status
            </label>
            <Select
              value={status}
              onValueChange={(v) => {
                if (isEscalationStatus(v)) setStatus(v)
              }}
            >
              <SelectTrigger id="escalation-status" className="bg-obsidian">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="contacted">Contacted</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="escalation-assignee"
              className="text-xs text-muted uppercase tracking-label"
            >
              Assigned to
            </label>
            <Input
              id="escalation-assignee"
              type="text"
              value={assignee}
              onChange={(e) => setAssignee(e.target.value)}
              placeholder="Assignee user ID"
              className="bg-obsidian"
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={updateMutation.isPending}>
            {updateMutation.isPending ? 'Saving…' : 'Save'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export function SalesPipelinePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState<number>(() => {
    const p = searchParams.get('page')
    return p ? Number.parseInt(p, 10) : 1
  })
  const [selected, setSelected] = useState<SalesEscalationRead | null>(null)

  const filters: Record<string, string> = {
    status: searchParams.get('status') ?? '',
    assigned_to: searchParams.get('assigned_to') ?? '',
    customer_id: searchParams.get('customer_id') ?? '',
  }

  const params: EscalationsListParams = {
    page,
    limit: 25,
    sort: 'created_at',
    order: 'desc',
    ...(filters.status && isEscalationStatus(filters.status)
      ? { status: filters.status }
      : {}),
    ...(filters.assigned_to && { assigned_to: filters.assigned_to }),
    ...(filters.customer_id && { customer_id: filters.customer_id }),
  }

  const { data, isLoading, isError, refetch } = useEscalationsList(params)

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
  const countByStatus = (status: EscalationStatus): number =>
    rows.filter((e) => e.status === status).length
  const totalOpportunity = rows
    .filter((e) => e.status === 'open' || e.status === 'contacted')
    .reduce((sum, e) => sum + Number(e.opportunity_value), 0)

  const columns: DataTableColumn<SalesEscalationRead>[] = [
    {
      key: 'escalation_reason',
      label: 'Reason',
      className: 'text-primary font-medium',
      render: (row) => row.escalation_reason.replace(/_/g, ' '),
    },
    {
      key: 'customer_id',
      label: 'Customer',
      className: 'font-mono text-xs text-muted',
      render: (row) => `${row.customer_id.slice(0, 8)}…`,
    },
    {
      key: 'opportunity_value',
      label: 'Opportunity',
      className: 'font-mono text-primary',
      render: (row) => formatCurrency(row.opportunity_value),
    },
    {
      key: 'assigned_to',
      label: 'Assigned to',
      className: 'text-secondary',
      render: (row) => row.assigned_to ?? '—',
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <StatusBadge status={row.status} variant="escalation" />,
    },
    {
      key: 'created_at',
      label: 'Created',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatDate(row.created_at),
    },
    {
      key: 'actions',
      label: '',
      render: (row) => (
        <Button
          size="sm"
          variant="outline"
          onClick={(e) => {
            e.stopPropagation()
            setSelected(row)
          }}
        >
          Manage
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <p className="section-label">Sales revenue at risk</p>
        <div className="flex items-center gap-3 mt-1">
          <h1 className="text-2xl font-bold text-primary">Sales Pipeline</h1>
          {data && (
            <span className="inline-flex items-center rounded-tight bg-accent/10 px-2 py-0.5 font-mono text-xs font-semibold text-accent">
              {data.pagination.total} records
            </span>
          )}
        </div>
      </div>

      {data && (
        <section className="space-y-3">
          <p className="section-label">Pipeline summary</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KpiCard
              label="Open"
              value={countByStatus('open')}
              icon={AlertCircle}
              accent
            />
            <KpiCard
              label="Contacted"
              value={countByStatus('contacted')}
              icon={PhoneCall}
            />
            <KpiCard
              label="Resolved"
              value={countByStatus('resolved')}
              icon={CheckCircle2}
            />
            <KpiCard
              label="Total opportunity"
              value={formatCurrency(totalOpportunity)}
              icon={DollarSign}
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
          message="Failed to load escalations"
          onRetry={() => refetch()}
        />
      )}
      {data && (
        <>
          <DataTable
            columns={columns}
            data={data.data}
            rowKey={(row) => row.id}
            onRowClick={(row) => setSelected(row)}
            emptyMessage="No escalations match the current filters."
          />
          <PaginationControls
            pagination={data.pagination}
            onPageChange={handlePageChange}
          />
        </>
      )}

      {selected && (
        <SalesPipelineManageDialog
          key={selected.id}
          escalation={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  )
}
