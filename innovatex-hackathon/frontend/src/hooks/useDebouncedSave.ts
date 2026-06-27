import { useRef, useEffect, useCallback } from 'react'
import type { AnswerEntry } from '@/types'

export function useDebouncedSave(
  persist: (questionId: string, entry: AnswerEntry) => Promise<void>,
  delayMs = 500,
) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const pendingRef = useRef<[string, AnswerEntry] | null>(null)

  const schedule = useCallback((questionId: string, entry: AnswerEntry) => {
    pendingRef.current = [questionId, entry]
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(async () => {
      const pending = pendingRef.current
      if (pending) {
        try { await persist(pending[0], pending[1]) } catch {}
        pendingRef.current = null
      }
    }, delayMs)
  }, [persist, delayMs])

  const flush = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    const pending = pendingRef.current
    if (pending) {
      pendingRef.current = null
      persist(pending[0], pending[1]).catch(() => {})
    }
  }, [persist])

  const cancel = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current)
    pendingRef.current = null
  }, [])

  useEffect(() => {
    return () => { if (timerRef.current) clearTimeout(timerRef.current) }
  }, [])

  return { schedule, flush, cancel }
}