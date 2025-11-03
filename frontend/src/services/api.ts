import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@store/authStore'
import toast from 'react-hot-toast'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Helper function to get CSRF token from cookies
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null
  return null
}

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
  withCredentials: true, // Send cookies with requests (for CSRF)
})

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { tokens } = useAuthStore.getState()
    
    // Add JWT token if available
    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`
    }
    
    // Add CSRF token for non-GET requests
    if (config.method && !['get', 'head', 'options'].includes(config.method.toLowerCase())) {
      const csrfToken = getCookie('csrftoken')
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken
      }
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    
    // Check if we should skip error toast
    const skipErrorToast = originalRequest?.headers?.['X-Skip-Error-Toast'] === 'true'

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const { tokens, clearAuth } = useAuthStore.getState()

      if (tokens?.refresh) {
        try {
          // Try to refresh token
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: tokens.refresh,
          })

          const newTokens = response.data.tokens
          useAuthStore.getState().setAuth(
            useAuthStore.getState().user!,
            newTokens
          )

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${newTokens.access}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, logout user
          clearAuth()
          window.location.href = '/login'
          if (!skipErrorToast) {
            toast.error('Session expired. Please login again.')
          }
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, logout
        clearAuth()
        window.location.href = '/login'
        if (!skipErrorToast) {
          toast.error('Please login to continue.')
        }
      }
    }

    // Handle other errors (but don't show toast for validation errors - let component handle it)
    if (!skipErrorToast) {
      if (error.response?.status === 403) {
        toast.error('You do not have permission to perform this action.')
      } else if (error.response?.status === 404) {
        toast.error('Resource not found.')
      } else if (error.response?.status === 500) {
        toast.error('Server error. Please try again later.')
      } else if (error.code === 'ECONNABORTED') {
        toast.error('Request timeout. Please check your connection.')
      } else if (!error.response && error.code !== 'ERR_CANCELED') {
        // Only show network error if it's not a canceled request
        console.error('Network error:', error)
        toast.error('Network error. Please check your connection.')
      }
    }

    return Promise.reject(error)
  }
)

export default api
