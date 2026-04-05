import { useParams, Link } from 'react-router-dom'
import { format } from 'date-fns'
import {
  ArrowLeft,
  ChevronRight,
  Mail,
  Building2,
  MapPin,
  Globe,
  FileCheck,
  AlertTriangle,
} from 'lucide-react'
import { DataTable, type DataTableColumn } from '@/components/shared/DataTable'
import { KpiCard } from '@/components/shared/KpiCard'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { EmptyState } from '@/components/shared/EmptyState'
import { useCustomerDetail } from '@/hooks/useCustomers'
import { useCertificatesList } from '@/hooks/useCertificates'
import { useEscalationsList } from '@/hooks/useEscalations'
import { useNotificationsList } from '@/hooks/useNotifications'
import type { CertificateRead } from '@/lib/types'
import { ROUTES } from '@/lib/routes'

/** Format an ISO date string to a human-readable form, returning '—' for null/undefined. */
function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return format(new Date(iso), 'dd MMM yyyy')
  } catch {
    return iso
  }
}

export function Customer360Page() {
  const { id } = useParams<{ id: string }>()

  const customerQ = useCustomerDetail(id ?? '', { enabled: Boolean(id) })
  const certsQ = useCertificatesList(
    id ? { customer_id: id, limit: 100 } : { limit: 1 },
  )
  const escalationsQ = useEscalationsList(
    id ? { customer_id: id, limit: 100 } : { limit: 1 },
  )
  const notifsQ = useNotificationsList(
    id ? { customer_id: id, limit: 100 } : { limit: 1 },
  )

  if (customerQ.isLoading) return <LoadingState rows={10} />
  if (customerQ.isError || !customerQ.data) {
    return (
      <ErrorState
        message="Failed to load customer"
        hint={id ? `Customer ID: ${id}` : 'No ID provided'}
        onRetry={() => customerQ.refetch()}
      />
    )
  }

  const customer = customerQ.data
  const certs = certsQ.data?.data ?? []
  const escalations = escalationsQ.data?.data ?? []
  const notifs = notifsQ.data?.data ?? []

  const activeCerts = certs.filter((c) => c.status === 'active').length
  const expiringCerts = certs.filter((c) => c.status === 'expiring').length
  const openEscalations = escalations.filter((e) => e.status !== 'resolved').length
  const pendingNotifs = notifs.filter((n) => n.status !== 'clicked').length

  const certColumns: DataTableColumn<CertificateRead>[] = [
    {
      key: 'certificate_number',
      label: 'Cert #',
      className: 'font-mono text-xs text-accent',
    },
    {
      key: 'product_description',
      label: 'Product',
      className: 'text-primary',
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <StatusBadge status={row.status} variant="certificate" />,
    },
    {
      key: 'issue_date',
      label: 'Issued',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatDate(row.issue_date),
    },
    {
      key: 'expiry_date',
      label: 'Expires',
      className: 'font-mono text-xs text-muted',
      render: (row) => formatDate(row.expiry_date),
    },
  ]

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <Link
          to={ROUTES.CUSTOMERS}
          className="text-secondary hover:text-primary inline-flex items-center gap-1"
        >
          <ArrowLeft className="h-3 w-3" />
          Customers
        </Link>
        <ChevronRight className="h-3 w-3 text-muted" />
        <span className="font-mono text-secondary">{customer.customer_number}</span>
      </div>

      {/* Header */}
      <div className="space-y-3">
        <p className="section-label">Customer 360</p>
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-full bg-elevated flex items-center justify-center border border-divider">
              <Building2 className="h-6 w-6 text-accent" strokeWidth={2} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-primary">{customer.company_name}</h1>
              <p className="mt-1 font-mono text-xs text-muted">{customer.customer_number}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Info grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-surface border border-divider rounded p-4">
          <div className="flex items-center gap-2 text-muted">
            <MapPin className="h-4 w-4" />
            <span className="section-label">Country</span>
          </div>
          <p className="mt-2 font-mono text-lg text-primary">{customer.country}</p>
        </div>
        <div className="bg-surface border border-divider rounded p-4">
          <div className="flex items-center gap-2 text-muted">
            <Globe className="h-4 w-4" />
            <span className="section-label">Sales area</span>
          </div>
          <p className="mt-2 text-sm font-medium text-primary">{customer.sales_area}</p>
        </div>
        <div className="bg-surface border border-divider rounded p-4">
          <span className="section-label">Language</span>
          <p className="mt-2 font-mono text-lg text-primary">{customer.language}</p>
        </div>
        <div className="bg-surface border border-divider rounded p-4">
          <div className="flex items-center gap-2 text-muted">
            <Mail className="h-4 w-4" />
            <span className="section-label">Contact</span>
          </div>
          <p className="mt-2 text-sm text-primary truncate">{customer.contact_name ?? '—'}</p>
          <p className="text-xs font-mono text-muted truncate">
            {customer.contact_email ?? '—'}
          </p>
        </div>
      </div>

      {/* KPI row */}
      <section className="space-y-3">
        <p className="section-label">Portfolio summary</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <KpiCard label="Active certificates" value={activeCerts} icon={FileCheck} accent />
          <KpiCard label="Expiring soon" value={expiringCerts} icon={AlertTriangle} />
          <KpiCard label="Open escalations" value={openEscalations} />
          <KpiCard label="Active notifications" value={pendingNotifs} />
        </div>
      </section>

      {/* Certificate portfolio */}
      <section className="space-y-3">
        <p className="section-label">Certificate portfolio</p>
        {certsQ.isLoading ? (
          <LoadingState rows={3} />
        ) : certs.length === 0 ? (
          <EmptyState message="No certificates on file for this customer." />
        ) : (
          <DataTable
            columns={certColumns}
            data={certs}
            rowKey={(row) => row.id}
          />
        )}
      </section>

      {/* Active escalations (if any) */}
      {escalations.filter((e) => e.status !== 'resolved').length > 0 && (
        <section className="space-y-3">
          <p className="section-label">Open escalations</p>
          <div className="space-y-2">
            {escalations
              .filter((e) => e.status !== 'resolved')
              .map((esc) => (
                <div
                  key={esc.id}
                  className="bg-surface border border-warn/30 border-l-2 border-l-warn rounded p-4 flex items-center justify-between gap-4"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-primary">
                      {esc.escalation_reason.replace(/_/g, ' ')}
                    </p>
                    <p className="text-xs text-muted mt-1">
                      Assigned to {esc.assigned_to ?? 'unassigned'} · Created{' '}
                      {formatDate(esc.created_at)}
                    </p>
                  </div>
                  <StatusBadge status={esc.status} variant="escalation" />
                  <p className="font-mono text-sm text-primary">
                    {Number(esc.opportunity_value).toLocaleString('en-US', {
                      style: 'currency',
                      currency: 'USD',
                      maximumFractionDigits: 0,
                    })}
                  </p>
                </div>
              ))}
          </div>
        </section>
      )}
    </div>
  )
}
