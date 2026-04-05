import { type LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'

interface KpiCardProps {
  label: string
  value: string | number
  delta?: {
    value: string
    direction: 'up' | 'down' | 'flat'
    invertColor?: boolean // e.g. breach count going down is good
  }
  icon?: LucideIcon
  accent?: boolean // highlight with emerald left border
  className?: string
}

export function KpiCard({
  label,
  value,
  delta,
  icon: Icon,
  accent = false,
  className,
}: KpiCardProps) {
  const deltaIcon = delta
    ? delta.direction === 'up'
      ? TrendingUp
      : delta.direction === 'down'
        ? TrendingDown
        : Minus
    : null

  const deltaColor = delta
    ? delta.direction === 'flat'
      ? 'text-muted'
      : (delta.direction === 'up') !== (delta.invertColor ?? false)
        ? 'text-accent'
        : 'text-danger'
    : 'text-muted'

  return (
    <div
      className={cn(
        'bg-surface border border-divider rounded p-6',
        accent && 'border-l-2 border-l-accent',
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <p className="section-label">{label}</p>
        {Icon && <Icon className="h-4 w-4 text-muted" strokeWidth={2} />}
      </div>
      <div className="mt-3">
        <p className="font-mono text-3xl font-bold text-primary tracking-tight">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        {delta && deltaIcon && (
          <div className={cn('mt-2 flex items-center gap-1 text-xs font-medium', deltaColor)}>
            {(() => {
              const DeltaIcon = deltaIcon
              return <DeltaIcon className="h-3 w-3" strokeWidth={2.5} />
            })()}
            <span>{delta.value}</span>
          </div>
        )}
      </div>
    </div>
  )
}
