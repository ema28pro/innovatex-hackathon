// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useDebouncedSave } from './useDebouncedSave'
import type { AnswerEntry } from '@/types'

const entry = (id: string): AnswerEntry => ({
  questionId: id,
  kind: 'scale',
  scale: 70,
  updatedAt: '2026-06-26T00:00:00.000Z',
})

describe('useDebouncedSave', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('does_not_persist_before_delay_when_scheduled', () => {
    const persist = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() => useDebouncedSave(persist, 500))

    act(() => result.current.schedule('P1', entry('P1')))

    // Before the delay elapses nothing should have been persisted.
    vi.advanceTimersByTime(499)
    expect(persist).not.toHaveBeenCalled()
  })

  it('persists_latest_entry_after_delay_when_scheduled', () => {
    const persist = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() => useDebouncedSave(persist, 500))

    act(() => result.current.schedule('P1', entry('P1')))

    vi.advanceTimersByTime(500)
    expect(persist).toHaveBeenCalledTimes(1)
    expect(persist).toHaveBeenCalledWith('P1', expect.objectContaining({ questionId: 'P1' }))
  })

  it('debounces_rapid_updates_to_only_persist_latest_entry', () => {
    const persist = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() => useDebouncedSave(persist, 500))

    // Three rapid schedules within the debounce window.
    act(() => result.current.schedule('P1', entry('P1')))
    act(() => result.current.schedule('P1', entry('P1')))
    act(() => result.current.schedule('P1', entry('P1')))

    vi.advanceTimersByTime(500)
    expect(persist).toHaveBeenCalledTimes(1)
    expect(persist).toHaveBeenCalledWith('P1', expect.any(Object))
  })

  it('flush_persists_pending_entry_immediately_and_cancels_timer', () => {
    const persist = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() => useDebouncedSave(persist, 500))

    act(() => result.current.schedule('P1', entry('P1')))
    act(() => result.current.flush())

    expect(persist).toHaveBeenCalledTimes(1)
    expect(persist).toHaveBeenCalledWith('P1', expect.any(Object))

    // Advancing time must not trigger a second persist (timer was cleared).
    vi.advanceTimersByTime(1000)
    expect(persist).toHaveBeenCalledTimes(1)
  })

  it('flush_is_noop_when_nothing_pending', () => {
    const persist = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() => useDebouncedSave(persist, 500))

    act(() => result.current.flush())
    expect(persist).not.toHaveBeenCalled()
  })

  it('cancel_prevents_pending_persist', () => {
    const persist = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() => useDebouncedSave(persist, 500))

    act(() => result.current.schedule('P1', entry('P1')))
    act(() => result.current.cancel())

    vi.advanceTimersByTime(1000)
    expect(persist).not.toHaveBeenCalled()
  })

  it('persists_only_latest_when_flush_called_after_rapid_updates', () => {
    const persist = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() => useDebouncedSave(persist, 500))

    act(() => result.current.schedule('P1', entry('P1')))
    act(() => result.current.schedule('P2', entry('P2')))
    act(() => result.current.flush())

    expect(persist).toHaveBeenCalledTimes(1)
    expect(persist).toHaveBeenCalledWith('P2', expect.objectContaining({ questionId: 'P2' }))
  })

  it('swallows_persist_errors_without_throwing_in_timer_callback', () => {
    const persist = vi.fn().mockRejectedValue(new Error('boom'))
    const { result } = renderHook(() => useDebouncedSave(persist, 500))

    act(() => result.current.schedule('P1', entry('P1')))
    // Should not throw when the timer fires and persist rejects.
    act(() => vi.runOnlyPendingTimers())
    expect(persist).toHaveBeenCalledTimes(1)
  })

  it('cleans_up_pending_timer_on_unmount', () => {
    const persist = vi.fn().mockResolvedValue(undefined)
    const { result, unmount } = renderHook(() => useDebouncedSave(persist, 500))

    act(() => result.current.schedule('P1', entry('P1')))
    unmount()

    // After unmount, timers should not fire any persist.
    vi.advanceTimersByTime(1000)
    expect(persist).not.toHaveBeenCalled()
  })

  it('uses_default_delay_of_500ms_when_not_specified', () => {
    const persist = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() => useDebouncedSave(persist))

    act(() => result.current.schedule('P1', entry('P1')))
    vi.advanceTimersByTime(499)
    expect(persist).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1)
    expect(persist).toHaveBeenCalledTimes(1)
  })
})