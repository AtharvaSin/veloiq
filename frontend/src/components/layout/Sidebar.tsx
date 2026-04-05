import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  ListChecks,
  Activity,
  Users,
  GitMerge,
  Mail,
  FileText,
  TrendingUp,
  Database,
  LogOut,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { getActor, clearSession } from '@/lib/demo-session'
import { ROUTES } from '@/lib/routes'

interface NavItem {
  to: string
  label: string
  icon: typeof LayoutDashboard
}

const NAV_ITEMS: NavItem[] = [
  { to: ROUTES.DASHBOARD, label: 'Dashboard', icon: LayoutDashboard },
  { to: ROUTES.QUEUE, label: 'TCC Queue', icon: ListChecks },
  { to: ROUTES.MATCHES, label: 'Match Queue', icon: GitMerge },
  { to: ROUTES.CUSTOMERS, label: 'Customers', icon: Users },
  { to: ROUTES.NOTIFICATIONS, label: 'Notifications', icon: Mail },
  { to: ROUTES.PIPELINE, label: 'Sales Pipeline', icon: TrendingUp },
  { to: ROUTES.INGESTION, label: 'Ingestion', icon: Database },
  { to: ROUTES.AUDIT, label: 'Audit Log', icon: FileText },
]

export function Sidebar() {
  const navigate = useNavigate()
  const actor = getActor()

  function handleLogout() {
    clearSession()
    navigate(ROUTES.LOGIN, { replace: true })
  }

  return (
    <aside className="w-60 flex-shrink-0 bg-void border-r border-divider flex flex-col">
      {/* Logo block */}
      <div className="h-16 flex items-center px-6 border-b border-divider">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded bg-accent flex items-center justify-center">
            <Activity className="h-5 w-5 text-obsidian" strokeWidth={2.5} />
          </div>
          <span className="font-bold text-lg tracking-tight text-primary">VeloIQ</span>
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 py-6 px-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === ROUTES.DASHBOARD}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2 rounded-tight text-sm font-medium transition-colors',
                  'border-l-2 border-transparent',
                  isActive
                    ? 'bg-elevated text-accent border-l-accent'
                    : 'text-secondary hover:bg-elevated hover:text-primary',
                )
              }
            >
              <Icon className="h-4 w-4" strokeWidth={2} />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* User block + logout at bottom */}
      <div className="px-4 py-4 border-t border-divider space-y-3">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-elevated flex items-center justify-center border border-divider">
            <span className="text-sm font-semibold text-accent">
              {actor
                .split(' ')
                .map((p) => p[0])
                .slice(0, 2)
                .join('')
                .toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-primary truncate">{actor}</p>
            <p className="text-xs text-muted">TCC Expert</p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-tight text-xs font-medium text-secondary hover:bg-elevated hover:text-primary border border-divider transition-colors"
        >
          <LogOut className="h-3.5 w-3.5" strokeWidth={2} />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  )
}
