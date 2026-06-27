import { useState, FormEvent } from 'react'
import { useCompanyStore } from '@/stores/companyStore'
import type { Sector, CompanySize } from '@/types'

const SECTOR_OPTIONS: { value: Sector; label: string }[] = [
  { value: 'tecnologia', label: 'Tecnología' },
  { value: 'salud', label: 'Salud' },
  { value: 'finanzas', label: 'Finanzas' },
  { value: 'comercio', label: 'Comercio' },
  { value: 'manufactura', label: 'Manufactura' },
  { value: 'educacion', label: 'Educación' },
  { value: 'gobierno', label: 'Gobierno' },
  { value: 'otro', label: 'Otro' },
]

const SIZE_OPTIONS: { value: CompanySize; label: string }[] = [
  { value: 'micro', label: 'Micro (1-10)' },
  { value: 'pequena', label: 'Pequeña (11-50)' },
  { value: 'mediana', label: 'Mediana (51-200)' },
  { value: 'grande', label: 'Grande (200+)' },
]

interface FormValues {
  companyName: string
  nit: string
  sector: Sector | ''
  size: CompanySize | ''
}

interface FormErrors {
  companyName?: string
  nit?: string
  sector?: string
  size?: string
}

interface Props {
  open: boolean
  onClose: () => void
}

export default function CreateCompanyModal({ open, onClose }: Props) {
  const createCompany = useCompanyStore((s) => s.createCompany)

  const [values, setValues] = useState<FormValues>({
    companyName: '',
    nit: '',
    sector: '',
    size: '',
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [apiError, setApiError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const update = (field: keyof FormValues, value: string) => {
    setValues((v) => ({ ...v, [field]: value }))
    setErrors((e) => ({ ...e, [field]: undefined }))
    setApiError(null)
  }

  const validate = (): FormErrors => {
    const next: FormErrors = {}
    if (!values.companyName.trim()) next.companyName = 'El nombre de la empresa es obligatorio'
    if (!values.nit.trim()) next.nit = 'El NIT es obligatorio'
    if (!values.sector) next.sector = 'Selecciona un sector'
    if (!values.size) next.size = 'Selecciona un tamaño de empresa'
    return next
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const nextErrors = validate()
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    setLoading(true)
    setApiError(null)
    try {
      await createCompany({
        companyName: values.companyName.trim(),
        nit: values.nit.trim(),
        sector: values.sector as Sector,
        size: values.size as CompanySize,
      })
      setValues({ companyName: '', nit: '', sector: '', size: '' })
      onClose()
    } catch (err: any) {
      setApiError(err?.message ?? 'Error al registrar la empresa')
    } finally {
      setLoading(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md mx-4 bg-white rounded-lg border border-slate-200 shadow-xl p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Registrar nueva empresa
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Completa los datos para crear una nueva empresa
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 transition-colors rounded-full hover:bg-slate-100"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div>
            <label htmlFor="modal-companyName" className="form-label">
              Nombre de la empresa
            </label>
            <input
              id="modal-companyName"
              type="text"
              value={values.companyName}
              onChange={(e) => update('companyName', e.target.value)}
              className="input-field"
              placeholder="Mi Empresa S.A.S."
              autoFocus
            />
            {errors.companyName && <p className="error-text">{errors.companyName}</p>}
          </div>

          <div>
            <label htmlFor="modal-nit" className="form-label">
              NIT
            </label>
            <input
              id="modal-nit"
              type="text"
              value={values.nit}
              onChange={(e) => update('nit', e.target.value)}
              className="input-field"
              placeholder="900123456-7"
            />
            {errors.nit && <p className="error-text">{errors.nit}</p>}
          </div>

          <div>
            <label htmlFor="modal-sector" className="form-label">
              Sector
            </label>
            <select
              id="modal-sector"
              value={values.sector}
              onChange={(e) => update('sector', e.target.value)}
              className="input-field"
            >
              <option value="" disabled>
                Selecciona un sector
              </option>
              {SECTOR_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            {errors.sector && <p className="error-text">{errors.sector}</p>}
          </div>

          <div>
            <label htmlFor="modal-size" className="form-label">
              Tamaño de la empresa
            </label>
            <select
              id="modal-size"
              value={values.size}
              onChange={(e) => update('size', e.target.value)}
              className="input-field"
            >
              <option value="" disabled>
                Selecciona un tamaño
              </option>
              {SIZE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            {errors.size && <p className="error-text">{errors.size}</p>}
          </div>

          {apiError && (
            <p className="text-sm text-red-600 text-center bg-red-50 rounded-md p-2">
              {apiError}
            </p>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 border border-slate-300 text-slate-700 rounded-md text-sm font-medium hover:bg-slate-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2.5 bg-brand-800 text-white rounded-md text-sm font-medium hover:bg-brand-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Registrando...' : 'Registrar empresa'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
