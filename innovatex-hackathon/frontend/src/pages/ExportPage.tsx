import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAssessmentStore } from '@/stores/assessmentStore'
import { useCompanyStore } from '@/stores/companyStore'
import * as reportsApi from '@/api/reports'
import type { ShareLinkInfo } from '@/api/reports'

export default function ExportPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const loadAssessment = useAssessmentStore((s) => s.loadAssessment)
  const getCurrent = useAssessmentStore((s) => s.getCurrent)
  const companies = useCompanyStore((s) => s.companies)

  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState<'pdf' | 'excel' | null>(null)
  const [shareLink, setShareLink] = useState<ShareLinkInfo | null>(null)
  const [creatingLink, setCreatingLink] = useState(false)
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    loadAssessment(id).then(() => setLoading(false))
  }, [id, loadAssessment])

  const assessment = getCurrent()
  const company = companies.find((c) => c.id === assessment?.companyId)

  // Only completed assessments can export
  const isCompleted = assessment?.status === 'completed'

  // Trigger file download from blob
  function triggerDownload(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  }

  async function handleDownloadPdf() {
    if (!id) return
    setError(null)
    setDownloading('pdf')
    try {
      const blob = await reportsApi.downloadPdf(id)
      triggerDownload(blob, `diagnostico-${id.slice(0, 8)}.pdf`)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Error al descargar PDF')
    } finally {
      setDownloading(null)
    }
  }

  async function handleDownloadExcel() {
    if (!id) return
    setError(null)
    setDownloading('excel')
    try {
      const blob = await reportsApi.downloadExcel(id)
      triggerDownload(blob, `diagnostico-${id.slice(0, 8)}.xlsx`)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Error al descargar Excel')
    } finally {
      setDownloading(null)
    }
  }

  async function handleCreateShareLink() {
    if (!id) return
    setError(null)
    setCreatingLink(true)
    try {
      const info = await reportsApi.createShareLink(id)
      setShareLink(info)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Error al crear enlace compartible')
    } finally {
      setCreatingLink(false)
    }
  }

  async function handleCopyLink() {
    if (!shareLink) return
    try {
      await navigator.clipboard.writeText(shareLink.url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback for non-HTTPS or older browsers
      const input = document.createElement('input')
      input.value = shareLink.url
      document.body.appendChild(input)
      input.select()
      document.execCommand('copy')
      input.remove()
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-slate-300 border-t-brand-800 rounded-full animate-spin" />
      </div>
    )
  }

  if (!assessment) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-500 mb-4">Diagnóstico no encontrado</p>
          <Link to="/dashboard" className="text-brand-800 hover:underline text-sm">
            Volver al dashboard
          </Link>
        </div>
      </div>
    )
  }

  const expiresText = shareLink
    ? `Expira: ${new Date(shareLink.expiresAt).toLocaleDateString('es-CO', {
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
      })}`
    : ''

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div>
            <Link to={`/assessment/${id}`} className="text-sm text-slate-500 hover:text-brand-800">
              ← Volver al diagnóstico
            </Link>
            <h1 className="text-xl font-bold text-slate-800 mt-1">Exportar Resultados</h1>
            {company && (
              <p className="text-sm text-slate-500">
                {company.companyName} · NIT {company.nit}
              </p>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8 space-y-6">
        {/* Status warning */}
        {!isCompleted && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-amber-800 text-sm">
            El diagnóstico debe estar <strong>completado</strong> para exportar los resultados.
            {assessment.status === 'draft' && (
              <span> Vuelve al cuestionario y presiona "Finalizar diagnóstico".</span>
            )}
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
            {error}
          </div>
        )}

        {/* PDF Download */}
        <section className="bg-white border border-slate-200 rounded-xl p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="font-semibold text-slate-800">Reporte PDF</h2>
              <p className="text-sm text-slate-500 mt-1">
                Documento formal con puntaje global, gráficos por sección y recomendaciones.
              </p>
            </div>
            <button
              onClick={handleDownloadPdf}
              disabled={!isCompleted || downloading === 'pdf'}
              className="shrink-0 px-5 py-2.5 bg-brand-800 text-white rounded-lg text-sm font-medium
                         hover:bg-brand-900 disabled:opacity-40 disabled:cursor-not-allowed
                         transition-colors flex items-center gap-2"
            >
              {downloading === 'pdf' ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generando...
                </>
              ) : (
                'Descargar PDF'
              )}
            </button>
          </div>
        </section>

        {/* Excel Download */}
        <section className="bg-white border border-slate-200 rounded-xl p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="font-semibold text-slate-800">Reporte Excel</h2>
              <p className="text-sm text-slate-500 mt-1">
                Datos detallados por pregunta, puntajes y plan de acción en formato hoja de cálculo.
              </p>
            </div>
            <button
              onClick={handleDownloadExcel}
              disabled={!isCompleted || downloading === 'excel'}
              className="shrink-0 px-5 py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-medium
                         hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed
                         transition-colors flex items-center gap-2"
            >
              {downloading === 'excel' ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generando...
                </>
              ) : (
                'Descargar Excel'
              )}
            </button>
          </div>
        </section>

        {/* Share Link */}
        <section className="bg-white border border-slate-200 rounded-xl p-6">
          <div>
            <h2 className="font-semibold text-slate-800">Link Compartible</h2>
            <p className="text-sm text-slate-500 mt-1">
              Crea un enlace temporal para compartir los resultados con terceros. El enlace expira
              automáticamente a los 7 días.
            </p>
          </div>

          {shareLink ? (
            <div className="mt-4 space-y-3">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={shareLink.url}
                  className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm
                             text-slate-700 font-mono truncate"
                />
                <button
                  onClick={handleCopyLink}
                  className="px-4 py-2 bg-brand-800 text-white rounded-lg text-sm font-medium
                             hover:bg-brand-900 transition-colors shrink-0"
                >
                  {copied ? '¡Copiado!' : 'Copiar'}
                </button>
              </div>
              <p className="text-xs text-slate-400">{expiresText}</p>
              <button
                onClick={handleCreateShareLink}
                className="text-sm text-brand-800 hover:underline"
              >
                Generar nuevo enlace
              </button>
            </div>
          ) : (
            <button
              onClick={handleCreateShareLink}
              disabled={!isCompleted || creatingLink}
              className="mt-4 px-5 py-2.5 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium
                         hover:bg-slate-200 disabled:opacity-40 disabled:cursor-not-allowed
                         transition-colors flex items-center gap-2"
            >
              {creatingLink ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
                  Creando...
                </>
              ) : (
                'Crear link compartible'
              )}
            </button>
          )}
        </section>
      </main>
    </div>
  )
}
