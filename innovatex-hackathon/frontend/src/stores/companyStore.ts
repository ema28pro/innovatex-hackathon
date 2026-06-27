import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Company, Sector, CompanySize } from '@/types'
import * as companiesApi from '@/api/companies'

interface CompanyState {
  companies: Company[]
  currentCompanyId: string | null
  loading: boolean
  loaded: boolean
  error: string | null

  loadCompanies: () => Promise<void>
  createCompany: (data: {
    companyName: string; nit: string; sector: Sector; size: CompanySize
  }) => Promise<Company>
  clearCompany: () => void
}

export const useCompanyStore = create<CompanyState>()(
  persist(
    (set, get) => ({
      companies: [],
      currentCompanyId: null,
      loading: false,
      loaded: false,
      error: null,

      loadCompanies: async () => {
        const { loaded, loading } = get()
        if (loaded || loading) return

        set({ loading: true, error: null })
        try {
          const companies = await companiesApi.listCompanies()
          // Auto-select first company if current ID doesn't match (e.g., stale localStorage)
          let cid = get().currentCompanyId
          if (cid && !companies.find((c) => c.id === cid)) {
            cid = companies.length > 0 ? companies[0].id : null
          } else if (!cid && companies.length > 0) {
            cid = companies[0].id
          }
          set({ companies, currentCompanyId: cid, loaded: true, loading: false })
        } catch (err: any) {
          const detail = err?.response?.data?.detail
          let msg = 'Error al cargar empresas'
          if (typeof detail === 'string') msg = detail
          else if (err?.message) msg = err.message
          set({ loaded: true, loading: false, error: msg })
        }
      },

      createCompany: async (formData) => {
        set({ loading: true, error: null })
        try {
          const company = await companiesApi.createCompany({
            name: formData.companyName,
            nit: formData.nit,
            sector: formData.sector,
            size: formData.size,
          })
          set((s) => ({
            companies: [...s.companies, company],
            currentCompanyId: company.id,
            loading: false,
          }))
          return company
        } catch (err: any) {
          const detail = err?.response?.data?.detail
          let msg = 'Error al crear empresa'
          if (Array.isArray(detail)) {
            // Pydantic validation errors: [{loc, msg, type}, ...]
            msg = detail.map((d: any) => d.msg).join('. ')
          } else if (typeof detail === 'string') {
            msg = detail
          } else if (err?.message) {
            msg = err.message
          }
          set({ loading: false, error: msg })
          throw new Error(msg)
        }
      },

      clearCompany: () => set({ currentCompanyId: null, companies: [], loaded: false }),
    }),
    {
      name: 'diagnostico:company',
      partialize: (state) => ({ currentCompanyId: state.currentCompanyId }),
    }
  )
)
