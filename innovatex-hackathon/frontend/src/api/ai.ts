import apiClient from './client'

interface AIExplainResponse {
  result: string
}

interface AISuggestResponse {
  result: string
}

export async function explainQuestion(
  questionText: string,
  legalReference: string,
  companyContext: string,
): Promise<string> {
  const { data } = await apiClient.post<AIExplainResponse>('/ai/explain', {
    question_text: questionText,
    legal_reference: legalReference,
    company_context: companyContext,
  })
  return data.result
}

export async function suggestAnswer(
  questionText: string,
  legalReference: string,
  priorAnswers: string,
  companyContext: string,
): Promise<string> {
  const { data } = await apiClient.post<AISuggestResponse>('/ai/suggest', {
    question_text: questionText,
    legal_reference: legalReference,
    prior_answers: priorAnswers,
    company_context: companyContext,
  })
  return data.result
}
