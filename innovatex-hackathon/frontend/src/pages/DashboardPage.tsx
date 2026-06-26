import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, signOut } = useAuthStore()

  const handleLogout = async () => {
    await signOut()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Minimal header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-lg font-semibold text-slate-900">
              Diagnóstico Ley 1581
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-slate-500">{user?.email}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-slate-500 hover:text-slate-700 transition-colors"
              >
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Content placeholder */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg border border-slate-200 p-8 text-center">
          <h2 className="text-xl font-semibold text-slate-900 mb-2">
            Bienvenido a la plataforma
          </h2>
          <p className="text-slate-500">
            Aquí podrás gestionar los diagnósticos de cumplimiento de la Ley 1581 de 2012.
          </p>
        </div>
      </main>
    </div>
  )
}
