interface AssessmentHeaderProps {
  progressPct: number
  totalAnswered: number
  totalQuestions: number
}

export default function AssessmentHeader({
  progressPct,
  totalAnswered,
  totalQuestions,
}: AssessmentHeaderProps) {
  const safePct = Math.min(100, Math.max(0, progressPct))
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-3">
        <h1 className="text-xl font-semibold text-slate-900">
          Cuestionario de Diagnóstico
        </h1>
        <span className="text-sm text-slate-500">
          {totalAnswered} / {totalQuestions} respondidas
        </span>
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