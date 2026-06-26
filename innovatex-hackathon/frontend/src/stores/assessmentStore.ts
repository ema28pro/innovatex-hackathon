import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Assessment, AnswerEntry, AssessmentResult } from '@/types'
import { QUESTIONS } from '@/data/questionnaire'
import { computeResult } from '@/lib/scoring'

interface AssessmentState {
  assessments: Record<string, Assessment>
  currentId: string | null
  hydrated: boolean

  getCurrent: () => Assessment | null
  startAssessment: (companyId: string, userId: string) => string
  setCurrent: (id: string) => void
  setAnswer: (questionId: string, entry: Partial<AnswerEntry>) => void
  applyGate: (gateAnswer: 'si' | 'no') => void
  isComplete: () => boolean
  complete: () => AssessmentResult | null
  clearAll: () => void
}

export const useAssessmentStore = create<AssessmentState>()(
  persist(
    (set, get) => ({
      assessments: {},
      currentId: null,
      hydrated: false,

      getCurrent: () => {
        const { currentId, assessments } = get()
        return currentId ? assessments[currentId] ?? null : null
      },

      startAssessment: (companyId, userId) => {
        const id = crypto.randomUUID()
        const assessment: Assessment = {
          id,
          companyId,
          userId,
          status: 'draft',
          answers: {},
          result: null,
          createdAt: new Date().toISOString(),
          completedAt: null,
        }
        set((s) => ({
          assessments: { ...s.assessments, [id]: assessment },
          currentId: id,
        }))
        return id
      },

      setCurrent: (id) => {
        if (get().assessments[id]) set({ currentId: id })
      },

      setAnswer: (questionId, entry) => {
        const { currentId } = get()
        if (!currentId) return
        const question = QUESTIONS.find((q) => q.id === questionId)
        set((s) => {
          const a = s.assessments[currentId]
          return {
            assessments: {
              ...s.assessments,
              [currentId]: {
                ...a,
                answers: {
                  ...a.answers,
                  [questionId]: {
                    questionId,
                    kind: question?.kind ?? 'scale',
                    ...entry,
                    updatedAt: new Date().toISOString(),
                  },
                },
              },
            },
          }
        })
      },

      applyGate: (gateAnswer) => {
        const { currentId } = get()
        if (!currentId) return
        set((s) => {
          const a = s.assessments[currentId]
          const answers = { ...a.answers }
          // Set P1
          answers['P1'] = {
            questionId: 'P1',
            kind: 'gate',
            gate: gateAnswer,
            updatedAt: new Date().toISOString(),
          }
          if (gateAnswer === 'no') {
            // Force P2-P5 to 0
            for (const forcedId of ['P2', 'P3', 'P4', 'P5']) {
              answers[forcedId] = {
                questionId: forcedId,
                kind: 'scale',
                scale: 0,
                forced: true,
                updatedAt: new Date().toISOString(),
              }
            }
          } else {
            // Remove forced answers so user can re-answer
            for (const forcedId of ['P2', 'P3', 'P4', 'P5']) {
              if (answers[forcedId]?.forced) {
                delete answers[forcedId]
              }
            }
          }
          return {
            assessments: { ...s.assessments, [currentId]: { ...a, answers } },
          }
        })
      },

      isComplete: () => {
        const a = get().getCurrent()
        if (!a) return false
        const required = QUESTIONS.filter((q) => q.kind !== 'validation')
        return required.every((q) => a.answers[q.id] != null)
      },

      complete: () => {
        const a = get().getCurrent()
        if (!a || !get().isComplete()) return null
        const result = computeResult(a.answers)
        set((s) => ({
          assessments: {
            ...s.assessments,
            [a.id]: {
              ...a,
              status: 'completed',
              result,
              completedAt: new Date().toISOString(),
            },
          },
        }))
        return result
      },

      clearAll: () => set({ assessments: {}, currentId: null }),
    }),
    {
      name: 'diagnostico:assessment',
      onRehydrateStorage: () => (state) => {
        if (state) state.hydrated = true
      },
    }
  )
)