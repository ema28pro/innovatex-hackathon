import apiClient from './client'
import type { Block, Question } from '@/types'

// Map API snake_case to frontend camelCase
function toBlock(raw: any): Block {
  return {
    id: raw.slug,           // Block.slug -> Block.id
    title: raw.title,
    description: raw.description,
    weight: raw.weight,
  }
}

function toQuestion(raw: any): Question {
  return {
    id: raw.slug,           // Question.slug -> Question.id
    blockId: raw.block_id,
    kind: raw.kind,
    order: raw.order_num,
    text: raw.text,
    weight: raw.weight,
    gateFor: raw.gate_for,
    options: [],            // API doesn't serve options yet; component uses data/questionnaire for labels
  }
}

export async function listBlocks(): Promise<Block[]> {
  const { data } = await apiClient.get('/blocks')
  return data.map(toBlock)
}

export async function getBlockQuestions(slug: string): Promise<Question[]> {
  const { data } = await apiClient.get(`/blocks/${slug}/questions`)
  return data.map(toQuestion)
}