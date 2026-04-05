import { useNavigate, useParams, Link } from 'react-router-dom'
import { format } from 'date-fns'
import { ArrowLeft, ChevronRight, ArrowRight, CheckCircle2, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ConfidencePillFromString } from '@/components/shared/ConfidencePill'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useMatchDetail } from '@/hooks/useMatches'
import { useStandardDetail } from '@/hooks/useStandards'
import { ROUTES } from '@/lib/routes'
import type { DecimalStr } from '@/lib/types'
import { cn } from '@/lib/utils'

function formatScore(score: DecimalStr | null | undefined): string {
  if (!score) return '—'
  const parsed = Number.parseFloat(score)
  return Number.isNaN(parsed) ? '—' : parsed.toFixed(3)
}

function scoreToTone(
  score: DecimalStr | null | undefined,
): 'accent' | 'warn' | 'danger' | 'muted' {
  if (!score) return 'muted'
  const parsed = Number.parseFloat(score)
  if (Number.isNaN(parsed)) return 'muted'
  if (parsed > 0.95) return 'accent'
  if (parsed >= 0.7) return 'warn'
  return 'danger'
}

interface AlgorithmTileProps {
  label: string
  score: DecimalStr | null | undefined
  description: string
}

function AlgorithmTile({ label, score, description }: AlgorithmTileProps) {
  const tone = scoreToTone(score)
  const toneClasses = {
    accent: 'border-accent/40 text-accent',
    warn: 'border-warn/40 text-warn',
    danger: 'border-danger/40 text-danger',
    muted: 'border-divider text-muted',
  } as const

  return (
    <div className={cn('bg-surface border rounded p-5 border-l-2', toneClasses[tone])}>
      <p className="section-label">{label}</p>
      <p className="mt-3 font-mono text-3xl font-bold text-primary">{formatScore(score)}</p>
      <p className="mt-1 text-xs text-muted leading-relaxed">{description}</p>
    </div>
  )
}

function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return format(new Date(iso), 'dd MMM yyyy · HH:mm')
  } catch {
    return iso
  }
}

export function MatchForensicPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const matchQ = useMatchDetail(id ?? '', { enabled: Boolean(id) })
  const standardQ = useStandardDetail(matchQ.data?.natos_standard_id ?? '', {
    enabled: Boolean(matchQ.data?.natos_standard_id),
  })

  if (matchQ.isLoading) return <LoadingState rows={10} />
  if (matchQ.isError || !matchQ.data) {
    return (
      <ErrorState
        message="Failed to load match result"
        hint={id ? `Match ID: ${id}` : 'No ID provided'}
        onRetry={() => matchQ.refetch()}
      />
    )
  }

  const match = matchQ.data
  const standard = standardQ.data

  const sourceCode = standard?.ac_code ?? '—'
  const normalizedSource = standard?.normalized_code ?? sourceCode.toLowerCase()
  // Synthetic SAP target reconstruction — Phase B would fetch real cert_standard_link
  const rawSapRef = `DIN EN ${sourceCode}`
  const normalizedTarget = normalizedSource

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <button
          onClick={() => navigate(ROUTES.MATCHES)}
          className="text-secondary hover:text-primary inline-flex items-center gap-1"
        >
          <ArrowLeft className="h-3 w-3" />
          Back
        </button>
        <ChevronRight className="h-3 w-3 text-muted" />
        <span className="font-mono text-secondary">Match {match.id.slice(0, 8)}…</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p className="section-label">Match forensic view</p>
          <h1 className="mt-2 text-2xl font-bold text-primary">
            {standard?.title ?? 'Loading standard…'}
          </h1>
          <p className="mt-1 font-mono text-xs text-muted">Match ID: {match.id}</p>
        </div>
        <div className="flex items-center gap-2">
          <ConfidencePillFromString score={match.similarity_score} />
          <StatusBadge status={match.status} variant="match" />
        </div>
      </div>

      {/* Section 01 — Normalization Trace */}
      <section className="space-y-3">
        <p className="section-label">01 — Normalization trace</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-surface border border-divider rounded p-5">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs uppercase tracking-label text-accent">
                NATOS source
              </span>
            </div>
            <div className="mt-4 space-y-3">
              <div>
                <p className="text-xs text-muted uppercase tracking-wide">Raw ac_code</p>
                <p className="mt-1 font-mono text-sm text-primary">{sourceCode}</p>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted">
                <ArrowRight className="h-3 w-3" />
                <span>lowercase + trim whitespace</span>
              </div>
              <div>
                <p className="text-xs text-muted uppercase tracking-wide">Normalized code</p>
                <p className="mt-1 font-mono text-sm text-accent">{normalizedSource}</p>
              </div>
            </div>
          </div>

          <div className="bg-surface border border-divider rounded p-5">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs uppercase tracking-label text-block-cert">
                SAP target
              </span>
            </div>
            <div className="mt-4 space-y-3">
              <div>
                <p className="text-xs text-muted uppercase tracking-wide">Raw standard_ref</p>
                <p className="mt-1 font-mono text-sm text-primary">{rawSapRef}</p>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted">
                <ArrowRight className="h-3 w-3" />
                <span>strip prefixes + lowercase + trim</span>
              </div>
              <div>
                <p className="text-xs text-muted uppercase tracking-wide">Normalized ref</p>
                <p className="mt-1 font-mono text-sm text-block-cert">{normalizedTarget}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 02 — Algorithm Scores */}
      <section className="space-y-3">
        <p className="section-label">02 — Algorithm scores</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <AlgorithmTile
            label="Composite (similarity)"
            score={match.similarity_score}
            description="Weighted ensemble of all algorithms below"
          />
          <AlgorithmTile
            label="Levenshtein"
            score={match.levenshtein_score}
            description="Edit-distance-based; good for character-level matches"
          />
          <AlgorithmTile
            label="Jaro-Winkler"
            score={match.jaro_winkler_score}
            description="Weights prefix matches higher; good for standards"
          />
          <AlgorithmTile
            label="Token Set"
            score={match.token_set_score}
            description="Set-based on tokens; order-invariant"
          />
        </div>
      </section>

      {/* Section 03 — Provenance */}
      <section className="space-y-3">
        <p className="section-label">03 — Provenance</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-surface border border-divider rounded p-5">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted" />
              <span className="section-label">Matched at</span>
            </div>
            <p className="mt-3 font-mono text-sm text-primary">{formatDateTime(match.matched_at)}</p>
          </div>
          <div className="bg-surface border border-divider rounded p-5">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-muted" />
              <span className="section-label">Reviewed at</span>
            </div>
            <p className="mt-3 font-mono text-sm text-primary">{formatDateTime(match.reviewed_at)}</p>
          </div>
          <div className="bg-surface border border-divider rounded p-5">
            <p className="section-label">Confidence tier</p>
            <p className="mt-3 font-mono text-sm text-primary uppercase">
              {match.confidence_tier.replace(/_/g, ' ')}
            </p>
          </div>
        </div>
      </section>

      {/* Actions */}
      <div className="flex items-center gap-3 pt-4 border-t border-divider">
        <Link to={ROUTES.QUEUE}>
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to queue
          </Button>
        </Link>
      </div>
    </div>
  )
}
