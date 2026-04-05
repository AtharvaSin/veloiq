import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { TCCQueuePage } from '@/pages/TCCQueuePage'
import { AssessmentWorkspacePage } from '@/pages/AssessmentWorkspacePage'
import { MatchForensicPage } from '@/pages/MatchForensicPage'
import { hasSession } from '@/lib/demo-session'
import { ROUTES } from '@/lib/routes'

interface ProtectedRouteProps {
  children: React.ReactNode
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  if (!hasSession()) {
    return <Navigate to={ROUTES.LOGIN} replace />
  }
  return <>{children}</>
}

function App() {
  return (
    <Routes>
      {/* Public route */}
      <Route path={ROUTES.LOGIN} element={<LoginPage />} />

      {/* Protected routes — wrapped in AppShell */}
      <Route
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
        <Route path={ROUTES.QUEUE} element={<TCCQueuePage />} />
        <Route path={ROUTES.ASSESSMENT_PATTERN} element={<AssessmentWorkspacePage />} />
        <Route path={ROUTES.MATCH_PATTERN} element={<MatchForensicPage />} />
      </Route>

      {/* Catch-all: redirect to dashboard (which will redirect to login if unauthed) */}
      <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
    </Routes>
  )
}

export default App
