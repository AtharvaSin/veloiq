import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { format } from 'date-fns'
import { ArrowLeft, CheckCircle2, XCircle, AlertCircle, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useToast } from '@/hooks/use-toast'
import { Toaster } from '@/components/ui/toaster'
import { ConfidencePillFromString } from '@/components/shared/ConfidencePill'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { KpiCard } from '@/components/shared/KpiCard'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useAssessmentDetail } from '@/hooks/useAssessments'
import { useMatchDetail } from '@/hooks/useMatches'
import { useStandardDetail } from '@/hooks/useStandards'
import { ROUTES } from '@/lib/routes'
import type { ImpactClassification, ActionRequired } from '@/lib/types'

// Synthetic clause deltas — Phase B will derive from source_payload JSONB
const SYNTHETIC_CLAUSES = [
  {
    section: '4.2.1',
    label: 'Annex A — Hazard classification',
    old: 'Category I/II/III classification based on pressure × volume.',
    new: 'Extended to include fluid group classification (Group 1/2) with revised thresholds at 50 bar.',
    change: 'modified' as const,
  },
  {
    section: '6.3.2',
    label: 'Test procedure — Pressure cycling',
    old: 'Minimum 1,000 pressure cycles at 1.5× working pressure.',
    new: 'Increased to 2,500 pressure cycles at 1.43× working pressure, with intermediate visual inspection at cycle 1,000.',
    change: 'modified' as const,
  },
  {
    section: '7.1.4',
    label: 'Documentation — CE technical file',
    old: null,
    new: 'New requirement: technical file must include digital twin simulation results for all variants (> 100 L capacity).',
    change: 'added' as const,
  },
]

const IMPACT_OPTIONS: { label: string; value: ImpactClassification }[] = [
  { label: 'No change', value: 'no_change' },
  { label: 'Administrative', value: 'administrative' },
  { label: 'Minor technical', value: 'minor_technical' },
  { label: 'Major technical', value: 'major_technical' },
  { label: 'Safety critical', value: 'safety_critical' },
]

const ACTION_OPTIONS: { label: string; value: ActionRequired }[] = [
  { label: 'Reconfirm', value: 'reconfirm' },
  { label: 'Retest', value: 'retest' },
  { label: 'Suspend', value: 'suspend' },
  { label: 'Withdraw', value: 'withdraw' },
]

/**
 * Renders a colored badge for a clause change type.
 */
function ChangeBadge({ change }: { change: 'added' | 'removed' | 'modified' }) {
  switch (change) {
    case 'added':
      return (
        <span className="inline-flex items-center rounded-tight bg-accent/10 px-2 py-0.5 text-xs font-semibold text-accent uppercase tracking-wide">
          Added
        </span>
      )
    case 'removed':
      return (
        <span className="inline-flex items-center rounded-tight bg-danger/10 px-2 py-0.5 text-xs font-semibold text-danger uppercase tracking-wide">
          Removed
        </span>
      )
    case 'modified':
      return (
        <span className="inline-flex items-center rounded-tight bg-warn/10 px-2 py-0.5 text-xs font-semibold text-warn uppercase tracking-wide">
          Modified
        </span>
      )
  }
}

