import { useLocation } from 'react-router-dom'
import { ROUTES } from '@/lib/routes'

const PAGE_TITLES: Record<string, string> = {
  [ROUTES.DASHBOARD]: 'System Dashboard',
  [ROUTES.QUEUE]: 'TCC Queue',
}

function titleFromPath(pathname: string): string {
  if (PAGE_TITLES[pathname]) return PAGE_TITLES[pathname]
  if (pathname.startsWith('/assessments/')) return 'Assessment Workspace'
  if (pathname.startsWith('/matches/')) return 'Match Forensic View'
  return 'VeloIQ'
}

export function TopBar() {
  const location = useLocation()
  const title = titleFromPath(location.pathname)

  return (
    <header className="h-16 flex-shrink-0 border-b border-divider bg-obsidian flex items-center justify-between px-8">
      <h1 className="text-xl font-semibold text-primary tracking-tight">{title}</h1>
      <div className="flex items-center gap-4">
        <span className="font-mono text-xs text-muted">
          {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
        </span>
      </div>
    </header>
  )
}
