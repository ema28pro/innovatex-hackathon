import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useQuestionnaireStore } from './questionnaireStore'
import type { Block, BlockId, Question } from '@/types'

// ── Mock the API client (Agent G) ───────────────────────────────
vi.mock('@/api/blocks', () => ({
  listBlocks: vi.fn(),
  getBlockQuestions: vi.fn(),
}))

import { listBlocks, getBlockQuestions } from '@/api/blocks'

const mockedListBlocks = vi.mocked(listBlocks)
const mockedGetBlockQuestions = vi.mocked(getBlockQuestions)

const blockPolitica: Block = { id: 'politica', title: 'Política', description: '', weight: 40 }
const blockDiseno: Block = { id: 'diseno', title: 'Diseño', description: '', weight: 36 }
const blockGobernanza: Block = { id: 'gobernanza', title: 'Gobernanza', description: '', weight: 24 }

const qPolitica: Question = {
  id: 'P1', blockId: 'politica', kind: 'scale', order: 1,
  text: '¿Tienes política?', weight: 10, options: [],
}
const qDiseno: Question = {
  id: 'P5', blockId: 'diseno', kind: 'gate', order: 1,
  text: '¿Tienes diseño?', weight: 8, options: [],
}
const qGobernanza: Question = {
  id: 'P10', blockId: 'gobernanza', kind: 'validation', order: 1,
  text: '¿Tienes gobernanza?', weight: 6, options: [],
}

describe('questionnaireStore', () => {
  beforeEach(() => {
    // Reset zustand store state between tests
    useQuestionnaireStore.setState({
      blocks: [],
      questionsByBlock: { politica: [], diseno: [], gobernanza: [] },
      loading: false,
      error: null,
      loaded: false,
    })
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('has empty defaults when_created', () => {
      const s = useQuestionnaireStore.getState()
      expect(s.blocks).toEqual([])
      expect(s.questionsByBlock).toEqual({ politica: [], diseno: [], gobernanza: [] })
      expect(s.loading).toBe(false)
      expect(s.loaded).toBe(false)
      expect(s.error).toBeNull()
    })
  })

  describe('getQuestions', () => {
    it('returns_empty_array_for_unknown_blockId', () => {
      expect(useQuestionnaireStore.getState().getQuestions('politica')).toEqual([])
    })

    it('returns_questions_for_known_blockId_after_fetchAll', async () => {
      mockedListBlocks.mockResolvedValueOnce([blockPolitica])
      mockedGetBlockQuestions.mockResolvedValueOnce([qPolitica])

      await useQuestionnaireStore.getState().fetchAll()
      expect(useQuestionnaireStore.getState().getQuestions('politica')).toEqual([qPolitica])
    })
  })

  describe('fetchAll (success)', () => {
    it('loads_blocks_and_questions_for_every_block', async () => {
      mockedListBlocks.mockResolvedValueOnce([blockPolitica, blockDiseno, blockGobernanza])
      mockedGetBlockQuestions
        .mockResolvedValueOnce([qPolitica])
        .mockResolvedValueOnce([qDiseno])
        .mockResolvedValueOnce([qGobernanza])

      await useQuestionnaireStore.getState().fetchAll()

      const s = useQuestionnaireStore.getState()
      expect(s.loading).toBe(false)
      expect(s.loaded).toBe(true)
      expect(s.error).toBeNull()
      expect(s.blocks).toHaveLength(3)
      expect(s.questionsByBlock.politica).toEqual([qPolitica])
      expect(s.questionsByBlock.diseno).toEqual([qDiseno])
      expect(s.questionsByBlock.gobernanza).toEqual([qGobernanza])
      expect(mockedListBlocks).toHaveBeenCalledTimes(1)
      expect(mockedGetBlockQuestions).toHaveBeenCalledTimes(3)
      expect(mockedGetBlockQuestions).toHaveBeenCalledWith('politica')
      expect(mockedGetBlockQuestions).toHaveBeenCalledWith('diseno')
      expect(mockedGetBlockQuestions).toHaveBeenCalledWith('gobernanza')
    })

    it('works_with_empty_block_list', async () => {
      mockedListBlocks.mockResolvedValueOnce([])
      await useQuestionnaireStore.getState().fetchAll()
      const s = useQuestionnaireStore.getState()
      expect(s.loaded).toBe(true)
      expect(s.blocks).toEqual([])
      expect(mockedGetBlockQuestions).not.toHaveBeenCalled()
    })
  })

  describe('fetchAll (error)', () => {
    it('handles_listBlocks_error_gracefully_without_throwing', async () => {
      mockedListBlocks.mockRejectedValueOnce(new Error('Network down'))
      // Must not throw
      await expect(useQuestionnaireStore.getState().fetchAll()).resolves.toBeUndefined()

      const s = useQuestionnaireStore.getState()
      expect(s.loading).toBe(false)
      expect(s.loaded).toBe(false)
      expect(s.error).toBe('Network down')
    })

    it('uses_default_message_when_error_has_no_message', async () => {
      mockedListBlocks.mockRejectedValueOnce({})
      await useQuestionnaireStore.getState().fetchAll()
      const s = useQuestionnaireStore.getState()
      expect(s.error).toBe('Error loading questionnaire')
      expect(s.loading).toBe(false)
    })

    it('handles_getBlockQuestions_error_gracefully', async () => {
      mockedListBlocks.mockResolvedValueOnce([blockPolitica])
      mockedGetBlockQuestions.mockRejectedValueOnce(new Error('Questions boom'))
      await useQuestionnaireStore.getState().fetchAll()
      const s = useQuestionnaireStore.getState()
      expect(s.loading).toBe(false)
      expect(s.error).toBe('Questions boom')
      expect(s.loaded).toBe(false)
    })
  })
})