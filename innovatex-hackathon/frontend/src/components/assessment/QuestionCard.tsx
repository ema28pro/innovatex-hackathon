import { useState } from 'react'
import type { Question, AnswerEntry } from '@/types'
import ExplainModal from './ExplainModal'

interface QuestionCardProps {
  question: Question
  answer: AnswerEntry | undefined
  onAnswer: (entry: Partial<AnswerEntry>) => void
  onExplain?: () => Promise<string>
  onSuggest?: () => Promise<string>
}

export default function QuestionCard({
  question,
  answer,
  onAnswer,
  onExplain,
  onSuggest,
}: QuestionCardProps) {
  const [modalOpen, setModalOpen] = useState(false)
  const [modalTitle, setModalTitle] = useState('')
  const [modalContent, setModalContent] = useState('')
  const [modalLoading, setModalLoading] = useState(false)

  const handleAI = async (mode: 'explain' | 'suggest') => {
    const fn = mode === 'explain' ? onExplain : onSuggest
    if (!fn) return
    setModalTitle(mode === 'explain' ? 'Explicación IA' : 'Sugerencia IA')
    setModalContent('')
    setModalLoading(true)
    setModalOpen(true)
    try {
      const result = await fn()
      setModalContent(result)
    } catch {
      setModalContent('Error al contactar el servicio de IA. Intente de nuevo.')
    } finally {
      setModalLoading(false)
    }
  }
  const aiButtons = (
    <div className="flex gap-2 pt-2">
      {onExplain && (
        <button
          type="button"
          onClick={() => handleAI('explain')}
          className="text-xs px-3 py-1.5 rounded-md border border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-colors flex items-center gap-1.5"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Explicar
        </button>
      )}
      {onSuggest && (
        <button
          type="button"
          onClick={() => handleAI('suggest')}
          className="text-xs px-3 py-1.5 rounded-md border border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-colors flex items-center gap-1.5"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          Sugerir
        </button>
      )}
    </div>
  )

  if (question.kind === 'gate') {
    const selected = answer?.gate
    return (
      <div className="space-y-3">
        <p className="text-base text-slate-900 font-medium">{question.text}</p>
        <div className="flex gap-4">
          <button
            type="button"
            className={`gate-btn ${selected === 'si' ? 'selected' : ''}`}
            onClick={() => onAnswer({ gate: 'si' })}
          >
            Sí
          </button>
          <button
            type="button"
            className={`gate-btn ${selected === 'no' ? 'selected' : ''}`}
            onClick={() => onAnswer({ gate: 'no' })}
          >
            No
          </button>
        </div>
        {aiButtons}
        <ExplainModal
          open={modalOpen}
          title={modalTitle}
          content={modalContent}
          loading={modalLoading}
          onClose={() => setModalOpen(false)}
        />
      </div>
    )
  }

  if (question.kind === 'validation') {
    const selected = answer?.validation
    return (
      <div className="space-y-3">
        <p className="text-base text-slate-900 font-medium">{question.text}</p>
        <div className="flex gap-4">
          <button
            type="button"
            className={`gate-btn ${selected === 'si' ? 'selected' : ''}`}
            onClick={() => onAnswer({ validation: 'si' })}
          >
            Sí
          </button>
          <button
            type="button"
            className={`gate-btn ${selected === 'no' ? 'selected' : ''}`}
            onClick={() => onAnswer({ validation: 'no' })}
          >
            No
          </button>
        </div>
        {aiButtons}
        <ExplainModal
          open={modalOpen}
          title={modalTitle}
          content={modalContent}
          loading={modalLoading}
          onClose={() => setModalOpen(false)}
        />
      </div>
    )
  }

  // scale
  const forced = answer?.forced === true
  const selectedScale = answer?.scale

  return (
    <div className="space-y-3">
      <p className="text-base text-slate-900 font-medium">{question.text}</p>
      {forced && (
        <p className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-md p-3">
          Forzado a 0% por filtro P1=No
        </p>
      )}
      <div className="space-y-2">
        {question.options.map((opt) => {
          const isSelected = selectedScale === opt.scale
          const classes = [
            'radio-card',
            isSelected ? 'selected' : '',
            forced ? 'disabled' : '',
          ]
            .filter(Boolean)
            .join(' ')
          return (
            <label key={opt.scale} className={classes}>
              <input
                type="radio"
                name={question.id}
                className="mt-1 accent-brand-700"
                disabled={forced}
                checked={isSelected}
                onChange={() => onAnswer({ scale: opt.scale, forced: false })}
              />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-900">
                    {opt.label}
                  </span>
                  <span className="text-xs text-slate-500">
                    {opt.scale}%
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-1">{opt.description}</p>
              </div>
            </label>
          )
        })}
      </div>
      {aiButtons}
      <ExplainModal
        open={modalOpen}
        title={modalTitle}
        content={modalContent}
        loading={modalLoading}
        onClose={() => setModalOpen(false)}
      />
    </div>
  )
}