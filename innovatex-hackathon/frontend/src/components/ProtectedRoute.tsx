import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

export default function ProtectedRoute() {
  const { session, loading, initialized } = useAuthStore()
  const location = useLocation()

  // Show loading spinner while checking auth state
  if (loading || !initialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-slate-300 border-t-brand-800 rounded-full animate-spin" />
          <p className="text-sm text-slate-500">Verificando sesión...</p>
        </div>
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!session?.access_token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Render child routes
  return <Outlet />
}
