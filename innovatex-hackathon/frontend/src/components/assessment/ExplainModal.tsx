import { useState } from 'react'

interface ExplainModalProps {
  open: boolean
  title: string
  content: string
  loading: boolean
  onClose: () => void
}

export default function ExplainModal({
  open,
  title,
  content,
  loading,
  onClose,
}: ExplainModalProps) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-xl shadow-xl border border-slate-200 w-full max-w-lg mx-4 max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h3 className="text-base font-semibold text-slate-900">{title}</h3>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded-md hover:bg-slate-50"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="w-6 h-6 border-2 border-slate-300 border-t-brand-800 rounded-full animate-spin" />
              <span className="ml-3 text-sm text-slate-500">Consultando IA...</span>
            </div>
          ) : (
            <div className="prose prose-sm max-w-none text-slate-700 whitespace-pre-line">
              {content}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-100 bg-slate-50 rounded-b-xl">
          <p className="text-xs text-slate-400">
            Generado por IA · Verificar con fuentes legales oficiales
          </p>
        </div>
      </div>
    </div>
  )
}
