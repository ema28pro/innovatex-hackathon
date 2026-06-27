interface AssessmentFooterProps {
  onPrev: () => void
  onNext: () => void
  prevDisabled: boolean
  nextDisabled: boolean
  onSubmit: () => void
  submitDisabled: boolean
}

export default function AssessmentFooter({
  onPrev,
  onNext,
  prevDisabled,
  nextDisabled,
  onSubmit,
  submitDisabled,
}: AssessmentFooterProps) {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 flex items-center justify-between gap-4">
      <button
        type="button"
        onClick={onPrev}
        disabled={prevDisabled}
        className="px-4 py-2 text-sm font-medium text-slate-700 border border-slate-200 rounded-md hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        ← Anterior
      </button>

      <button
        type="button"
        onClick={onSubmit}
        disabled={submitDisabled}
        className="btn-primary !w-auto flex-1 max-w-xs"
      >
        Finalizar diagnóstico
      </button>

      <button
        type="button"
        onClick={onNext}
        disabled={nextDisabled}
        className="px-4 py-2 text-sm font-medium text-slate-700 border border-slate-200 rounded-md hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Siguiente →
      </button>
    </div>
  )
}