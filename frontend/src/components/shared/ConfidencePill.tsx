import { cn } from '@/lib/utils'

type ConfidenceTier = 'auto_match' | 'expert_review' | 'manual_triage'

interface ConfidencePillProps {
  score: number // 0.0 - 1.0
  showLabel?: boolean // default true
  className?: string
}

interface TierSpec {
  tier: ConfidenceTier
  label: string
  className: string // text + bg color classes
}

function classifyScore(score: number): TierSpec {
  if (score > 0.95) {
    return {
      tier: 'auto_match',
      label: 'AUTO MATCH',
      className: 'text-accent bg-accent/10',
    }
  }
  if (score >= 0.70) {
    return {
      tier: 'expert_review',
      label: 'EXPERT REVIEW',
      className: 'text-warn bg-warn/10',
    }
  }
  return {
    tier: 'manual_triage',
    label: 'MANUAL TRIAGE',
    className: 'text-danger bg-danger/10',
  }
}

export function ConfidencePill({
  score,
  showLabel = true,
  className,
}: ConfidencePillProps) {
  const spec = classifyScore(score)
  const formattedScore = score.toFixed(3)
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-tight px-2 py-0.5 font-mono text-xs font-semibold whitespace-nowrap',
        spec.className,
        className,
      )}
      title={`Confidence: ${formattedScore} (${spec.label})`}
    >
      {formattedScore}
      {showLabel && <span className="ml-1.5 tracking-wide">· {spec.label}</span>}
    </span>
  )
}

// Accept string input too (for DecimalStr from backend)
export function ConfidencePillFromString({
  score,
  ...props
}: Omit<ConfidencePillProps, 'score'> & { score: string }) {
  const parsed = Number.parseFloat(score)
  if (Number.isNaN(parsed)) {
    return <span className="text-muted font-mono text-xs">—</span>
  }
  return <ConfidencePill score={parsed} {...props} />
}
