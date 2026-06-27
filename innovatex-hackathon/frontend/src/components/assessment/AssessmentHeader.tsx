export type SavingState = 'idle' | 'pending' | 'saving' | 'saved' | 'error'

interface AssessmentHeaderProps {
  progressPct: number
  totalAnswered: number
  totalQuestions: number
  saving?: SavingState
}

function SavingIndicator({ saving }: { saving?: SavingState }) {
  switch (saving) {
    case 'pending':
      return <span className="text-slate-400 text-xs">Pendiente…</span>
    case 'saving':
      return <span className="text-amber-500 text-xs">Guardando…</span>
    case 'error':
      return <span className="text-red-500 text-xs">⚠ Error al guardar</span>
    case 'idle':
    case 'saved':
    default:
      return <span className="text-emerald-600 text-xs">Guardado ✓</span>
  }
}

export default function AssessmentHeader({
  progressPct,
  totalAnswered,
  totalQuestions,
  saving,
}: AssessmentHeaderProps) {
  const safePct = Math.min(100, Math.max(0, progressPct))
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-3">
        <h1 className="text-xl font-semibold text-slate-900">
          Cuestionario de Diagnóstico
        </h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-500">
            {totalAnswered} / {totalQuestions} respondidas
          </span>
          <SavingIndicator saving={saving} />
        </div>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${safePct}%` }}
        />
      </div>
      <p className="text-xs text-slate-500 mt-2">
        {Math.round(safePct)}% completado
      </p>
    </div>
  )
}