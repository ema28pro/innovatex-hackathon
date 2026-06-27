import type { Question, AnswerEntry } from '@/types'

interface QuestionCardProps {
  question: Question
  answer: AnswerEntry | undefined
  onAnswer: (entry: Partial<AnswerEntry>) => void
}

export default function QuestionCard({
  question,
  answer,
  onAnswer,
}: QuestionCardProps) {
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