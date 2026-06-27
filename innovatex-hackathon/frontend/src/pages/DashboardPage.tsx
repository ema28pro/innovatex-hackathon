import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useCompanyStore } from '@/stores/companyStore'
import { useAssessmentStore } from '@/stores/assessmentStore'
import CreateCompanyModal from '@/components/CreateCompanyModal'

const SECTOR_LABELS: Record<string, string> = {
  tecnologia: 'Tecnología', salud: 'Salud', finanzas: 'Finanzas',
  comercio: 'Comercio', manufactura: 'Manufactura', educacion: 'Educación',
  gobierno: 'Gobierno', otro: 'Otro',
}
const SIZE_LABELS: Record<string, string> = {
  micro: 'Micro (1-10)', pequena: 'Pequeña (11-50)',
  mediana: 'Mediana (51-200)', grande: 'Grande (200+)',
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, signOut } = useAuthStore()
  const companies = useCompanyStore((s) => s.companies)
  const currentCompanyId = useCompanyStore((s) => s.currentCompanyId)
  const setCurrentCompany = useCompanyStore((s) => s.setCurrentCompany)
  const currentCompany = companies.find((c) => c.id === currentCompanyId) ?? null
  const assessments = useAssessmentStore((s) => s.assessments)
  const assessmentsLoading = useAssessmentStore((s) => s.loading)
  const startAssessment = useAssessmentStore((s) => s.startAssessment)
  const loadCompanyAssessments = useAssessmentStore((s) => s.loadCompanyAssessments)

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showSwitcher, setShowSwitcher] = useState(false)
  const switcherRef = useRef<HTMLDivElement>(null)

  // Load assessments when current company changes
  useEffect(() => {
    if (currentCompanyId) {
      loadCompanyAssessments(currentCompanyId)
    }
  }, [currentCompanyId, loadCompanyAssessments])

  // Close switcher on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (switcherRef.current && !switcherRef.current.contains(e.target as Node)) {
        setShowSwitcher(false)
      }
    }
    if (showSwitcher) {
      document.addEventListener('mousedown', handleClick)
      return () => document.removeEventListener('mousedown', handleClick)
    }
  }, [showSwitcher])

  const handleLogout = async () => {
    await signOut()
    navigate('/login', { replace: true })
  }

  const handleStartAssessment = async () => {
    if (!currentCompany) return
    try {
      const assessment = await startAssessment(currentCompany.id)
      navigate(`/assessment/${assessment.id}`)
    } catch {
      // error surfaced in store
    }
  }

  // Filter assessments for current company
  const companyAssessments = Object.values(assessments).filter(
    (a) => a.companyId === currentCompany?.id
  )

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-lg font-semibold text-slate-900">Diagnóstico Ley 1581</h1>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="text-sm font-medium text-brand-700 hover:text-brand-900 transition-colors flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                Nueva empresa
              </button>
              <span className="text-sm text-slate-500 hidden sm:inline">{user?.email}</span>
              <button onClick={handleLogout} className="text-sm text-slate-500 hover:text-slate-700 transition-colors">
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Company banner with switcher */}
        {currentCompany && (
          <div className="bg-white rounded-lg border border-slate-200 p-6 mb-8">
            <p className="text-xs font-medium text-brand-700 uppercase tracking-wide mb-1">
              Empresa actual
            </p>
            <div className="flex items-start justify-between">
              <div className="relative" ref={switcherRef}>
                {/* Company name - clickable to open switcher */}
                <button
                  onClick={() => setShowSwitcher(!showSwitcher)}
                  className="flex items-center gap-2 group"
                >
                  <h2 className="text-xl font-semibold text-slate-900 group-hover:text-brand-700 transition-colors">
                    {currentCompany.companyName}
                  </h2>
                  <svg className={`w-4 h-4 text-slate-400 group-hover:text-brand-700 transition-all ${
                    showSwitcher ? 'rotate-180' : ''
                  }`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                <div className="flex gap-4 mt-2 text-sm text-slate-500">
                  <span>NIT: {currentCompany.nit}</span>
                  <span>·</span>
                  <span>{SECTOR_LABELS[currentCompany.sector] ?? currentCompany.sector}</span>
                  <span>·</span>
                  <span>{SIZE_LABELS[currentCompany.size] ?? currentCompany.size}</span>
                </div>

                {/* Switcher dropdown */}
                {showSwitcher && (
                  <div className="absolute top-full left-0 mt-2 w-72 bg-white rounded-lg border border-slate-200 shadow-lg z-40 py-1">
                    <p className="px-3 py-2 text-xs font-medium text-slate-400 uppercase tracking-wide">
                      Cambiar de empresa
                    </p>
                    {companies.map((c) => (
                      <button
                        key={c.id}
                        onClick={() => {
                          setCurrentCompany(c.id)
                          setShowSwitcher(false)
                        }}
                        className={`w-full text-left px-3 py-2.5 text-sm transition-colors flex items-center justify-between ${
                          c.id === currentCompanyId
                            ? 'bg-brand-50 text-brand-700 font-medium'
                            : 'text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        <div className="min-w-0">
                          <p className="truncate">{c.companyName}</p>
                          <p className="text-xs text-slate-400 truncate">
                            {SECTOR_LABELS[c.sector] ?? c.sector} · {SIZE_LABELS[c.size] ?? c.size}
                          </p>
                        </div>
                        {c.id === currentCompanyId && (
                          <svg className="w-4 h-4 text-brand-700 shrink-0 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </button>
                    ))}
                    <div className="border-t border-slate-100 mt-1 pt-1">
                      <button
                        onClick={() => {
                          setShowSwitcher(false)
                          setShowCreateModal(true)
                        }}
                        className="w-full text-left px-3 py-2.5 text-sm text-brand-700 hover:bg-brand-50 transition-colors flex items-center gap-2"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                        </svg>
                        Registrar nueva empresa
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <button
                onClick={handleStartAssessment}
                className="px-4 py-2 bg-brand-800 text-white rounded-md text-sm font-medium hover:bg-brand-900 transition-colors shrink-0"
              >
                Iniciar diagnóstico
              </button>
            </div>
          </div>
        )}

        {/* Assessment list */}
        {assessmentsLoading ? (
          <div className="flex items-center justify-center py-16">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-2 border-slate-300 border-t-brand-800 rounded-full animate-spin" />
              <p className="text-sm text-slate-500">Cargando diagnósticos...</p>
            </div>
          </div>
        ) : companyAssessments.length > 0 ? (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-slate-900">Diagnósticos anteriores</h3>
            {companyAssessments.map((a) => (
              <div
                key={a.id}
                onClick={() => navigate(`/assessment/${a.id}`)}
                className="bg-white rounded-lg border border-slate-200 p-4 cursor-pointer hover:border-brand-300 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-900">
                      Diagnóstico del {new Date(a.createdAt).toLocaleDateString('es-CO')}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {a.status === 'completed' ? 'Completado' : 'En progreso'}
                    </p>
                  </div>
                  {a.result && (
                    <span className={`text-sm font-semibold px-3 py-1 rounded-full ${
                      a.result.maturity.color === 'red' ? 'bg-red-100 text-red-800' :
                      a.result.maturity.color === 'amber' ? 'bg-amber-100 text-amber-800' :
                      a.result.maturity.color === 'green' ? 'bg-green-100 text-green-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {a.result.totalPct}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-slate-200 p-12 text-center">
            <h3 className="text-lg font-medium text-slate-700 mb-2">Sin diagnósticos</h3>
            <p className="text-sm text-slate-500 mb-6">
              Aún no has realizado ningún diagnóstico de cumplimiento para esta empresa.
            </p>
            <button
              onClick={handleStartAssessment}
              className="inline-flex px-6 py-2.5 bg-brand-800 text-white rounded-md text-sm font-medium hover:bg-brand-900 transition-colors"
            >
              Comenzar primer diagnóstico
            </button>
          </div>
        )}
      </main>

      <CreateCompanyModal
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  )
}
