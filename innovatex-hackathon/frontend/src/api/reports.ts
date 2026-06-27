import apiClient from './client'

export interface ShareLinkInfo {
  id: string
  assessmentId: string
  token: string
  expiresAt: string
  status: 'active' | 'revoked' | 'expired'
  viewCount: number
  createdAt: string
  url: string
}

export interface SharedReportData {
  companyName: string
  assessmentStatus: string
  completedAt: string | null
  scores: {
    overallPercentage: number
    maturityLevel: string
    maturityLabel: string
    blocks: Array<{
      blockSlug: string
      blockTitle: string
      score: number
      maxScore: number
      percentage: number
    }>
  }
  actionItems: Array<{
    id: string
    title: string
    status: string
    notes: string | null
  }>
  expiresAt: string
  viewCount: number
}

/** Download the PDF for an assessment. Returns a Blob. */
export async function downloadPdf(assessmentId: string): Promise<Blob> {
  const response = await apiClient.get(`/assessments/${assessmentId}/export/pdf`, {
    responseType: 'blob',
  })
  return response.data as Blob
}

/** Download the Excel file for an assessment. Returns a Blob. */
export async function downloadExcel(assessmentId: string): Promise<Blob> {
  const response = await apiClient.get(`/assessments/${assessmentId}/export/excel`, {
    responseType: 'blob',
  })
  return response.data as Blob
}

/** Create or refresh a shareable link for an assessment. */
export async function createShareLink(
  assessmentId: string,
  expiresInHours: number = 168,
): Promise<ShareLinkInfo> {
  const { data } = await apiClient.post(`/assessments/${assessmentId}/share`, {
    expires_in_hours: expiresInHours,
  })
  return {
    id: data.id,
    assessmentId: data.assessment_id,
    token: data.token,
    expiresAt: data.expires_at,
    status: data.status,
    viewCount: data.view_count,
    createdAt: data.created_at,
    url: data.url,
  }
}

/** View a shared report (public endpoint, no auth). */
export async function getSharedReport(token: string): Promise<SharedReportData> {
  const { data } = await apiClient.get(`/share/${token}`)
  return {
    companyName: data.company_name,
    assessmentStatus: data.assessment_status,
    completedAt: data.completed_at,
    scores: {
      overallPercentage: data.scores.overall_percentage,
      maturityLevel: data.scores.maturity_level,
      maturityLabel: data.scores.maturity_label,
      blocks: (data.scores.blocks || []).map((b: any) => ({
        blockSlug: b.block_slug,
        blockTitle: b.block_title,
        score: b.score,
        maxScore: b.max_score,
        percentage: b.percentage,
      })),
    },
    actionItems: (data.action_items || []).map((ai: any) => ({
      id: ai.id,
      title: ai.title,
      status: ai.status,
      notes: ai.notes,
    })),
    expiresAt: data.expires_at,
    viewCount: data.view_count,
  }
}
