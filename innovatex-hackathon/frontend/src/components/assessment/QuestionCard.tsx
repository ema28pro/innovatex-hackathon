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
    </div>
  )
}