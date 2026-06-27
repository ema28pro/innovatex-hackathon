import { useEffect } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useCompanyStore } from '@/stores/companyStore'

export default function ProtectedRoute() {
  const { session, loading, initialized } = useAuthStore()
  const companies = useCompanyStore((s) => s.companies)
  const loaded = useCompanyStore((s) => s.loaded)
  const loadCompanies = useCompanyStore((s) => s.loadCompanies)
  const location = useLocation()
  const ONBOARDING_PATH = '/onboarding'

  // Fetch companies once auth is ready
  useEffect(() => {
    if (session?.access_token && !loaded) {
      loadCompanies()
    }
  }, [session?.access_token, loaded, loadCompanies])

  // Wait for auth + companies to load
  const waiting = loading || !initialized || (!!session?.access_token && !loaded)

  if (waiting) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-slate-300 border-t-brand-800 rounded-full animate-spin" />
          <p className="text-sm text-slate-500">Verificando sesión...</p>
        </div>
      </div>
    )
  }

  if (!session?.access_token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  const isOnOnboarding = location.pathname === ONBOARDING_PATH
  const hasCompany = companies.length > 0

  if (!hasCompany && !isOnOnboarding) {
    return <Navigate to={ONBOARDING_PATH} replace />
  }
  if (hasCompany && isOnOnboarding) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
