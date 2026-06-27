import type { AssessmentResult, MaturityMeta } from '@/types'
import { BLOCKS } from '@/data/questionnaire'

interface ResultPanelProps {
  result: AssessmentResult
}

const BADGE_COLORS: Record<MaturityMeta['color'], string> = {
  red: 'bg-red-100 text-red-800',
  amber: 'bg-amber-100 text-amber-800',
  green: 'bg-green-100 text-green-800',
  blue: 'bg-blue-100 text-blue-800',
}

const CIRCLE_COLORS: Record<MaturityMeta['color'], string> = {
  red: 'text-red-600',
  amber: 'text-amber-600',
  green: 'text-green-600',
  blue: 'text-blue-600',
}

const BAR_COLORS: Record<MaturityMeta['color'], string> = {
  red: 'bg-red-500',
  amber: 'bg-amber-500',
  green: 'bg-green-500',
  blue: 'bg-blue-500',
}

export default function ResultPanel({ result }: ResultPanelProps) {
  const { totalPct, maturity, blocks } = result
  const circle = 2 * Math.PI * 52
  const offset = circle - (circle * Math.min(100, Math.max(0, totalPct))) / 100

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4 text-center">
          Resultado del diagnóstico
        </h2>

        {/* Percentage circle */}
        <div className="flex flex-col items-center gap-4">
          <div className="relative w-36 h-36">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
              <circle
                cx="60"
                cy="60"
                r="52"
                fill="none"
                stroke="currentColor"
                strokeWidth="10"
                className="text-slate-200"
              />
              <circle
                cx="60"
                cy="60"
                r="52"
                fill="none"
                stroke="currentColor"
                strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray={circle}
                strokeDashoffset={offset}
                className={CIRCLE_COLORS[maturity.color]}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-3xl font-semibold text-slate-900">
                {Math.round(totalPct)}%
              </span>
            </div>
          </div>

          <span className={`maturity-badge ${BADGE_COLORS[maturity.color]}`}>
            {maturity.label}
          </span>

          <p className="text-sm text-slate-600 text-center max-w-xl">
            {maturity.description}
          </p>

          <p className="text-xs text-slate-400">
            Puntaje: {result.totalObtained} / {result.maxPossible}
          </p>
        </div>
      </div>

      {/* Per-block breakdown */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
        <h3 className="text-base font-semibold text-slate-900">
          Desglose por bloque
        </h3>
        {blocks.map((b) => {
          const meta = BLOCKS.find((blk) => blk.id === b.blockId)
          return (
            <div key={b.blockId} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-slate-700">
                  {meta?.title ?? b.blockId}
                </span>
                <span className="text-slate-500">
                  {Math.round(b.obtained * 100) / 100} / {b.max} ·{' '}
                  {Math.round(b.pct)}%
                </span>
              </div>
              <div className="progress-track">
                <div
                  className={`h-full transition-all duration-500 ${BAR_COLORS[maturity.color]}`}
                  style={{ width: `${Math.min(100, b.pct)}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}