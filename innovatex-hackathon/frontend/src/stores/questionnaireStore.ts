import { create } from 'zustand'
import { listBlocks, getBlockQuestions } from '@/api/blocks'
import type { Block, BlockId, Question } from '@/types'

interface QuestionnaireState {
  blocks: Block[]
  questionsByBlock: Record<BlockId, Question[]>
  loading: boolean
  error: string | null
  loaded: boolean
  fetchAll: () => Promise<void>
  getQuestions: (blockId: BlockId) => Question[]
}

export const useQuestionnaireStore = create<QuestionnaireState>((set, get) => ({
  blocks: [],
  questionsByBlock: { politica: [], diseno: [], gobernanza: [] },
  loading: false,
  error: null,
  loaded: false,

  fetchAll: async () => {
    set({ loading: true, error: null })
    try {
      const blocks = await listBlocks()
      const questionsByBlock: Record<BlockId, Question[]> = {
        politica: [],
        diseno: [],
        gobernanza: [],
      }
      for (const block of blocks) {
        const questions = await getBlockQuestions(block.id)
        questionsByBlock[block.id] = questions
      }
      set({ blocks, questionsByBlock, loaded: true, loading: false })
    } catch (e: any) {
      set({ error: e.message || 'Error loading questionnaire', loading: false })
    }
  },

  getQuestions: (blockId: BlockId) => get().questionsByBlock[blockId] ?? [],
}))