import { create } from 'zustand'
import { supabase } from '@/lib/supabase'
import type { Session, User } from '@supabase/supabase-js'

interface AuthState {
  session: Session | null
  user: User | null
  loading: boolean
  initialized: boolean
  error: string | null

  init: () => Promise<void>
  setSession: (session: Session | null) => void
  signOut: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set, get) => ({
  session: null,
  user: null,
  loading: true,
  initialized: false,
  error: null,

  init: async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      set({ session, user: session?.user ?? null, loading: false, initialized: true })

      // Listen for auth state changes (login, logout, token refresh)
      supabase.auth.onAuthStateChange((_event, session) => {
        set({ session, user: session?.user ?? null })
      })
    } catch (err) {
      set({ loading: false, initialized: true })
    }
  },

  setSession: (session: Session | null) => {
    set({ session, user: session?.user ?? null })
  },

  signOut: async () => {
    try {
      await supabase.auth.signOut()
      set({ session: null, user: null })
    } catch (err: any) {
      set({ error: err?.message || 'Error al cerrar sesión' })
    }
  },

  clearError: () => set({ error: null }),
}))
