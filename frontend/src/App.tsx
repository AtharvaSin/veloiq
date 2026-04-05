import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { TCCQueuePage } from '@/pages/TCCQueuePage'
import { AssessmentWorkspacePage } from '@/pages/AssessmentWorkspacePage'
import { MatchForensicPage } from '@/pages/MatchForensicPage'
import { CustomerListPage } from '@/pages/CustomerListPage'
import { Customer360Page } from '@/pages/Customer360Page'
import { MatchesListPage } from '@/pages/MatchesListPage'
import { NotificationCenterPage } from '@/pages/NotificationCenterPage'
import { AuditTrailPage } from '@/pages/AuditTrailPage'
import { SalesPipelinePage } from '@/pages/SalesPipelinePage'
import { IngestionMonitorPage } from '@/pages/IngestionMonitorPage'
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
        <Route path={ROUTES.CUSTOMERS} element={<CustomerListPage />} />
        <Route path={ROUTES.CUSTOMER_PATTERN} element={<Customer360Page />} />
        <Route path={ROUTES.MATCHES} element={<MatchesListPage />} />
        <Route path={ROUTES.MATCH_PATTERN} element={<MatchForensicPage />} />
        <Route path={ROUTES.NOTIFICATIONS} element={<NotificationCenterPage />} />
        <Route path={ROUTES.AUDIT} element={<AuditTrailPage />} />
        <Route path={ROUTES.PIPELINE} element={<SalesPipelinePage />} />
        <Route path={ROUTES.INGESTION} element={<IngestionMonitorPage />} />
        <Route path={ROUTES.ASSESSMENT_PATTERN} element={<AssessmentWorkspacePage />} />
      </Route>

      {/* Catch-all: redirect to dashboard (which will redirect to login if unauthed) */}
      <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
    </Routes>
  )
}

export default App
