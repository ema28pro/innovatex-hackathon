import apiClient from './client'
import type { Company, CompanyCreate } from '@/types'

/** Map backend snake_case to frontend camelCase + field rename. */
function toCompany(raw: Record<string, any>): Company {
  return {
    id: raw.id,
    companyName: raw.name,
    nit: raw.nit,
    sector: raw.sector,
    size: raw.size,
    contactEmail: raw.contact_email ?? undefined,
    createdAt: raw.created_at,
  }
}

/** GET /api/companies — list companies for authenticated user. */
export async function listCompanies(): Promise<Company[]> {
  const { data } = await apiClient.get('/companies/')
  return (data ?? []).map(toCompany)
}

/** POST /api/companies — create company + auto-assign caller as admin. */
export async function createCompany(payload: CompanyCreate): Promise<Company> {
  const { data } = await apiClient.post('/companies/', payload)
  return toCompany(data)
}

/** GET /api/companies/:id — single company detail. */
export async function getCompany(id: string): Promise<Company> {
  const { data } = await apiClient.get(`/companies/${id}`)
  return toCompany(data)
}
