import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import * as reportsApi from '@/api/reports'
import type { SharedReportData } from '@/api/reports'

const MATURITY_COLORS: Record<string, string> = {
  optimizado: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  avanzado: 'bg-blue-100 text-blue-800 border-blue-200',
  basico: 'bg-amber-100 text-amber-800 border-amber-200',
  critico: 'bg-red-100 text-red-800 border-red-200',
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pendiente',
  in_progress: 'En progreso',
  completed: 'Completada',
}

export default function SharePage() {
  const { token } = useParams<{ token: string }>()
  const [data, setData] = useState<SharedReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) {
      setError('Token no proporcionado')
      setLoading(false)
      return
    }
    reportsApi
      .getSharedReport(token)
      .then((d) => {
        setData(d)
        setLoading(false)
      })
      .catch((e) => {
        const status = e?.response?.status
        if (status === 410) setError('Este enlace ha expirado o fue revocado.')
        else if (status === 404) setError('Enlace no encontrado.')
        else setError(e?.response?.data?.detail || 'Error al cargar el reporte.')
        setLoading(false)
      })
  }, [token])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-slate-300 border-t-brand-800 rounded-full animate-spin" />
          <p className="text-sm text-slate-500">Cargando reporte...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center max-w-md px-6">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
            <span className="text-2xl">⚠</span>
          </div>
          <h1 className="text-lg font-bold text-slate-800 mb-2">No disponible</h1>
          <p className="text-slate-500 text-sm">{error || 'Reporte no encontrado.'}</p>
        </div>
      </div>
    )
  }

  const { scores } = data
  const maturityColor = MATURITY_COLORS[scores.maturityLevel] || MATURITY_COLORS.basico

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-lg font-bold text-slate-800">
            Diagnóstico de Cumplimiento — Ley 1581 de 2012
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {data.companyName}
            {data.completedAt && (
              <> · {new Date(data.completedAt).toLocaleDateString('es-CO')}</>
            )}
          </p>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8 space-y-6">
        {/* Global Score */}
        <section className="bg-white border border-slate-200 rounded-xl p-6 text-center">
          <p className="text-sm text-slate-500 mb-2">Puntaje Global de Cumplimiento</p>
          <p className="text-5xl font-bold text-slate-800 mb-1">
            {scores.overallPercentage.toFixed(1)}%
          </p>
          <span className={`inline-block px-4 py-1 rounded-full text-sm font-medium border ${maturityColor}`}>
            {scores.maturityLabel}
          </span>
        </section>

        {/* Block Scores */}
        <section className="bg-white border border-slate-200 rounded-xl p-6">
          <h2 className="font-semibold text-slate-800 mb-4">Resultados por Sección</h2>
          <div className="space-y-3">
            {scores.blocks.map((b) => (
              <div key={b.blockSlug}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-700 font-medium">{b.blockTitle}</span>
                  <span className="text-slate-500">{b.percentage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5">
                  <div
                    className="bg-brand-800 h-2.5 rounded-full transition-all"
                    style={{ width: `${Math.min(b.percentage, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Action Items */}
        {data.actionItems.length > 0 && (
          <section className="bg-white border border-slate-200 rounded-xl p-6">
            <h2 className="font-semibold text-slate-800 mb-4">
              Plan de Acción ({data.actionItems.length} ítems)
            </h2>
            <ul className="space-y-2">
              {data.actionItems.map((ai) => (
                <li key={ai.id} className="flex items-start gap-3 text-sm">
                  <span
                    className={`mt-0.5 w-2 h-2 rounded-full shrink-0 ${
                      ai.status === 'completed'
                        ? 'bg-emerald-500'
                        : ai.status === 'in_progress'
                          ? 'bg-amber-500'
                          : 'bg-slate-300'
                    }`}
                  />
                  <div>
                    <span className="text-slate-700">{ai.title}</span>
                    <span className="ml-2 text-xs text-slate-400">
                      {STATUS_LABELS[ai.status] || ai.status}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Footer info */}
        <p className="text-xs text-slate-400 text-center">
          Este reporte fue compartido mediante un enlace temporal. Expira:{' '}
          {new Date(data.expiresAt).toLocaleDateString('es-CO', {
            day: '2-digit', month: 'short', year: 'numeric',
          })}
          {' · '}Visto {data.viewCount} {data.viewCount === 1 ? 'vez' : 'veces'}
        </p>
      </main>
    </div>
  )
}
