import { useState, useEffect, useMemo, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAssessmentStore } from '@/stores/assessmentStore'
import { useDebouncedSave } from '@/hooks/useDebouncedSave'
import type { BlockId, AnswerEntry } from '@/types'
import { BLOCKS, QUESTIONS } from '@/data/questionnaire'
import AssessmentHeader from '@/components/assessment/AssessmentHeader'
import BlockNavigator from '@/components/assessment/BlockNavigator'
import QuestionList from '@/components/assessment/QuestionList'
import AssessmentFooter from '@/components/assessment/AssessmentFooter'
import ResultPanel from '@/components/assessment/ResultPanel'

const BLOCK_ORDER: BlockId[] = ['politica', 'diseno', 'gobernanza']

export default function AssessmentPage() {
  const { id = '' } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const assessments = useAssessmentStore((s) => s.assessments)
  const setCurrent = useAssessmentStore((s) => s.setCurrent)
  const getCurrent = useAssessmentStore((s) => s.getCurrent)
  const loadAssessment = useAssessmentStore((s) => s.loadAssessment)
  const setAnswer = useAssessmentStore((s) => s.setAnswer)
  const persistAnswer = useAssessmentStore((s) => s.persistAnswer)
  const applyGate = useAssessmentStore((s) => s.applyGate)
  const isComplete = useAssessmentStore((s) => s.isComplete)
  const complete = useAssessmentStore((s) => s.complete)
  const loading = useAssessmentStore((s) => s.loading)
  const error = useAssessmentStore((s) => s.error)
  const saving = useAssessmentStore((s) => s.saving)

  // Debounced autosave: fires persistAnswer 500ms after last change
  const { schedule } = useDebouncedSave(persistAnswer, 500)

  const [activeBlock, setActiveBlock] = useState<BlockId>('politica')

  // Load assessment from API on mount
  useEffect(() => {
    if (id) {
      loadAssessment(id)
    }
  }, [id, loadAssessment])

  // Redirect if load failed
  useEffect(() => {
    if (error && !getCurrent()) {
      navigate('/dashboard', { replace: true })
    }
  }, [error, getCurrent, navigate])

  const assessment = getCurrent()

  // Block completion tracking
  const blockCompletion = useMemo(() => {
    const result: Record<string, boolean> = {}
    for (const block of BLOCKS) {
      const blockQuestions = QUESTIONS.filter((q) => q.blockId === block.id && q.kind !== 'validation')
      result[block.id] = blockQuestions.every((q) => assessment?.answers[q.id] != null)
    }
    return result as Record<BlockId, boolean>
  }, [assessment?.answers])

  // Progress calculation
  const progressPct = useMemo(() => {
    const required = QUESTIONS.filter((q) => q.kind !== 'validation')
    const answered = required.filter((q) => assessment?.answers[q.id] != null).length
    return required.length > 0 ? (answered / required.length) * 100 : 0
  }, [assessment?.answers])

  const totalAnswered = useMemo(() => {
    const required = QUESTIONS.filter((q) => q.kind !== 'validation')
    return required.filter((q) => assessment?.answers[q.id] != null).length
  }, [assessment?.answers])

  const totalQuestions = useMemo(
    () => QUESTIONS.filter((q) => q.kind !== 'validation').length,
    [],
  )

  // Questions for active block
  const activeQuestions = useMemo(
    () => QUESTIONS.filter((q) => q.blockId === activeBlock).sort((a, b) => a.order - b.order),
    [activeBlock],
  )

  // Block navigation
  const currentIndex = BLOCK_ORDER.indexOf(activeBlock)

  const handlePrev = useCallback(() => {
    if (currentIndex > 0) setActiveBlock(BLOCK_ORDER[currentIndex - 1])
  }, [currentIndex])

  const handleNext = useCallback(() => {
    if (currentIndex < BLOCK_ORDER.length - 1) setActiveBlock(BLOCK_ORDER[currentIndex + 1])
  }, [currentIndex])

  const handleGateChange = useCallback(
    (answer: 'si' | 'no') => {
      applyGate(answer)
    },
    [applyGate],
  )

  const handleAnswer = useCallback(
    (questionId: string, entry: Partial<AnswerEntry>) => {
      setAnswer(questionId, entry)
      // Schedule autosave via debounce
      const question = QUESTIONS.find((q) => q.id === questionId)
      const fullEntry: AnswerEntry = {
        questionId,
        kind: question?.kind ?? 'scale',
        ...entry,
        updatedAt: new Date().toISOString(),
      }
      schedule(questionId, fullEntry)
    },
    [setAnswer, schedule],
  )

  const handleSubmit = useCallback(() => {
    complete()
  }, [complete])

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-slate-300 border-t-brand-800 rounded-full animate-spin" />
          <p className="text-sm text-slate-500">Cargando diagnóstico...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error && !assessment) {
    return (
      <div className="min-h-screen bg-slate-50">
        <header className="bg-white border-b border-slate-200">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <h1 className="text-lg font-semibold text-slate-900">Diagnóstico</h1>
              <button
                onClick={() => navigate('/dashboard', { replace: true })}
                className="text-sm text-slate-500 hover:text-slate-700 transition-colors"
              >
                Volver al dashboard
              </button>
            </div>
          </div>
        </header>
        <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg border border-slate-200 p-12 text-center">
            <h2 className="text-lg font-medium text-red-700 mb-2">Error al cargar</h2>
            <p className="text-sm text-slate-500 mb-4">{error}</p>
            <button
              onClick={() => loadAssessment(id)}
              className="px-4 py-2 bg-brand-800 text-white rounded-md text-sm"
            >
              Reintentar
            </button>
          </div>
        </main>
      </div>
    )
  }

  // Show results after completion
  if (assessment?.status === 'completed' && assessment.result) {
    return (
      <div className="min-h-screen bg-slate-50">
        <header className="bg-white border-b border-slate-200">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <h1 className="text-lg font-semibold text-slate-900">
                Resultado del diagnóstico
              </h1>
              <div className="flex items-center gap-4">
                <Link
                  to={`/assessment/${id}/export`}
                  className="text-sm px-4 py-2 bg-brand-800 text-white rounded-lg hover:bg-brand-900 transition-colors"
                >
                  Exportar resultados
                </Link>
                <button
                  onClick={() => navigate('/dashboard', { replace: true })}
                  className="text-sm text-slate-500 hover:text-slate-700 transition-colors"
                >
                  Volver al dashboard
                </button>
              </div>
            </div>
          </div>
        </header>
        <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <ResultPanel result={assessment.result} />
          <div className="mt-6 text-center">
            <Link
              to={`/assessment/${id}/export`}
              className="inline-block px-6 py-3 bg-brand-800 text-white rounded-lg text-sm font-medium hover:bg-brand-900 transition-colors"
            >
              Descargar PDF / Excel · Compartir resultados
            </Link>
          </div>
        </main>
      </div>
    )
  }

  // Not found
  if (!assessment) {
    return (
      <div className="min-h-screen bg-slate-50">
        <header className="bg-white border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <h1 className="text-lg font-semibold text-slate-900">Diagnóstico</h1>
              <button
                onClick={() => navigate('/dashboard', { replace: true })}
                className="text-sm text-slate-500 hover:text-slate-700 transition-colors"
              >
                Volver al dashboard
              </button>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg border border-slate-200 p-12 text-center">
            <h2 className="text-lg font-medium text-slate-700 mb-2">
              Diagnóstico no encontrado
            </h2>
            <p className="text-sm text-slate-500">
              El diagnóstico solicitado no existe o fue eliminado.
            </p>
          </div>
        </main>
      </div>
    )
  }

  // Store has result via previous complete() call
  const showResult = assessment.result != null

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-lg font-semibold text-slate-900">Diagnóstico</h1>
            <button
              onClick={() => navigate('/dashboard', { replace: true })}
              className="text-sm text-slate-500 hover:text-slate-700 transition-colors"
            >
              Volver al dashboard
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Progress header */}
        <AssessmentHeader
          progressPct={progressPct}
          totalAnswered={totalAnswered}
          totalQuestions={totalQuestions}
          saving={saving}
        />

        {showResult ? (
          <>
            <ResultPanel result={assessment.result!} />
            <div className="text-center">
              <Link
                to={`/assessment/${id}/export`}
                className="inline-block px-6 py-3 bg-brand-800 text-white rounded-lg text-sm font-medium hover:bg-brand-900 transition-colors"
              >
                Descargar PDF / Excel · Compartir resultados
              </Link>
            </div>
          </>
        ) : (
          <>
            {/* Block navigator */}
            <BlockNavigator
              blocks={BLOCKS}
              activeBlock={activeBlock}
              onSelect={setActiveBlock}
              blockCompletion={blockCompletion}
            />

            {/* Questions */}
            <QuestionList
              questions={activeQuestions}
              answers={assessment.answers}
              onAnswer={handleAnswer}
              onGateChange={handleGateChange}
            />

            {/* Footer navigation */}
            <AssessmentFooter
              onPrev={handlePrev}
              onNext={handleNext}
              prevDisabled={currentIndex === 0}
              nextDisabled={currentIndex === BLOCK_ORDER.length - 1}
              onSubmit={handleSubmit}
              submitDisabled={!isComplete()}
            />
          </>
        )}
      </main>
    </div>
  )
}