export function AssessmentWorkspacePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()

  const assessmentQ = useAssessmentDetail(id ?? '', { enabled: Boolean(id) })
  const matchQ = useMatchDetail(assessmentQ.data?.match_result_id ?? '', {
    enabled: Boolean(assessmentQ.data?.match_result_id),
  })
  const standardQ = useStandardDetail(matchQ.data?.natos_standard_id ?? '', {
    enabled: Boolean(matchQ.data?.natos_standard_id),
  })

  // Decision form state
  const [impact, setImpact] = useState<ImpactClassification | ''>('')
  const [action, setAction] = useState<ActionRequired | ''>('')
  const [reasonCode, setReasonCode] = useState('')
  const [notes, setNotes] = useState('')
  const [seeded, setSeeded] = useState(false)

  // Seed form once from backend data — useEffect prevents render-during-render warning
  useEffect(() => {
    const assessment = assessmentQ.data
    if (assessment && !seeded) {
      setImpact(assessment.impact_classification as ImpactClassification)
      setAction(assessment.action_required as ActionRequired)
      setReasonCode(assessment.reason_code)
      setNotes(assessment.notes ?? '')
      setSeeded(true)
    }
  }, [assessmentQ.data, seeded])

  if (assessmentQ.isLoading) {
    return <LoadingState rows={12} />
  }

  if (assessmentQ.isError || !assessmentQ.data) {
    return (
      <ErrorState
        message="Failed to load assessment"
        hint={id ? `Assessment ID: ${id}` : 'No ID provided'}
        onRetry={() => assessmentQ.refetch()}
      />
    )
  }

  const assessment = assessmentQ.data
  const match = matchQ.data
  const standard = standardQ.data

  /**
   * Validates form fields and shows a toast for approve/reject.
   * POC demo mode — no backend POST per user decision.
   */
  function handleDecision(decision: 'approved' | 'rejected') {
    if (!impact || !action || !reasonCode) {
      toast({
        title: 'Missing fields',
        description: 'Impact, action, and reason code are required.',
        variant: 'destructive',
      })
      return
    }
    toast({
      title:
        decision === 'approved'
          ? 'Decision recorded: Approved'
          : 'Decision recorded: Rejected',
      description: `${assessment.assessor_id} · impact=${impact} · action=${action} · POC demo mode — no DB write`,
    })
    // Navigate back to queue after short delay so user can read the toast
    setTimeout(() => navigate(ROUTES.QUEUE), 800)
  }

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <Link
          to={ROUTES.QUEUE}
          className="text-secondary hover:text-primary inline-flex items-center gap-1"
        >
          <ArrowLeft className="h-3 w-3" />
          TCC Queue
        </Link>
        <ChevronRight className="h-3 w-3 text-muted" />
        <span className="font-mono text-secondary">
          {standard?.ac_code ?? 'Loading…'}
        </span>
      </div>

      {/* Header */}
      <div className="space-y-3">
        <p className="section-label">Assessment workspace</p>
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-primary">
              {standard?.title ?? 'Loading standard…'}
            </h1>
            <p className="mt-1 font-mono text-xs text-muted">
              Assessment ID: {assessment.id}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {match && <ConfidencePillFromString score={match.similarity_score} />}
            <StatusBadge status={assessment.decision} variant="match" />
          </div>
        </div>
      </div>

      {/* Section 01 — Clause Delta */}
      <section className="space-y-3">
        <p className="section-label">01 — Clause delta (2018 → 2023)</p>
        <div className="bg-surface border border-divider rounded divide-y divide-divider">
          {SYNTHETIC_CLAUSES.map((clause) => (
            <div
              key={clause.section}
              className="grid grid-cols-1 md:grid-cols-[140px_1fr_120px] gap-4 p-5"
            >
              <div>
                <p className="font-mono text-sm font-semibold text-accent">
                  § {clause.section}
                </p>
                <p className="text-xs text-muted mt-1">{clause.label}</p>
              </div>
              <div className="space-y-2">
                {clause.old && (
                  <div className="text-xs">
                    <span className="font-mono text-muted">2018: </span>
                    <span className="text-secondary line-through decoration-danger/50">
                      {clause.old}
                    </span>
                  </div>
                )}
                <div className="text-xs">
                  <span className="font-mono text-accent">2023: </span>
                  <span className="text-primary">{clause.new}</span>
                </div>
              </div>
              <div className="flex md:justify-end">
                <ChangeBadge change={clause.change} />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Section 02 — Impact summary */}
      <section className="space-y-3">
        <p className="section-label">02 — Impact summary</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <KpiCard label="Affected certificates" value={8} icon={AlertCircle} accent />
          <KpiCard label="Affected customers" value={3} />
          <KpiCard label="Clause deltas" value={SYNTHETIC_CLAUSES.length} />
          <KpiCard label="Priority" value="HIGH" />
        </div>
      </section>

      {/* Section 03 — Decision form */}
      <section className="space-y-3">
        <p className="section-label">03 — Record decision</p>
        <div className="bg-surface border border-divider rounded p-6 space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label
                htmlFor="impact"
                className="text-xs uppercase tracking-label text-muted"
              >
                Impact classification *
              </Label>
              <Select
                value={impact || undefined}
                onValueChange={(v) => setImpact(v as ImpactClassification)}
              >
                <SelectTrigger id="impact" className="bg-obsidian">
                  <SelectValue placeholder="Select impact" />
                </SelectTrigger>
                <SelectContent>
                  {IMPACT_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label
                htmlFor="action"
                className="text-xs uppercase tracking-label text-muted"
              >
                Action required *
              </Label>
              <Select
                value={action || undefined}
                onValueChange={(v) => setAction(v as ActionRequired)}
              >
                <SelectTrigger id="action" className="bg-obsidian">
                  <SelectValue placeholder="Select action" />
                </SelectTrigger>
                <SelectContent>
                  {ACTION_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label
              htmlFor="reason"
              className="text-xs uppercase tracking-label text-muted"
            >
              Reason code *
            </Label>
            <Input
              id="reason"
              value={reasonCode}
              onChange={(e) => setReasonCode(e.target.value)}
              placeholder="RC-MINOR-TECH-112"
              className="bg-obsidian font-mono"
            />
          </div>

          <div className="space-y-1.5">
            <Label
              htmlFor="notes"
              className="text-xs uppercase tracking-label text-muted"
            >
              Notes
            </Label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="flex w-full rounded border border-divider bg-obsidian px-3 py-2 text-sm text-primary placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="Administrative amendment — no change to test procedure."
            />
          </div>

          <div className="flex items-center gap-3 pt-2 border-t border-divider">
            <Button onClick={() => handleDecision('approved')} className="gap-2" size="lg">
              <CheckCircle2 className="h-4 w-4" />
              Approve
            </Button>
            <Button
              onClick={() => handleDecision('rejected')}
              variant="outline"
              className="gap-2"
              size="lg"
            >
              <XCircle className="h-4 w-4" />
              Reject
            </Button>
            <div className="flex-1" />
            <p className="text-xs text-muted font-mono">
              Decided by {assessment.assessor_id}
              {assessment.decided_at &&
                ` · ${format(new Date(assessment.decided_at), 'dd MMM yyyy')}`}
            </p>
          </div>
        </div>
        <p className="text-xs text-muted italic pt-2">
          POC demo mode: Approve/Reject show toast confirmation but do NOT persist to the
          backend. Full POST workflow is Phase C.
        </p>
      </section>

      <Toaster />
    </div>
  )
}
