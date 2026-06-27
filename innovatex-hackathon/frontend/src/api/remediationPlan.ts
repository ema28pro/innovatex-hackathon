import apiClient from './client'
import type { RemediationPlan, WeakQuestion } from '@/types'

export async function generateRemediationPlan(assessmentId: string): Promise<RemediationPlan> {
  const { data } = await apiClient.post(`/assessments/${assessmentId}/remediation-plan`, undefined, {
    timeout: 120000, // 2 min — AI generation can be slow
  })
  return toRemediationPlan(data)
}

export async function listWeakQuestions(assessmentId: string): Promise<WeakQuestion[]> {
  const { data } = await apiClient.get(`/assessments/${assessmentId}/remediation-plan/weak-questions`)
  return (data ?? []).map(toWeakQuestion)
}

function toWeakQuestion(raw: any): WeakQuestion {
  return {
    questionSlug: raw.question_slug,
    questionText: raw.question_text,
    currentAnswer: raw.current_answer,
    blockTitle: raw.block_title,
    kind: raw.kind,
  }
}

function toRemediationPlan(raw: any): RemediationPlan {
  return {
    assessmentId: raw.assessment_id,
    overallScore: raw.overall_score,
    maturityLevel: raw.maturity_level,
    maturityLabel: raw.maturity_label,
    weakQuestions: (raw.weak_questions ?? []).map(toWeakQuestion),
    planItems: (raw.plan_items ?? []).map((item: any) => ({
      questionSlug: item.question_slug,
      questionText: item.question_text,
      currentAnswer: item.current_answer,
      title: item.title,
      description: item.description,
      priority: item.priority,
      steps: item.steps ?? [],
    })),
    generatedAt: raw.generated_at,
    error: raw.error,
  }
}
