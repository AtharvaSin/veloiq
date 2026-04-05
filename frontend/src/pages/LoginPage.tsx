import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { setActor } from '@/lib/demo-session'
import { ROUTES } from '@/lib/routes'

const DEMO_ACTORS = [
  'Dr. M. Weber',
  'Dr. S. Chen',
  'Dr. R. Kumar',
  'Dr. A. Müller',
  'Dr. L. Schmidt',
]

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  function handleSignIn(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    // POC: real auth not implemented. Fall through to demo mode.
    setActor('Dr. M. Weber')
    navigate(ROUTES.DASHBOARD)
  }

  function handleDemoMode(actor: string) {
    setActor(actor)
    navigate(ROUTES.DASHBOARD)
  }

  return (
    <div className="min-h-screen flex bg-obsidian">
      {/* Left: brand panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-void border-r border-divider p-16 flex-col justify-between relative overflow-hidden">
        {/* decorative emerald accent */}
        <div className="absolute -top-20 -right-20 h-96 w-96 rounded-full bg-accent/5 blur-3xl" />
        <div className="absolute bottom-20 left-20 h-64 w-64 rounded-full bg-accent/10 blur-2xl" />

        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded bg-accent flex items-center justify-center">
              <Activity className="h-6 w-6 text-obsidian" strokeWidth={2.5} />
            </div>
            <span className="font-bold text-2xl tracking-tight text-primary">VeloIQ</span>
          </div>
        </div>

        <div className="relative space-y-6">
          <div>
            <p className="section-label text-accent">Standards Automation Platform</p>
            <h2 className="mt-3 text-4xl font-bold text-primary leading-tight">
              Matching velocity.
              <br />
              Compliance certainty.
            </h2>
            <p className="mt-4 text-secondary max-w-md">
              TÜV Rheinland's automated pipeline for standards ingestion, fuzzy
              matching, expert assessment, and customer notification.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-6 pt-6 border-t border-divider">
            <div>
              <p className="font-mono text-2xl font-bold text-accent">50</p>
              <p className="text-xs text-muted uppercase tracking-wide mt-1">Standards</p>
            </div>
            <div>
              <p className="font-mono text-2xl font-bold text-accent">200</p>
              <p className="text-xs text-muted uppercase tracking-wide mt-1">Certificates</p>
            </div>
            <div>
              <p className="font-mono text-2xl font-bold text-accent">30</p>
              <p className="text-xs text-muted uppercase tracking-wide mt-1">Assessments</p>
            </div>
          </div>
        </div>

        <p className="relative font-mono text-xs text-muted">
          POC demo · v0.1.0 · Phase A Foundation
        </p>
      </div>

      {/* Right: login form */}
      <div className="flex-1 flex items-center justify-center p-16">
        <div className="w-full max-w-md space-y-8">
          <div>
            <p className="section-label">Access</p>
            <h1 className="mt-2 text-3xl font-bold text-primary">Sign in to VeloIQ</h1>
            <p className="mt-2 text-sm text-secondary">
              Enter your credentials or use a demo identity below.
            </p>
          </div>

          <form onSubmit={handleSignIn} className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-xs uppercase tracking-label text-muted">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@tuv.example.com"
                className="mt-1.5 bg-surface"
              />
            </div>
            <div>
              <Label htmlFor="password" className="text-xs uppercase tracking-label text-muted">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1.5 bg-surface"
              />
            </div>
            <Button type="submit" className="w-full" size="lg">
              Sign in
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </form>

          <div className="relative py-2">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-divider" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-obsidian px-2 text-muted tracking-label">Demo mode</span>
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-xs text-muted">Sign in as a seeded TCC expert:</p>
            <div className="grid grid-cols-1 gap-2">
              {DEMO_ACTORS.slice(0, 3).map((actor) => (
                <button
                  key={actor}
                  onClick={() => handleDemoMode(actor)}
                  className="text-left px-4 py-2.5 rounded-tight border border-divider bg-surface hover:bg-elevated hover:border-accent/30 transition-colors text-sm font-medium text-primary"
                >
                  {actor}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
