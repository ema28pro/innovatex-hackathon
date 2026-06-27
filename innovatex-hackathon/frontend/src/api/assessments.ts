import apiClient from './client'
import type { Assessment, AnswerEntry } from '@/types'

function toAnswerEntry(raw: any): AnswerEntry {
  const kind = raw.kind
  return {
    questionId: raw.question_id,
    kind,
    scale: kind === 'scale' ? raw.scale_resp as (0|35|70|100) : undefined,
    gate: kind === 'gate' ? (raw.gate_resp ? 'si' : 'no') : undefined,
    validation: kind === 'validation' ? (raw.validation_resp ? 'si' : 'no') : undefined,
    forced: false,  // re-derived client-side from P1 on load
    updatedAt: raw.answered_at,
  }
}

function toAssessment(raw: any): Assessment {
  const answers: Record<string, AnswerEntry> = {}
  for (const a of raw.answers || []) {
    answers[a.question_id] = toAnswerEntry(a)
  }
  return {
    id: raw.id,
    companyId: raw.company_id,
    userId: raw.created_by,  // maps created_by -> userId (frontend type uses userId)
    status: raw.status,
    answers,
    result: null,
    createdAt: raw.created_at,
    completedAt: raw.completed_at,
  } as Assessment
}

function toUpsertBody(entry: AnswerEntry): any {
  const base: any = { question_id: entry.questionId, kind: entry.kind }
  if (entry.kind === 'gate') base.gate_resp = entry.gate === 'si'
  if (entry.kind === 'scale') base.scale_resp = entry.scale
  if (entry.kind === 'validation') base.validation_resp = entry.validation === 'si'
  if (entry.notes) base.notes = entry.notes
  return base
}

export async function startAssessment(companyId: string): Promise<Assessment> {
  const { data } = await apiClient.post('/assessments', { company_id: companyId })
  return toAssessment(data)
}

export async function getAssessment(id: string): Promise<Assessment> {
  const { data } = await apiClient.get(`/assessments/${id}`)
  return toAssessment(data)
}

export async function upsertAnswer(assessmentId: string, entry: AnswerEntry): Promise<any> {
  const { data } = await apiClient.post(`/assessments/${assessmentId}/answers`, toUpsertBody(entry))
  return toAnswerEntry(data)
}

export async function updateAssessment(id: string, status: 'draft' | 'completed'): Promise<Assessment> {
  const { data } = await apiClient.put(`/assessments/${id}`, { status })
  return toAssessment(data)
}