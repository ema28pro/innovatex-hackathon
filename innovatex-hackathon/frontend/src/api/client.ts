import axios from 'axios'
import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/stores/authStore'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor: attach Supabase JWT from authStore (avoids getSession timing issues)
apiClient.interceptors.request.use(
  (config) => {
    const session = useAuthStore.getState().session
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor: handle 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try getting a fresh session once before giving up
      const { data } = await supabase.auth.getSession()
      const newSession = data.session
      if (newSession?.access_token && error.config && !error.config._retry) {
        error.config._retry = true
        error.config.headers.Authorization = `Bearer ${newSession.access_token}`
        useAuthStore.getState().setSession(newSession)
        return apiClient(error.config)
      }
      // If refresh fails, sign out and redirect
      await supabase.auth.signOut()
      useAuthStore.getState().signOut()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
