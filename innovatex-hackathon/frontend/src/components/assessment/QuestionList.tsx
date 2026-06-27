import type { Question, AnswerEntry } from '@/types'
import QuestionCard from './QuestionCard'

interface QuestionListProps {
  questions: Question[]
  answers: Record<string, AnswerEntry>
  onAnswer: (questionId: string, entry: Partial<AnswerEntry>) => void
  onGateChange: (answer: 'si' | 'no') => void
}

export default function QuestionList({
  questions,
  answers,
  onAnswer,
  onGateChange,
}: QuestionListProps) {
  const p1Answer = answers['P1']?.gate

  return (
    <div className="space-y-6">
      {questions.map((question) => {
        const answer = answers[question.id]
        const handleAnswer = (entry: Partial<AnswerEntry>) => {
          if (question.kind === 'gate') {
            onGateChange(entry.gate === 'si' ? 'si' : 'no')
          } else {
            onAnswer(question.id, entry)
          }
        }

        return (
          <div
            key={question.id}
            className="bg-white rounded-lg border border-slate-200 p-6"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold text-brand-700 bg-brand-50 px-2 py-0.5 rounded">
                {question.id}
              </span>
              {question.kind === 'scale' && question.weight > 0 && (
                <span className="text-xs text-slate-400">
                  Peso: {question.weight}%
                </span>
              )}
            </div>
            <QuestionCard
              question={question}
              answer={answer}
              onAnswer={handleAnswer}
            />
            {question.id === 'P1' && p1Answer === 'no' && (
              <p className="mt-3 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-md p-3">
                Al responder “No”, las preguntas P2–P5 se califican
                automáticamente en 0% y quedan deshabilitadas.
              </p>
            )}
          </div>
        )
      })}
    </div>
  )
}