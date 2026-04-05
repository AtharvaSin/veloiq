import { Inbox } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface EmptyStateProps {
  message?: string
  hint?: string
  action?: { label: string; onClick: () => void }
  className?: string
}

export function EmptyState({
  message = 'No records to display.',
  hint,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 py-16 px-4 text-center',
        className,
      )}
    >
      <div className="h-12 w-12 rounded-full bg-elevated flex items-center justify-center">
        <Inbox className="h-6 w-6 text-muted" strokeWidth={1.5} />
      </div>
      <div>
        <p className="text-sm font-medium text-secondary">{message}</p>
        {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
      </div>
      {action && (
        <Button variant="outline" size="sm" onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  )
}
