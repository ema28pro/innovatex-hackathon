import { useState, useCallback } from 'react'
import type { RemediationPlan, RemediationPlanItem, WeakQuestion } from '@/types'
import { generateRemediationPlan } from '@/api/remediationPlan'

interface RemediationPlanViewProps {
  assessmentId: string
}

const PRIORITY_BADGE: Record<string, string> = {
  high: 'bg-red-100 text-red-800',
  medium: 'bg-amber-100 text-amber-800',
  low: 'bg-blue-100 text-blue-800',
}

const PRIORITY_LABEL: Record<string, string> = {
  high: 'Alta',
  medium: 'Media',
  low: 'Baja',
}

const STATUS_BADGE: Record<string, string> = {
  no: 'bg-red-100 text-red-800',
  partial: 'bg-amber-100 text-amber-800',
}

function getQuestionStatus(item: WeakQuestion | RemediationPlanItem): 'no' | 'partial' {
  const answer = 'currentAnswer' in item ? item.currentAnswer : ''
  if (answer === 'No' || answer === '0/100' || answer.startsWith('0/')) return 'no'
  return 'partial'
}

function WeakQuestionRow({ question }: { question: WeakQuestion }) {
  const status = getQuestionStatus(question)
  return (
    <div className="flex items-start gap-3 py-2 border-b border-slate-100 last:border-0">
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${STATUS_BADGE[status]}`}>
        {status === 'no' ? 'No' : 'Parcial'}
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-slate-900">
          {question.questionSlug}
          <span className="text-slate-400 font-normal"> · {question.blockTitle}</span>
        </p>
        <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{question.questionText}</p>
        <p className="text-xs text-slate-400 mt-0.5">Respuesta: {question.currentAnswer}</p>
      </div>
    </div>
  )
}

function PlanItemCard({ item }: { item: RemediationPlanItem }) {
  const [expanded, setExpanded] = useState(false)
  const status = getQuestionStatus(item)

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left p-4 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-slate-400 uppercase">
                {item.questionSlug || ''}
              </span>
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${PRIORITY_BADGE[item.priority]}`}>
                {PRIORITY_LABEL[item.priority]}
              </span>
              {status && (
                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${STATUS_BADGE[status]}`}>
                  {status === 'no' ? 'No' : 'Parcial'}
                </span>
              )}
            </div>
            <h4 className="text-sm font-semibold text-slate-900">{item.title}</h4>
          </div>
          <svg
            className={`w-4 h-4 text-slate-400 mt-1 transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3 border-t border-slate-100">
          {item.questionText && (
            <div className="pt-3">
              <p className="text-xs text-slate-500 font-medium mb-1">Pregunta</p>
              <p className="text-sm text-slate-700">{item.questionText}</p>
              {item.currentAnswer && (
                <p className="text-xs text-slate-400 mt-1">Respuesta actual: {item.currentAnswer}</p>
              )}
            </div>
          )}

          <div>
            <p className="text-xs text-slate-500 font-medium mb-1">Descripción</p>
            <p className="text-sm text-slate-700 whitespace-pre-line">{item.description}</p>
          </div>

          {item.steps.length > 0 && (
            <div>
              <p className="text-xs text-slate-500 font-medium mb-1">Pasos recomendados</p>
              <ol className="list-decimal list-inside space-y-1">
                {item.steps.map((step, i) => (
                  <li key={i} className="text-sm text-slate-700">{step}</li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function RemediationPlanView({ assessmentId }: RemediationPlanViewProps) {
  const [plan, setPlan] = useState<RemediationPlan | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await generateRemediationPlan(assessmentId)
      setPlan(result)
      if (result.error) {
        setError(result.error)
      }
    } catch (e: any) {
      setError(e?.message || 'Error al generar el plan de remediación')
    } finally {
      setLoading(false)
    }
  }, [assessmentId])

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Plan de Remediación
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Basado en las preguntas respondidas con "No" o "Parcialmente"
            </p>
          </div>
          {!plan && (
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="px-4 py-2 bg-brand-800 text-white rounded-lg text-sm font-medium hover:bg-brand-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Generando...' : 'Generar plan'}
            </button>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-8">
            <div className="flex flex-col items-center gap-2">
              <div className="w-6 h-6 border-2 border-slate-300 border-t-brand-800 rounded-full animate-spin" />
              <p className="text-sm text-slate-500">Analizando respuestas y generando plan...</p>
            </div>
          </div>
        )}
      </div>

      {/* Show weak questions summary when plan is loaded */}
      {plan && plan.weakQuestions.length > 0 && (
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h3 className="text-base font-semibold text-slate-900 mb-3">
            Preguntas débiles identificadas ({plan.weakQuestions.length})
          </h3>
          <div className="divide-y divide-slate-100">
            {plan.weakQuestions.map((q) => (
              <WeakQuestionRow key={q.questionSlug} question={q} />
            ))}
          </div>
        </div>
      )}

      {/* AI-generated plan items */}
      {plan && plan.planItems.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-base font-semibold text-slate-900 px-1">
            Plan de acción recomendado
          </h3>
          {plan.planItems.map((item, idx) => (
            <PlanItemCard key={`${item.questionSlug}-${idx}`} item={item} />
          ))}
        </div>
      )}

      {/* Regenerate button */}
      {plan && (
        <div className="text-center">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="text-sm text-brand-800 hover:text-brand-900 underline underline-offset-2 disabled:opacity-50"
          >
            {loading ? 'Generando...' : 'Regenerar plan'}
          </button>
        </div>
      )}

      {/* Empty state: plan but no weak questions */}
      {plan && plan.weakQuestions.length === 0 && plan.planItems.length === 0 && !error && (
        <div className="bg-white rounded-lg border border-slate-200 p-8 text-center">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-base font-semibold text-slate-900 mb-1">
            ¡Excelente resultado!
          </h3>
          <p className="text-sm text-slate-500">
            No se identificaron preguntas débiles. Todas las respuestas están en nivel óptimo.
          </p>
        </div>
      )}
    </div>
  )
}
