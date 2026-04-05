import { cn } from '@/lib/utils'

type StatusVariant =
  | 'certificate'
  | 'notification'
  | 'escalation'
  | 'match'
  | 'default'

interface StatusBadgeProps {
  status: string
  variant: StatusVariant
  className?: string
}

// Map status values to Tailwind color utility classes per DESIGN.md semantics
function stylesFor(variant: StatusVariant, status: string): string {
  switch (variant) {
    case 'certificate':
      switch (status) {
        case 'active':
          return 'text-accent bg-accent/10 border-accent/30'
        case 'expiring':
          return 'text-warn bg-warn/10 border-warn/30'
        case 'expired':
          return 'text-danger bg-danger/10 border-danger/30'
        case 'suspended':
          return 'text-muted bg-muted/10 border-muted/30'
        default:
          return 'text-secondary bg-elevated border-divider'
      }
    case 'notification':
      switch (status) {
        case 'sent':
        case 'delivered':
        case 'opened':
        case 'clicked':
          return 'text-accent bg-accent/10 border-accent/30'
        case 'queued':
          return 'text-secondary bg-elevated border-divider'
        case 'bounced':
          return 'text-warn bg-warn/10 border-warn/30'
        case 'breached':
          return 'text-danger bg-danger/10 border-danger/30'
        default:
          return 'text-secondary bg-elevated border-divider'
      }
    case 'escalation':
      switch (status) {
        case 'open':
          return 'text-warn bg-warn/10 border-warn/30'
        case 'contacted':
          return 'text-block-cert bg-block-cert/10 border-block-cert/30'
        case 'resolved':
          return 'text-accent bg-accent/10 border-accent/30'
        default:
          return 'text-secondary bg-elevated border-divider'
      }
    case 'match':
      switch (status) {
        case 'pending':
          return 'text-warn bg-warn/10 border-warn/30'
        case 'reviewed':
          return 'text-accent bg-accent/10 border-accent/30'
        default:
          return 'text-secondary bg-elevated border-divider'
      }
    case 'default':
    default:
      return 'text-secondary bg-elevated border-divider'
  }
}

export function StatusBadge({ status, variant, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-tight px-2 py-0.5 text-xs font-medium uppercase tracking-wide border',
        stylesFor(variant, status),
        className,
      )}
    >
      {status.replace(/_/g, ' ')}
    </span>
  )
}
