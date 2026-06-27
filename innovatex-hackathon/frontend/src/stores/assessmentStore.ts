import { create } from 'zustand'
import type { Assessment, AnswerEntry, AssessmentResult } from '@/types'
import { QUESTIONS } from '@/data/questionnaire'
import { computeResult } from '@/lib/scoring'
import * as api from '@/api/assessments'

export type SavingState = 'idle' | 'pending' | 'saving' | 'saved' | 'error'

// Question IDs forced to scale=0 when the politica gate (P1) is answered "no".
const FORCED_BY_GATE = ['P2', 'P3', 'P4', 'P5']

interface AssessmentState {
  assessments: Record<string, Assessment>
  currentId: string | null
  hydrated: boolean

  // async lifecycle flags
  loading: boolean
  error: string | null
  saving: SavingState

  getCurrent: () => Assessment | null
  startAssessment: (companyId: string, userId?: string) => Promise<Assessment>
  loadAssessment: (id: string) => Promise<Assessment | null>
  setCurrent: (id: string) => void
  setAnswer: (questionId: string, entry: Partial<AnswerEntry>) => void
  persistAnswer: (questionId: string, entry: AnswerEntry) => Promise<void>
  applyGate: (gateAnswer: 'si' | 'no') => Promise<void>
  isComplete: () => boolean
  complete: () => Promise<AssessmentResult | null>
  clearAll: () => void
}

export const useAssessmentStore = create<AssessmentState>((set, get) => ({
  assessments: {},
  currentId: null,
  hydrated: true,

  loading: false,
  error: null,
  saving: 'idle',

  getCurrent: () => {
    const { currentId, assessments } = get()
    return currentId ? assessments[currentId] ?? null : null
  },

  startAssessment: async (companyId) => {
    set({ loading: true, error: null })
    try {
      const assessment = await api.startAssessment(companyId)
      set((s) => ({
        assessments: { ...s.assessments, [assessment.id]: assessment },
        currentId: assessment.id,
        loading: false,
      }))
      return assessment
    } catch (e: any) {
      set({ loading: false, error: e?.message || 'Error al iniciar el diagnóstico' })
      throw e
    }
  },

  loadAssessment: async (id) => {
    set({ loading: true, error: null })
    try {
      const assessment = await api.getAssessment(id)
      set((s) => ({
        assessments: { ...s.assessments, [id]: assessment },
        currentId: id,
        loading: false,
      }))
      return assessment
    } catch (e: any) {
      set({ loading: false, error: e?.message || 'Error al cargar el diagnóstico' })
      return null
    }
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
      if (!a) return s
      return {
        saving: 'pending',
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

  persistAnswer: async (questionId, entry) => {
    const { currentId } = get()
    if (!currentId) return
    set({ saving: 'saving' })
    try {
      await api.upsertAnswer(currentId, entry)
      set({ saving: 'saved' })
    } catch (e: any) {
      set({ saving: 'error' })
      throw e
    }
  },

  applyGate: async (gateAnswer) => {
    const { currentId } = get()
    if (!currentId) return

    const now = new Date().toISOString()
    const affected: AnswerEntry[] = [
      { questionId: 'P1', kind: 'gate', gate: gateAnswer, updatedAt: now },
    ]

    // Apply local state + mark pending
    set((s) => {
      const a = s.assessments[currentId]
      if (!a) return s
      const answers = { ...a.answers }

      if (gateAnswer === 'no') {
        // Snapshot real P2-P5 answers BEFORE overwriting with forced zeros
        const preGate: Record<string, AnswerEntry> = (a as any)._preGate || {}
        for (const forcedId of FORCED_BY_GATE) {
          if (answers[forcedId] && !answers[forcedId].forced) {
            preGate[forcedId] = { ...answers[forcedId] }
          }
        }
        // Write forced zero answers
        for (const forcedId of FORCED_BY_GATE) {
          affected.push({
            questionId: forcedId,
            kind: 'scale',
            scale: 0,
            forced: true,
            updatedAt: now,
          })
          answers[forcedId] = {
            questionId: forcedId,
            kind: 'scale',
            scale: 0,
            forced: true,
            updatedAt: now,
          }
        }
        answers['P1'] = { questionId: 'P1', kind: 'gate', gate: 'no', updatedAt: now }
        return {
          saving: 'pending',
          assessments: {
            ...s.assessments,
            [currentId]: { ...a, answers, _preGate: preGate } as Assessment,
          },
        }
      } else {
        // gateAnswer === 'si': restore from preGate snapshot
        const preGate: Record<string, AnswerEntry> = (a as any)._preGate || {}
        for (const forcedId of FORCED_BY_GATE) {
          if (preGate[forcedId]) {
            answers[forcedId] = { ...preGate[forcedId] }
          } else {
            delete answers[forcedId]
          }
        }
        answers['P1'] = { questionId: 'P1', kind: 'gate', gate: 'si', updatedAt: now }
        return {
          saving: 'pending',
          assessments: {
            ...s.assessments,
            [currentId]: { ...a, answers, _preGate: {} } as Assessment,
          },
        }
      }
    })

    // Persist the affected batch directly (the debounce hook is single-entry,
    // so the store handles the multi-answer gate persistence).
    set({ saving: 'saving' })
    try {
      for (const entry of affected) {
        await api.upsertAnswer(currentId, entry)
      }
      set({ saving: 'saved' })
    } catch (e: any) {
      set({ saving: 'error' })
    }
  },

  isComplete: () => {
    const a = get().getCurrent()
    if (!a) return false
    const required = QUESTIONS.filter((q) => q.kind !== 'validation')
    return required.every((q) => a.answers[q.id] != null)
  },

  complete: async () => {
    const a = get().getCurrent()
    if (!a || !get().isComplete()) return null
    try {
      await api.updateAssessment(a.id, 'completed')
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
    } catch (e: any) {
      set({ error: e?.message || 'Error al completar el diagnóstico' })
      return null
    }
  },

  clearAll: () =>
    set({ assessments: {}, currentId: null, error: null, saving: 'idle' }),
}))