import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from '@/stores/authStore'
import ProtectedRoute from '@/components/ProtectedRoute'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import OnboardingPage from '@/pages/OnboardingPage'
import DashboardPage from '@/pages/DashboardPage'
import AssessmentPage from '@/pages/AssessmentPage'

function App() {
  const init = useAuthStore((state) => state.init)
  useEffect(() => { init() }, [init])

  return (
    <div className="min-h-screen bg-slate-50">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/assessment/:id" element={<AssessmentPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </div>
  )
}

export default App