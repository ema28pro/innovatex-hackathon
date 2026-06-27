import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
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

export default function OnboardingPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const createCompany = useCompanyStore((s) => s.createCompany)

  const [values, setValues] = useState<FormValues>({
    companyName: '',
    nit: '',
    sector: '',
    size: '',
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const [apiError, setApiError] = useState<string | null>(null)

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

    if (!user) return

    setLoading(true)
    setApiError(null)
    try {
      await createCompany({
        companyName: values.companyName.trim(),
        nit: values.nit.trim(),
        sector: values.sector as Sector,
        size: values.size as CompanySize,
      })
      setSuccess(true)
    } catch (err: any) {
      setApiError(err?.message ?? 'Error al registrar la empresa')
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="auth-card p-8 text-center">
          <div className="mx-auto w-12 h-12 flex items-center justify-center bg-green-100 rounded-full mb-4">
            <svg
              className="w-6 h-6 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-slate-900 mb-2">
            ¡Empresa registrada!
          </h1>
          <p className="text-sm text-slate-500 mb-6">
            Tu empresa <strong>{values.companyName}</strong> ha sido registrada correctamente.
            Ya puedes comenzar tu diagnóstico de cumplimiento de la Ley 1581.
          </p>
          <button
            onClick={() => navigate('/dashboard', { replace: true })}
            className="btn-primary"
          >
            Ir al dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
      <div className="auth-card p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-slate-900">
            Registra tu empresa
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Completa la información para comenzar con el diagnóstico
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div>
            <label htmlFor="companyName" className="form-label">
              Nombre de la empresa
            </label>
            <input
              id="companyName"
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
            <label htmlFor="nit" className="form-label">
              NIT
            </label>
            <input
              id="nit"
              type="text"
              value={values.nit}
              onChange={(e) => update('nit', e.target.value)}
              className="input-field"
              placeholder="900123456-7"
            />
            {errors.nit && <p className="error-text">{errors.nit}</p>}
          </div>

          <div>
            <label htmlFor="sector" className="form-label">
              Sector
            </label>
            <select
              id="sector"
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
            <label htmlFor="size" className="form-label">
              Tamaño de la empresa
            </label>
            <select
              id="size"
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

          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Registrando empresa...' : 'Registrar empresa'}
          </button>

          {apiError && (
            <p className="text-sm text-red-600 text-center bg-red-50 rounded-md p-2">
              {apiError}
            </p>
          )}
        </form>
      </div>
    </div>
  )
}