import { AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface ErrorStateProps {
  message?: string
  hint?: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({
  message = 'Something went wrong.',
  hint,
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 py-16 px-4 text-center',
        className,
      )}
    >
      <div className="h-12 w-12 rounded-full bg-danger/10 flex items-center justify-center">
        <AlertTriangle className="h-6 w-6 text-danger" strokeWidth={2} />
      </div>
      <div>
        <p className="text-sm font-medium text-primary">{message}</p>
        {hint && <p className="mt-1 text-xs text-muted font-mono">{hint}</p>}
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  )
}
