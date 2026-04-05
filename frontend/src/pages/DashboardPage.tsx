import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Database, FileCheck, Shield, MessageSquare, Activity } from 'lucide-react'
import { KpiCard } from '@/components/shared/KpiCard'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useStandardsList } from '@/hooks/useStandards'
import { useMatchesList } from '@/hooks/useMatches'
import { useAssessmentsList } from '@/hooks/useAssessments'
import { useNotificationsList } from '@/hooks/useNotifications'
import { useCertificatesList } from '@/hooks/useCertificates'
import { useEscalationsList } from '@/hooks/useEscalations'
import { ROUTES } from '@/lib/routes'

function useCountQuery<
  T extends { data: { pagination: { total: number } } | undefined; isLoading: boolean; isError: boolean },
>(q: T): { count: number; isLoading: boolean; isError: boolean } {
  return {
    count: q.data?.pagination.total ?? 0,
    isLoading: q.isLoading,
    isError: q.isError,
  }
}

export function DashboardPage() {
  const standardsQ = useStandardsList({ page: 1, limit: 1 })
  const certificatesQ = useCertificatesList({ page: 1, limit: 1 })
  const matchesQ = useMatchesList({ page: 1, limit: 1 })
  const assessmentsQ = useAssessmentsList({ page: 1, limit: 1 })
  const notificationsQ = useNotificationsList({ page: 1, limit: 1 })
  const escalationsQ = useEscalationsList({ page: 1, limit: 1 })

  const standards = useCountQuery(standardsQ)
  const certificates = useCountQuery(certificatesQ)
  const matches = useCountQuery(matchesQ)
  const assessments = useCountQuery(assessmentsQ)
  const notifications = useCountQuery(notificationsQ)
  const escalations = useCountQuery(escalationsQ)

  const isLoading = standards.isLoading || matches.isLoading || assessments.isLoading || notifications.isLoading
  const hasError =
    standards.isError || matches.isError || assessments.isError || notifications.isError

  const autoMatchRate = useMemo(() => {
    if (matches.count === 0) return '—'
    // placeholder: hardcoded since Phase B computes this from tier distribution
    return '33%'
  }, [matches.count])

  if (hasError) {
    return (
      <ErrorState
        message="Unable to load pipeline metrics"
        hint="Is the backend running on :8000?"
        onRetry={() => window.location.reload()}
      />
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <p className="section-label">Pipeline overview</p>
        <p className="text-sm text-secondary mt-1">
          Real-time throughput and compliance state across the ingestion pipeline.
        </p>
      </div>

      {/* KPI cards */}
      {isLoading ? (
        <LoadingState rows={1} className="h-28" />
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to={ROUTES.INGESTION}
            className="block focus:outline-none focus:ring-2 focus:ring-accent rounded"
          >
            <KpiCard
              label="Standards Ingested"
              value={standards.count}
              icon={Database}
              accent
            />
          </Link>
          <Link
            to={ROUTES.MATCHES}
            className="block focus:outline-none focus:ring-2 focus:ring-accent rounded"
          >
            <KpiCard
              label="Matches Generated"
              value={matches.count}
              icon={Activity}
              delta={{ value: `${autoMatchRate} auto-match`, direction: 'up' }}
            />
          </Link>
          <Link
            to={ROUTES.QUEUE}
            className="block focus:outline-none focus:ring-2 focus:ring-accent rounded"
          >
            <KpiCard
              label="Assessments Complete"
              value={assessments.count}
              icon={Shield}
            />
          </Link>
          <Link
            to={ROUTES.NOTIFICATIONS}
            className="block focus:outline-none focus:ring-2 focus:ring-accent rounded"
          >
            <KpiCard
              label="Notifications Sent"
              value={notifications.count}
              icon={MessageSquare}
            />
          </Link>
        </div>
      )}

      {/* Second row: detail panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-surface border border-divider rounded p-6 lg:col-span-2">
          <p className="section-label">Pipeline health</p>
          <div className="mt-4 space-y-3">
            {[
              { label: 'Ingestion', count: standards.count, stage: '01', to: ROUTES.INGESTION },
              { label: 'Fuzzy matching', count: matches.count, stage: '02', to: ROUTES.MATCHES },
              { label: 'Expert assessment', count: assessments.count, stage: '03', to: ROUTES.QUEUE },
              { label: 'Customer notification', count: notifications.count, stage: '04', to: ROUTES.NOTIFICATIONS },
            ].map((stage) => (
              <Link
                key={stage.stage}
                to={stage.to}
                className="flex items-center gap-4 py-2 border-b border-divider last:border-0 hover:bg-elevated transition-colors rounded px-2 -mx-2"
              >
                <span className="font-mono text-xs text-accent w-8">{stage.stage}</span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-primary">{stage.label}</p>
                </div>
                <span className="font-mono text-lg font-bold text-primary">
                  {stage.count.toLocaleString()}
                </span>
                <span className="text-xs text-muted uppercase tracking-label">records</span>
              </Link>
            ))}
          </div>
        </div>

        <Link
          to={ROUTES.PIPELINE}
          className="bg-surface border border-divider rounded p-6 block hover:border-accent/40 transition-colors focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <p className="section-label">Escalations open</p>
          <div className="mt-6">
            <p className="font-mono text-5xl font-bold text-primary">
              {escalations.count}
            </p>
            <p className="mt-2 text-sm text-secondary">Sales pipeline items</p>
          </div>
          <div className="mt-6 pt-6 border-t border-divider">
            <div className="flex items-center gap-2">
              <FileCheck className="h-4 w-4 text-accent" />
              <span className="text-sm font-medium text-primary">
                {certificates.count.toLocaleString()} certificates tracked
              </span>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}
